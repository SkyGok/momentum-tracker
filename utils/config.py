"""Configuration management for Momentum Tracker."""
import os
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manages application configuration with defaults and user overrides."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "app_name": "Momentum Tracker",
        "interval_minutes": 15,
        "popup_enabled": True,
        "sound_enabled": False,
        "theme": "light",  # light or dark
        "categories": ["Working", "Chilling", "Gaming", "Academics", "Business"],
        "auto_save": True,
        "export_to_excel": False,  # Optional Excel export
    }
    
    def __init__(self, base_dir: str = None):
        """
        Initialize configuration.
        
        Args:
            base_dir: Base directory for the app. If None, uses current file's parent.
        """
        if base_dir is None:
            # Get the project root (parent of utils/)
            self.base_dir = Path(__file__).parent.parent.absolute()
        else:
            self.base_dir = Path(base_dir).absolute()
        
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.base_dir / "reports"
        self.config_file = self.data_dir / "config.json"
        self.db_path = self.data_dir / "momentum_tracker.db"
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults
                config = self.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Save default config
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value and save."""
        self._config[key] = value
        self._save_config(self._config)
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values."""
        self._config.update(updates)
        self._save_config(self._config)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
    
    @property
    def interval_minutes(self) -> int:
        """Get the tracking interval in minutes."""
        return self.get("interval_minutes", 15)
    
    @property
    def categories(self) -> list:
        """Get the list of activity categories."""
        return self.get("categories", [])
    
    @property
    def theme(self) -> str:
        """Get the current theme."""
        return self.get("theme", "light")

