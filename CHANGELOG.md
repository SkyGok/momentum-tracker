# Changelog

## Version 2.0.0 - Major Refactor (Current)

### 🎉 Major Changes

#### Architecture
- ✅ Complete refactor to modular, class-based architecture
- ✅ Separated into UI, Controllers, Data, and Utils layers
- ✅ Removed all global variables
- ✅ Implemented proper thread safety

#### Database
- ✅ Migrated from Excel to SQLite database
- ✅ Future-ready schema with users, categories, activity_logs, aggregations
- ✅ Automatic Excel-to-SQLite migration tool
- ✅ Thread-safe database operations

#### UI Improvements
- ✅ Modern dashboard with pie charts (matplotlib)
- ✅ Calendar view for date filtering and timeline
- ✅ Settings window for full customization
- ✅ Improved popup with quick actions ("Same as last", "Didn't track")
- ✅ Tabbed interface (Dashboard, Today, Calendar)

#### Configuration
- ✅ JSON-based configuration system
- ✅ Relative paths (no hardcoded paths)
- ✅ User-configurable categories, intervals, themes
- ✅ Settings persist across sessions

#### Code Quality
- ✅ Proper logging system (replaced stdout redirection)
- ✅ Error handling and validation
- ✅ Type hints and documentation
- ✅ Clean separation of concerns

#### Features Added
- ✅ Daily summary with visual charts
- ✅ Calendar navigation and filtering
- ✅ Category management (add/edit/delete)
- ✅ Customizable tracking interval (5-60 minutes)
- ✅ Theme selection (light/dark)
- ✅ Activity timeline view
- ✅ Real-time dashboard refresh

### 🔧 Technical Improvements

- Thread-safe database operations with locks
- Proper resource cleanup
- Modular imports and dependencies
- Comprehensive error logging
- Data validation on input

### 📝 Documentation

- Updated README with new features
- Architecture documentation (ARCHITECTURE.md)
- Migration guide (MIGRATION.md)
- Code comments and docstrings

### 🐛 Bug Fixes

- Fixed stdout redirection issue
- Fixed race conditions in popup triggering
- Fixed hardcoded path issues
- Fixed thread safety issues
- Prevented duplicate popups

### ⚠️ Breaking Changes

- Old `tracker_widget.py` is now legacy (use `app.py`)
- Excel files are no longer the primary storage (migrated to SQLite)
- Configuration format changed (now JSON instead of hardcoded)

### 📦 Dependencies

- Removed: customtkinter, plyer (unused)
- Updated: pandas, openpyxl, matplotlib
- Added: sqlite3 (built-in)

---

## Version 1.0.0 - Initial Release

- Basic activity tracking with Excel storage
- 15-minute interval popups
- Simple category selection
- Daily Excel reports

