---

## 🧠 README for “Vibe Productivity Tracker”

### 📘 Overview

**Vibe Productivity Tracker** is a simple Python desktop widget built using **Tkinter**.
Every 15 minutes (at 00, 15, 30, and 45 past each hour), it asks you:

> “What have you been doing for the past 15 minutes?”

You can then select a category such as:

* 💼 **Working**
* 📚 **Academics**
* 🎮 **Gaming**
* 😌 **Chilling**
* 💡 **Business**

…and write a short note describing what you were doing.

At the end of the day, the app generates a **daily report** showing:

* Time spent on each category (as a percentage)
* A log of all entries
* A progress comparison (how much more productive you were compared to yesterday)

---

### 🖥️ How it Works

1. The widget runs silently in the background.
2. At **every 15-minute mark** (00, 15, 30, 45), a popup appears with category buttons and a text field.
3. After you log your activity, the entry is saved to a file.
4. At midnight, an **Excel report** is created in the `reports/` folder.

---

### 📂 Data Storage

Each log entry is saved automatically to a `.csv` file under the folder:

```
/reports/YYYY-MM-DD_report.xlsx
```

Each row contains:

| Time  | Category | Description              | Date       |
| ----- | -------- | ------------------------ | ---------- |
| 12:00 | Working  | Wrote code for the rover | 2025-10-31 |

---

### 📊 Daily Reports

At the end of each day (or when you restart the app the next day), the widget generates an Excel report summarizing your productivity.
You can open it directly in Excel or Google Sheets to view your progress.

---

### 🚀 Future Improvements

* Add a weekly summary report
* Add graphs for daily category distribution
* Add a “%1 better” progress tracker comparing yesterday vs today
* Sync with a mobile app

