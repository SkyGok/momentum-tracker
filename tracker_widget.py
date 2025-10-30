import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from datetime import datetime
import threading
import time

# --- Setup ---
data = []
os.makedirs("reports", exist_ok=True)
today_file = f"reports/{datetime.now().strftime('%Y-%m-%d')}_report.xlsx"

# --- Load previous data if exists ---
if os.path.exists(today_file):
    try:
        data = pd.read_excel(today_file).to_dict(orient="records")
        print(f"Loaded {len(data)} previous entries from {today_file}")
    except Exception as e:
        print(f"Error loading file: {e}")

def save_entry(category, description):
    """Save a new entry and append to Excel file."""
    global data
    now = datetime.now()
    entry = {
        "Time": now.strftime("%H:%M"),
        "Category": category,
        "Description": description,
        "Date": now.strftime("%Y-%m-%d")
    }
    data.append(entry)

    df = pd.DataFrame(data)
    df.to_excel(today_file, index=False)
    print(f"Saved {len(data)} total entries to {today_file}")
    messagebox.showinfo("Saved!", f"Entry saved under {category}.")

def show_popup():
    """Popup to ask user what they have been doing."""
    popup = tk.Toplevel(root)
    popup.title("Momentum Tracker")
    popup.geometry("350x350")
    popup.configure(bg="#f0f0f0")

    tk.Label(popup, text="What have you been doing for the past 15 mins?",
             font=("Helvetica", 11, "bold"), bg="#f0f0f0").pack(pady=10)

    categories = ["Working", "Chilling", "Gaming", "Academics", "Business"]
    selected_category = tk.StringVar(value=categories[0])

    for cat in categories:
        tk.Radiobutton(popup, text=cat, variable=selected_category,
                       value=cat, bg="#f0f0f0", font=("Helvetica", 10)).pack(anchor="w", padx=50)

    tk.Label(popup, text="Add details:", bg="#f0f0f0").pack(pady=5)
    detail_entry = tk.Entry(popup, width=40)
    detail_entry.pack(pady=5)

    def submit():
        category = selected_category.get()
        description = detail_entry.get()
        save_entry(category, description)
        popup.destroy()

    tk.Button(popup, text="Submit", command=submit, bg="#4CAF50", fg="white",
              font=("Helvetica", 10, "bold"), relief="flat", width=15).pack(pady=10)

def check_time():
    """Check every minute if it's one of the report times (00, 15, 30, 45)."""
    while True:
        now = datetime.now()
        if now.minute in [0, 15, 30, 45] and now.second == 0:
            root.after(0, show_popup)
            time.sleep(60)
        time.sleep(1)

def show_today_summary():
    """Show today's summary in a popup."""
    if not os.path.exists(today_file):
        messagebox.showinfo("No Data", "No report found for today yet.")
        return

    df = pd.read_excel(today_file)
    if df.empty:
        messagebox.showinfo("No Data", "No data recorded for today yet.")
        return

    category_counts = df["Category"].value_counts(normalize=True) * 100
    summary_text = "\n".join([f"{cat}: {percent:.1f}%" for cat, percent in category_counts.items()])
    messagebox.showinfo("Today's Summary", summary_text)

# --- UI Setup ---
root = tk.Tk()
root.title("Momentum Tracker")
root.geometry("300x200")
root.configure(bg="#e8f5e9")

tk.Label(root, text="Momentum Tracker", bg="#e8f5e9",
         font=("Helvetica", 13, "bold")).pack(pady=10)

tk.Button(root, text="Log Now", command=show_popup, bg="#2196F3", fg="white",
          font=("Helvetica", 10, "bold"), relief="flat", width=20).pack(pady=10)

tk.Button(root, text="Today So Far", command=show_today_summary, bg="#4CAF50", fg="white",
          font=("Helvetica", 10, "bold"), relief="flat", width=20).pack(pady=10)

tk.Label(root, text="Auto asks every 15 mins", bg="#e8f5e9",
         font=("Helvetica", 9, "italic")).pack(side="bottom", pady=5)

# Run time checker in background thread
threading.Thread(target=check_time, daemon=True).start()

root.mainloop()
