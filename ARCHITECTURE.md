# Architecture Documentation

## Overview

Momentum Tracker follows a modular, class-based architecture with clear separation of concerns.

## Directory Structure

```
momentum-tracker/
├── app.py                    # Main entry point
├── ui/                       # User Interface Layer
│   ├── main_window.py        # Main dashboard window
│   ├── calendar_view.py      # Calendar widget
│   └── settings_window.py    # Settings management
├── controllers/              # Business Logic Layer
│   ├── activity_controller.py    # Activity tracking logic
│   ├── analytics_controller.py   # Analytics and visualization
│   └── popup_controller.py       # Popup dialog management
├── data/                     # Data Layer
│   ├── database.py           # SQLite database manager
│   └── migrations.py         # Excel to SQLite migration
└── utils/                    # Utilities
    ├── config.py             # Configuration management
    └── logger.py             # Logging system
```

## Architecture Layers

### 1. Data Layer (`data/`)

**Database (`database.py`)**
- Thread-safe SQLite database manager
- Handles all database operations
- Provides connection pooling via thread-local storage
- Implements transaction management

**Migrations (`migrations.py`)**
- Excel to SQLite data migration
- Handles various Excel formats
- Preserves data integrity

### 2. Business Logic Layer (`controllers/`)

**ActivityController**
- Manages activity tracking timing
- Handles interval monitoring
- Provides summary statistics
- Thread-safe background monitoring

**AnalyticsController**
- Data aggregation and analysis
- Chart data preparation
- Trend calculations

**PopupController**
- Manages activity logging popups
- Improved UX with quick actions
- Handles user input validation

### 3. UI Layer (`ui/`)

**MainWindow**
- Main application window
- Dashboard with charts
- Tabbed interface
- Real-time data refresh

**CalendarView**
- Interactive calendar widget
- Date selection and filtering
- Activity timeline display

**SettingsWindow**
- Configuration management
- Category CRUD operations
- Timer and appearance settings

### 4. Utilities (`utils/`)

**Config**
- Centralized configuration
- JSON-based storage
- Default value management
- Relative path handling

**Logger**
- Structured logging
- Daily log file rotation
- Console and file output
- Error tracking

## Design Patterns

### MVC-like Architecture
- **Model**: Database layer
- **View**: UI components
- **Controller**: Business logic controllers

### Singleton Pattern
- Database connection per thread
- Configuration instance

### Observer Pattern
- Activity logging callbacks
- Settings change notifications

### Factory Pattern
- Window creation
- Controller initialization

## Thread Safety

- Database operations use locks
- Thread-local database connections
- Safe GUI updates via `root.after()`
- Background monitoring in daemon thread

## Data Flow

1. **User Action** → UI Component
2. **UI Component** → Controller
3. **Controller** → Database
4. **Database** → SQLite
5. **Response** → Controller → UI Update

## Configuration Management

Configuration is stored in `data/config.json`:
- User preferences
- Categories
- Timer settings
- Theme preferences

Defaults are defined in `Config.DEFAULT_CONFIG` and merged with user settings.

## Database Schema

### Tables

1. **users**: Future multi-user support
2. **categories**: Activity categories
3. **activity_logs**: Main activity entries
4. **weekly_aggregations**: Performance optimization
5. **monthly_aggregations**: Performance optimization

### Indexes

- `idx_activity_logs_logged_at`: Fast date queries
- `idx_activity_logs_category`: Fast category filtering

## Error Handling

- Try-except blocks in critical paths
- Logging of all errors
- User-friendly error messages
- Graceful degradation

## Future Extensibility

The architecture supports:
- Multi-user support (users table ready)
- Cloud sync (database abstraction)
- Mobile app (REST API layer can be added)
- Plugin system (controller interfaces)
- Export formats (Excel, CSV, JSON)

## Performance Considerations

- Database indexes for fast queries
- Aggregation tables for weekly/monthly stats
- Lazy loading of UI components
- Efficient chart rendering
- Thread-safe operations

## Security Considerations

- SQL injection prevention (parameterized queries)
- File path validation
- Input sanitization
- Safe file operations

