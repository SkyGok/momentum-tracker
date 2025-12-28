"""Main application entry point for Momentum Tracker."""
import tkinter as tk
from tkinter import messagebox
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from utils.config import Config
from utils.logger import AppLogger
from data.database import Database
from data.migrations import ExcelMigrator
from controllers.activity_controller import ActivityController
from controllers.analytics_controller import AnalyticsController
from controllers.popup_controller import PopupController
from ui.main_window import MainWindow
from ui.settings_window import SettingsWindow


class MomentumTrackerApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        # Initialize configuration
        self.config = Config()
        
        # Initialize logger
        log_dir = self.config.data_dir / "logs"
        self.logger = AppLogger(log_dir)
        self.logger.info("=" * 50)
        self.logger.info("Momentum Tracker starting...")
        
        # Initialize database
        self.database = Database(self.config.db_path, self.logger)
        
        # Check if migration is needed
        self._check_and_migrate()
        
        # Initialize controllers
        self.activity_controller = ActivityController(
            self.database,
            self.config,
            self.logger
        )
        self.analytics_controller = AnalyticsController(self.database)
        self.popup_controller = PopupController(
            None,  # Will be set after root window creation
            self.database,
            self.config,
            self.logger,
            on_submit=self._on_activity_logged,
            on_snooze=self.activity_controller.snooze
        )
        
        # Initialize UI
        self.root = tk.Tk()
        self.popup_controller.root = self.root
        
        # Create main window
        self.main_window = MainWindow(
            self.root,
            self.activity_controller,
            self.analytics_controller,
            self.popup_controller,
            self.config,
            on_settings=self._open_settings
        )
        
        # Start activity monitoring
        if self.config.get("popup_enabled", True):
            self.activity_controller.set_popup_callback(
                self.popup_controller.show_popup
            )
            self.activity_controller.start_monitoring()
        
        self.logger.info("Application initialized successfully")
    
    def _check_and_migrate(self):
        """Check if Excel migration is needed and perform it."""
        # Check if database has any activities
        activities = self.database.get_activities_by_date_range(
            datetime(2020, 1, 1),
            datetime.now()
        )
        
        if not activities:
            # Check if Excel files exist
            excel_files = list(self.config.reports_dir.glob("*_report.xlsx"))
            if excel_files:
                response = messagebox.askyesno(
                    "Import Data",
                    f"Found {len(excel_files)} Excel report files.\n"
                    "Would you like to import them into the database?"
                )
                
                if response:
                    migrator = ExcelMigrator(
                        self.config.reports_dir,
                        self.database,
                        self.logger
                    )
                    stats = migrator.migrate_all_reports()
                    
                    messagebox.showinfo(
                        "Import Complete",
                        f"Imported {stats['entries_migrated']} entries from "
                        f"{stats['files_processed']} files."
                    )
    
    def _on_activity_logged(self, log_id: int, category: str, description: str):
        """Callback when activity is logged."""
        # Refresh dashboard
        if hasattr(self, 'main_window'):
            self.main_window._refresh_dashboard()
    
    def _open_settings(self):
        """Open settings window."""
        def on_settings_close():
            # Refresh categories in popup controller
            # Restart monitoring if interval changed
            if self.config.get("popup_enabled", True):
                self.activity_controller.stop_monitoring()
                self.activity_controller.start_monitoring()
            else:
                self.activity_controller.stop_monitoring()
        
        settings_window = SettingsWindow(
            self.root,
            self.config,
            self.database,
            on_close=on_settings_close
        )
    
    def run(self):
        """Run the application."""
        try:
            self.logger.info("Starting main loop")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            messagebox.showerror("Fatal Error", f"Application error:\n{e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up...")
        self.activity_controller.stop_monitoring()
        self.database.close()
        self.logger.info("Application closed")


def main():
    """Main entry point."""
    # Small startup delay (helps if launched too early)
    import time
    time.sleep(1)
    
    app = MomentumTrackerApp()
    app.run()


if __name__ == "__main__":
    main()

