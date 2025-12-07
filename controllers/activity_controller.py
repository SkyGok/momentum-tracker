"""Activity tracking controller with business logic."""
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from data.database import Database
from utils.config import Config


class ActivityController:
    """Manages activity tracking logic and timing."""
    
    def __init__(self, database: Database, config: Config, logger=None):
        """
        Initialize activity controller.
        
        Args:
            database: Database instance
            config: Configuration instance
            logger: Logger instance
        """
        self.database = database
        self.config = config
        self.logger = logger
        self._lock = threading.Lock()
        self._last_popup_time: Optional[str] = None
        self._popup_callback: Optional[Callable] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def set_popup_callback(self, callback: Callable):
        """Set the callback function to show popup."""
        self._popup_callback = callback
    
    def start_monitoring(self):
        """Start the background monitoring thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        
        if self.logger:
            self.logger.info("Activity monitoring started")
    
    def stop_monitoring(self):
        """Stop the background monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        
        if self.logger:
            self.logger.info("Activity monitoring stopped")
    
    def _monitor_loop(self):
        """Background loop that checks for interval triggers."""
        interval = self.config.interval_minutes
        
        while self._running:
            try:
                now = datetime.now()
                minute = now.minute
                
                # Check if we're at an interval mark
                if minute % interval == 0:
                    time_key = now.strftime("%H:%M")
                    
                    with self._lock:
                        # Prevent duplicate popups in the same minute
                        if self._last_popup_time != time_key:
                            self._last_popup_time = time_key
                            
                            if self.logger:
                                self.logger.info(f"Triggering popup at {time_key}")
                            
                            # Schedule popup on main thread
                            if self._popup_callback:
                                self._popup_callback()
                            
                            # Sleep for a minute to avoid multiple triggers
                            time.sleep(60)
                
                # Check every 5 seconds
                time.sleep(5)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in monitor loop: {e}", exc_info=True)
                time.sleep(5)
    
    def log_activity(self, category: str, description: str = "", 
                    duration_minutes: int = None) -> int:
        """
        Log a new activity.
        
        Args:
            category: Activity category name
            description: Optional description
            duration_minutes: Duration in minutes (default: from config)
        
        Returns:
            ID of the created log entry
        """
        if duration_minutes is None:
            duration_minutes = self.config.interval_minutes
        
        # Validate
        if not category or not category.strip():
            raise ValueError("Category cannot be empty")
        
        log_id = self.database.add_activity_log(
            category_name=category.strip(),
            description=description.strip(),
            duration_minutes=duration_minutes
        )
        
        if self.logger:
            self.logger.info(f"Logged activity: {category} ({duration_minutes} min)")
        
        return log_id
    
    def get_today_summary(self) -> dict:
        """Get summary statistics for today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        activities = self.database.get_activities_by_date_range(today, tomorrow)
        summary = self.database.get_category_summary(today, tomorrow)
        
        total_minutes = sum(item['total_minutes'] for item in summary)
        total_entries = len(activities)
        
        return {
            'activities': activities,
            'summary': summary,
            'total_minutes': total_minutes,
            'total_entries': total_entries,
            'date': today
        }
    
    def get_week_summary(self, week_start: datetime = None) -> dict:
        """Get summary statistics for a week."""
        if week_start is None:
            # Start of current week (Monday)
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        week_end = week_start + timedelta(days=7)
        
        activities = self.database.get_activities_by_date_range(week_start, week_end)
        summary = self.database.get_category_summary(week_start, week_end)
        
        total_minutes = sum(item['total_minutes'] for item in summary)
        
        return {
            'activities': activities,
            'summary': summary,
            'total_minutes': total_minutes,
            'week_start': week_start,
            'week_end': week_end
        }
    
    def get_month_summary(self, month_start: datetime = None) -> dict:
        """Get summary statistics for a month."""
        if month_start is None:
            # Start of current month
            today = datetime.now()
            month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # End of month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        activities = self.database.get_activities_by_date_range(month_start, month_end)
        summary = self.database.get_category_summary(month_start, month_end)
        
        total_minutes = sum(item['total_minutes'] for item in summary)
        
        return {
            'activities': activities,
            'summary': summary,
            'total_minutes': total_minutes,
            'month_start': month_start,
            'month_end': month_end
        }

