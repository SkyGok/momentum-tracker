"""Migration tools for importing existing Excel data into SQLite."""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List
from data.database import Database


class ExcelMigrator:
    """Migrate data from Excel files to SQLite database."""
    
    def __init__(self, reports_dir: Path, database: Database, logger=None):
        """
        Initialize migrator.
        
        Args:
            reports_dir: Directory containing Excel report files
            database: Database instance
            logger: Logger instance
        """
        self.reports_dir = Path(reports_dir)
        self.database = database
        self.logger = logger
    
    def migrate_all_reports(self) -> dict:
        """
        Migrate all Excel reports to the database.
        
        Returns:
            Dictionary with migration statistics
        """
        stats = {
            'files_processed': 0,
            'entries_migrated': 0,
            'errors': []
        }
        
        excel_files = list(self.reports_dir.glob("*_report.xlsx"))
        
        if self.logger:
            self.logger.info(f"Found {len(excel_files)} Excel files to migrate")
        
        for excel_file in excel_files:
            try:
                entries = self.migrate_file(excel_file)
                stats['files_processed'] += 1
                stats['entries_migrated'] += entries
            except Exception as e:
                error_msg = f"Error migrating {excel_file.name}: {e}"
                stats['errors'].append(error_msg)
                if self.logger:
                    self.logger.error(error_msg, exc_info=True)
        
        if self.logger:
            self.logger.info(
                f"Migration complete: {stats['files_processed']} files, "
                f"{stats['entries_migrated']} entries"
            )
        
        return stats
    
    def migrate_file(self, excel_file: Path) -> int:
        """
        Migrate a single Excel file to the database.
        
        Args:
            excel_file: Path to Excel file
            
        Returns:
            Number of entries migrated
        """
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            raise Exception(f"Could not read Excel file: {e}")
        
        if df.empty:
            return 0
        
        entries_migrated = 0
        
        # Handle different column name variations
        time_col = None
        category_col = None
        desc_col = None
        duration_col = None
        date_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'time' in col_lower:
                time_col = col
            elif 'category' in col_lower:
                category_col = col
            elif 'description' in col_lower or 'desc' in col_lower:
                desc_col = col
            elif 'duration' in col_lower:
                duration_col = col
            elif 'date' in col_lower:
                date_col = col
        
        if not category_col:
            raise Exception("Could not find 'Category' column in Excel file")
        
        for _, row in df.iterrows():
            try:
                # Extract data
                category = str(row[category_col]).strip()
                description = str(row[desc_col]).strip() if desc_col and pd.notna(row.get(desc_col)) else ""
                duration = int(row[duration_col]) if duration_col and pd.notna(row.get(duration_col)) else 15
                
                # Parse date and time
                if date_col and pd.notna(row.get(date_col)):
                    if isinstance(row[date_col], str):
                        date_str = row[date_col]
                    else:
                        date_str = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d')
                else:
                    # Try to extract from filename
                    date_str = excel_file.stem.split('_')[0]
                
                if time_col and pd.notna(row.get(time_col)):
                    time_str = str(row[time_col])
                    if ':' in time_str:
                        # Parse time
                        try:
                            if isinstance(row[time_col], str):
                                time_parts = time_str.split(':')
                                hour = int(time_parts[0])
                                minute = int(time_parts[1].split()[0])  # Handle "15 AM" cases
                            else:
                                # Pandas time object
                                dt = pd.to_datetime(row[time_col])
                                hour = dt.hour
                                minute = dt.minute
                            
                            logged_at = datetime.strptime(
                                f"{date_str} {hour:02d}:{minute:02d}:00",
                                "%Y-%m-%d %H:%M:%S"
                            )
                        except:
                            # Fallback to date only
                            logged_at = datetime.strptime(date_str, "%Y-%m-%d")
                    else:
                        logged_at = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    logged_at = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Add to database
                self.database.add_activity_log(
                    category_name=category,
                    description=description,
                    duration_minutes=duration,
                    logged_at=logged_at
                )
                entries_migrated += 1
                
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error migrating row: {e}")
                continue
        
        if self.logger:
            self.logger.info(f"Migrated {entries_migrated} entries from {excel_file.name}")
        
        return entries_migrated

