"""Logging system for Momentum Tracker."""
import logging
import sys
from pathlib import Path
from datetime import datetime


class AppLogger:
    """Centralized logging for the application."""
    
    def __init__(self, log_dir: Path, log_level: int = logging.INFO):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level (default: INFO)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("MomentumTracker")
        self.logger.setLevel(log_level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # File handler - daily log files
        log_file = self.log_dir / f"tracker_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # Console handler - only warnings and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def exception(self, message: str):
        """Log exception with traceback."""
        self.logger.exception(message)

