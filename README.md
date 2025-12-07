# 🚀 Momentum Tracker

A powerful desktop application for tracking your daily activities and productivity with visual dashboards, calendar views, and detailed analytics.

## 📘 Overview

**Momentum Tracker** is a Python desktop application built with Tkinter that helps you track how you spend your time. It automatically prompts you at regular intervals (default: every 15 minutes) to log your activities, then provides insightful visualizations and reports.

### Key Features

- ⏰ **Automatic Tracking**: Popup reminders at configurable intervals
- 📊 **Visual Dashboards**: Pie charts and statistics for daily activity
- 📅 **Calendar View**: Browse and filter activities by date
- ⚙️ **Customizable**: Manage categories, adjust intervals, configure settings
- 💾 **SQLite Database**: Robust data storage with migration from Excel
- 📈 **Analytics**: Daily, weekly, and monthly summaries
- 🎨 **Modern UI**: Clean, intuitive interface

## 🖥️ How It Works

1. The application runs in the background
2. At configured intervals (default: every 15 minutes), a popup appears asking "What did you just do?"
3. You can quickly select a category, add details, or skip
4. Activities are saved to a SQLite database
5. View your progress in the Dashboard, Today's list, or Calendar view

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

### First Run

- If you have existing Excel files in the `reports/` directory, the app will prompt to import them automatically
- The database and configuration files will be created automatically in the `data/` directory

## 📂 Project Structure

```
momentum-tracker/
├── app.py                 # Main entry point
├── ui/                    # User interface components
│   ├── main_window.py     # Main dashboard
│   ├── calendar_view.py   # Calendar widget
│   └── settings_window.py # Settings management
├── controllers/           # Business logic
│   ├── activity_controller.py
│   ├── analytics_controller.py
│   └── popup_controller.py
├── data/                  # Data layer
│   ├── database.py        # SQLite database
│   └── migrations.py      # Excel migration
├── utils/                 # Utilities
│   ├── config.py          # Configuration
│   └── logger.py          # Logging
└── reports/               # Legacy Excel files (optional)
```

## 🎯 Features in Detail

### Dashboard
- Real-time activity statistics
- Visual pie chart of daily activity distribution
- Total time tracked and entry count

### Calendar View
- Interactive monthly calendar
- Click any date to view activities
- Timeline of activities for selected date
- Navigate between months

### Settings
- **Categories**: Add, edit, or delete activity categories
- **Timer**: Adjust tracking interval (5-60 minutes)
- **Notifications**: Enable/disable popups and sounds
- **Appearance**: Light/dark theme selection

### Improved Popup
- Quick action buttons ("Same as last", "Didn't track")
- Category selection with radio buttons
- Optional description field
- Keyboard shortcuts (Enter to submit, Escape to cancel)

## 📊 Data Storage

### SQLite Database
- Location: `data/momentum_tracker.db`
- Tables: users, categories, activity_logs, aggregations
- Thread-safe operations
- Automatic backups recommended

### Configuration
- Location: `data/config.json`
- Stores user preferences and settings
- Can be edited manually or through UI

### Logs
- Location: `data/logs/`
- Daily log files with timestamps
- Error tracking and debugging

## 🔄 Migration from Excel

If you have existing Excel files:

1. Place them in the `reports/` directory (format: `YYYY-MM-DD_report.xlsx`)
2. Run the application
3. When prompted, choose to import existing data
4. All entries will be migrated to SQLite

See [MIGRATION.md](MIGRATION.md) for detailed migration instructions.

## ⚙️ Configuration

Default settings can be modified in `data/config.json`:

```json
{
  "app_name": "Momentum Tracker",
  "interval_minutes": 15,
  "popup_enabled": true,
  "sound_enabled": false,
  "theme": "light",
  "categories": ["Working", "Chilling", "Gaming", "Academics", "Business"]
}
```

Or use the Settings UI for easy configuration.

## 🛠️ Development

### Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

### Key Design Decisions
- **Modular Structure**: Clear separation of UI, business logic, and data layers
- **Thread Safety**: Safe concurrent database operations
- **Extensibility**: Ready for future features (multi-user, cloud sync, mobile app)
- **Backward Compatibility**: Automatic migration from Excel format

## 📝 Requirements

- Python 3.7+
- tkinter (usually included with Python)
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- matplotlib >= 3.5.0

## 🐛 Troubleshooting

### Database locked errors
- Ensure only one instance is running
- Check file permissions on `data/momentum_tracker.db`

### Import errors
- Verify Excel files are in correct format
- Check logs in `data/logs/` for details

### Missing dependencies
```bash
pip install pandas openpyxl matplotlib
```

## 🚀 Future Improvements

- [ ] Weekly and monthly trend charts
- [ ] Export to Excel/CSV/JSON
- [ ] Goal setting and progress tracking
- [ ] Mobile app with cloud sync
- [ ] Desktop notifications
- [ ] Activity templates
- [ ] Time blocking features

## 📄 License

This project is open source and available for personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Happy Tracking!** 📊✨
