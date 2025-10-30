#!/usr/bin/env python3
"""
Quarter-Hour Tracker (CustomTkinter Version)
Prompts user at 00, 15, 30, 45 minutes each hour.
Logs category + notes, stores in SQLite, shows daily/weekly reports.
"""

import os, sqlite3, json, threading, time
from datetime import datetime, timedelta, date
import customtkinter as ctk
from tkinter import messagebox
from plyer import notification
import matplotlib.pyplot as plt

# -----------------------
# CONFIGURATION
# -----------------------
DB_PATH = os.path.join(os.path.expanduser("~"), ".tracker_widget.db")
CATEGORIES = ["Working", "Chilling", "Gaming", "Academics", "Business"]
NOTIFICATION_TITLE = "Quarter-Hour Tracker"
PRODUCTIVE_CATS = {"Working", "Academics", "Business"}
# -----------------------

# -----------------------
# DATABASE
# -----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            category TEXT,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_entry(category, note):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO entries (timestamp, category, note) VALUES (?, ?, ?)",
              (datetime.utcnow().isoformat(), category, note))
    conn.commit()
    conn.close()

def get_entries_for_date(dt: date):
    start = datetime(dt.year, dt.month, dt.day)
    end = start + timedelta(days=1)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT category FROM entries WHERE timestamp >= ? AND timestamp < ?",
              (start.isoformat(), end.isoformat()))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# -----------------------
# REPORTS
# -----------------------
def generate_daily_report(dt: date = None, show_plot=True):
    dt = dt or date.today()
    rows = get_entries_for_date(dt)
    if not rows:
        messagebox.showinfo("Report", f"No entries for {dt.isoformat()}")
        return
    totals = {cat: rows.count(cat) for cat in CATEGORIES}
    total = sum(totals.values()) or 1
    percentages = {cat: (count/total)*100 for cat, count in totals.items()}

    report_dir = os.path.join(os.path.expanduser("~"), ".tracker_reports")
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, f"{dt.isoformat()}.json")
    json.dump({"date": dt.isoformat(), "data": percentages}, open(path, "w"), indent=2)

    if show_plot:
        plt.figure(figsize=(6,6))
        plt.pie(percentages.values(), labels=percentages.keys(), autopct='%1.1f%%', startangle=140)
        plt.axis("equal")
        plt.title(f"Daily Report {dt.isoformat()}")
        plt.show()

def compare_with_yesterday():
    today = get_entries_for_date(date.today())
    yesterday = get_entries_for_date(date.today() - timedelta(days=1))
    if not today or not yesterday:
        messagebox.showinfo("Compare", "Not enough data for comparison.")
        return
    def productive_score(entries): return sum(1 for e in entries if e in PRODUCTIVE_CATS)
    t, y = productive_score(today), productive_score(yesterday)
    improvement = ((t - y) / y * 100) if y != 0 else 0
    messagebox.showinfo("Daily Comparison",
                        f"Today's productive: {t}\nYesterday: {y}\nChange: {improvement:.1f}%")

# -----------------------
# UTILITIES
# -----------------------
def notify_user():
    try:
        notification.notify(title=NOTIFICATION_TITLE, message="What were you doing last 15 mins?", timeout=5)
    except Exception as e:
        print("Notification failed:", e)

def next_quarter_seconds():
    now = datetime.now()
    minutes = now.minute
    next_quarter = ((minutes // 15) + 1) * 15
    if next_quarter == 60:
        next_quarter = 0
        next_time = now.replace(hour=(now.hour+1)%24, minute=0, second=0, microsecond=0)
    else:
        next_time = now.replace(minute=next_quarter, second=0, microsecond=0)
    return (next_time - now).total_seconds()

# -----------------------
# UI CLASSES
# -----------------------
class Prompt(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Quarter-Hour Tracker")
        self.geometry("400x320")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        ctk.CTkLabel(self, text="What have you been doing?", font=("Arial", 16, "bold")).pack(pady=10)
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        for cat in CATEGORIES:
            ctk.CTkButton(btn_frame, text=cat, command=lambda c=cat: self.save(c)).pack(pady=4, padx=20, fill="x")

        self.note = ctk.CTkTextbox(self, height=80)
        self.note.pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(self, text="Save", command=lambda: self.save("Unspecified"), fg_color="#4CAF50").pack(pady=6)

    def save(self, category):
        note = self.note.get("1.0", "end").strip()
        save_entry(category, note)
        self.destroy()

# -----------------------
# MAIN APP
# -----------------------
class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Quarter-Hour Tracker")
        self.geometry("400x220")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        ctk.CTkLabel(self, text="Quarter-Hour Tracker", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkButton(self, text="Force Prompt", command=self.show_prompt, fg_color="#2196F3").pack(pady=6)
        ctk.CTkButton(self, text="Show Daily Report", command=generate_daily_report).pack(pady=6)
        ctk.CTkButton(self, text="Compare with Yesterday", command=compare_with_yesterday).pack(pady=6)

        self.after(int(next_quarter_seconds()*1000), self.schedule_prompt)

    def show_prompt(self):
        notify_user()
        self.bell()
        Prompt(self)

    def schedule_prompt(self):
        self.show_prompt()
        # schedule again for the next quarter
        self.after(int(next_quarter_seconds()*1000), self.schedule_prompt)

# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    init_db()
    app = TrackerApp()
    app.mainloop()
