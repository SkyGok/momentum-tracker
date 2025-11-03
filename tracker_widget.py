import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from datetime import datetime
import threading
import time
import sys
import traceback

# --- CONFIG ---
BASE_DIR = os.path.expanduser("/home/gokhan/Side-Projects/momentum-tracker")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
LOG_FILE = os.path.join(BASE_DIR, "tracker.log")

os.makedirs(REPORT_DIR, exist_ok=True)

# Redirect stdout/stderr to log file for debugging
sys.stdout = open(LOG_FILE, "a")
sys.stderr = sys.stdout

def log(msg):
    """Log messages with timestamps."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
    sys.stdout.flush()

def log_exception(e):
    """Log exceptions to tracker.log."""
    log(f"ERROR: {e}\n{traceback.format_exc()}")

# Small startup delay (helps if Hyprland launches too early)
time.sleep(3)

data = []
LOCK = threading.Lock()
last_popup_time = None

def get_today_file():
    """Return today's Excel file path."""
    now = datetime.now()
    return os.path.join(REPORT_DIR, f"{now.strftime('%Y-%m-%d')}_report.xlsx")

# --- Load today's data if file exists ---
today_file = get_today_file()
if os.path.exists(today_file):
    try:
        data = pd.read_excel(today_file).to_dict(orient="records")
        log(f"Loaded {len(data)} previous entries from {today_file}")
    except Exception as e:
        log_exception(e)

def save_entry(category, description):
    """Save a new entry to today's Excel report (create if missing)."""
    global data
    now = datetime.now()
    today_file = get_today_file()
    entry = {
        "Time": now.strftime("%H:%M"),
        "Category": category,
        "Description": description,
        "Duration (min)": 15,
        "Date": now.strftime("%Y-%m-%d")
    }
    data.append(entry)

    df = pd.DataFrame(data)
    try:
        df.to_excel(today_file, index=False)
        log(f"Saved {len(data)} entries to {today_file}")
        messagebox.showinfo("Saved!", f"Entry saved under '{category}'.")
    except Exception as e:
        log_exception(e)
        messagebox.showerror("Error", f"Could not save data:\n{e}")

def show_popup():
    """Popup to ask user what they have been doing."""
    popup = tk.Toplevel(root)
    popup.title("Momentum Tracker")
    popup.geometry("350x350")
    popup.configure(bg="#f9f9f9")

    # Center window
    popup.update_idletasks()
    w = popup.winfo_width()
    h = popup.winfo_height()
    ws = popup.winfo_screenwidth()
    hs = popup.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    popup.geometry(f"+{x}+{y}")

    tk.Label(popup, text="What have you been doing for the past 15 mins?",
             font=("Helvetica", 11, "bold"), bg="#f9f9f9").pack(pady=10)

    categories = ["Working", "Chilling", "Gaming", "Academics", "Business"]
    selected_category = tk.StringVar(value=categories[0])

    for cat in categories:
        tk.Radiobutton(popup, text=cat, variable=selected_category,
                       value=cat, bg="#f9f9f9", font=("Helvetica", 10)).pack(anchor="w", padx=50)

    tk.Label(popup, text="Add details:", bg="#f9f9f9").pack(pady=5)
    detail_entry = tk.Entry(popup, width=40)
    detail_entry.pack(pady=5)

    def submit(event=None):
        category = selected_category.get()
        description = detail_entry.get().strip()
        save_entry(category, description)
        popup.destroy()

    submit_btn = tk.Button(popup, text="Submit", command=submit, bg="#4CAF50", fg="white",
                           font=("Helvetica", 10, "bold"), relief="flat", width=15)
    submit_btn.pack(pady=10)

    popup.bind("<Return>", submit)

def check_time():
    """Check every few seconds for 15-minute intervals."""
    global last_popup_time
    while True:
        now = datetime.now()
        minute = now.minute
        if minute % 15 == 0:
            with LOCK:
                if last_popup_time != now.strftime("%H:%M"):
                    last_popup_time = now.strftime("%H:%M")
                    log(f"Triggering popup at {last_popup_time}")
                    root.after(0, show_popup)
            time.sleep(60)
        time.sleep(5)

def show_today_summary():
    """Show today's summary in a popup."""
    today_file = get_today_file()
    if not os.path.exists(today_file):
        messagebox.showinfo("No Data", "No report found for today yet.")
        return

    try:
        df = pd.read_excel(today_file)
        if df.empty:
            messagebox.showinfo("No Data", "No data recorded for today yet.")
            return

        category_counts = df["Category"].value_counts()
        total_entries = category_counts.sum()
        total_time = total_entries * 15
        summary_lines = [f"{cat}: {count * 15} min ({count / total_entries * 100:.1f}%)"
                         for cat, count in category_counts.items()]
        summary_text = "\n".join(summary_lines)
        messagebox.showinfo("Today's Summary",
                            f"Total Time Tracked: {total_time} min\n\n" + summary_text)
    except Exception as e:
        log_exception(e)
        messagebox.showerror("Error", str(e))

# --- UI Setup ---
root = tk.Tk()
root.title("Momentum Tracker")
root.geometry("300x200")
root.configure(bg="#e8f5e9")

tk.Label(root, text="Momentum Tracker", bg="#e8f5e9",
         font=("Helvetica", 13, "bold")).pack(pady=10)

tk.Button(root, text="Log Now", command=show_popup, bg="#2196F3", fg="white",
          font=("Helvetica", 10, "bold"), relief="flat", width=20).pack(pady=10)

tk.Button(root, text="Today's Summary", command=show_today_summary, bg="#4CAF50", fg="white",
          font=("Helvetica", 10, "bold"), relief="flat", width=20).pack(pady=10)

tk.Label(root, text="Auto asks every 15 mins", bg="#e8f5e9",
         font=("Helvetica", 9, "italic")).pack(side="bottom", pady=5)

# --- Background Thread ---
threading.Thread(target=check_time, daemon=True).start()

log("Momentum Tracker started successfully.")
root.mainloop()
