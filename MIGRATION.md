# Migration Guide

## Overview

The Momentum Tracker has been refactored from a simple Excel-based system to a robust SQLite-based architecture with improved UI and features.

## Key Changes

### Architecture
- **Before**: Single file with global variables, Excel-based storage
- **After**: Modular class-based architecture with SQLite database

### Data Storage
- **Before**: Excel files in `reports/` directory
- **After**: SQLite database in `data/momentum_tracker.db` with optional Excel export

### Features Added
- ✅ SQLite database with proper schema
- ✅ Dashboard with visual charts
- ✅ Calendar view for date filtering
- ✅ Settings window for customization
- ✅ Improved popup UX with quick actions
- ✅ Proper logging system
- ✅ Thread-safe operations
- ✅ Configuration management

## Migration Process

### Automatic Migration

When you first run the new application (`app.py`), it will:
1. Detect existing Excel files in the `reports/` directory
2. Ask if you want to import them
3. Automatically migrate all data to SQLite

### Manual Migration

If you need to re-run migration or import specific files:

```python
from pathlib import Path
from data.database import Database
from data.migrations import ExcelMigrator
from utils.logger import AppLogger

# Setup
config = Config()
logger = AppLogger(config.data_dir / "logs")
database = Database(config.db_path, logger)

# Migrate
migrator = ExcelMigrator(config.reports_dir, database, logger)
stats = migrator.migrate_all_reports()

print(f"Migrated {stats['entries_migrated']} entries from {stats['files_processed']} files")
```

## Running the Application

### First Time Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. If you have existing Excel files, the app will prompt to import them.

### Directory Structure

```
momentum-tracker/
├── app.py                 # Main entry point
├── data/
│   ├── momentum_tracker.db  # SQLite database (created automatically)
│   ├── config.json          # User configuration (created automatically)
│   └── logs/                # Log files
├── reports/                 # Excel reports (legacy, can be kept for backup)
├── ui/                      # UI components
├── controllers/             # Business logic
├── data/                    # Data layer (database, migrations)
└── utils/                   # Utilities (config, logging)
```

## Configuration

Settings are stored in `data/config.json` and can be modified through the Settings UI or directly in the file.

Default configuration:
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

## Database Schema

The SQLite database includes:

- **users**: For future multi-user support
- **categories**: Activity categories (editable in Settings)
- **activity_logs**: Main activity entries
- **weekly_aggregations**: Pre-computed weekly stats (for performance)
- **monthly_aggregations**: Pre-computed monthly stats (for performance)

## Backward Compatibility

- Old Excel files are preserved in `reports/` directory
- Data is migrated automatically on first run
- You can still export to Excel if needed (future feature)

## Troubleshooting

### Database locked errors
- Ensure only one instance of the app is running
- Check if database file has proper permissions

### Import errors
- Verify Excel files are in correct format
- Check log files in `data/logs/` for details

### Missing dependencies
```bash
pip install pandas openpyxl matplotlib
```

## Next Steps

After migration:
1. Review your data in the Calendar view
2. Customize categories in Settings
3. Adjust tracking interval if needed
4. Explore the Dashboard for insights

