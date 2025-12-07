"""Analytics and visualization controller."""
from datetime import datetime, timedelta
from typing import List, Dict
from data.database import Database


class AnalyticsController:
    """Handles analytics and data visualization."""
    
    def __init__(self, database: Database):
        """
        Initialize analytics controller.
        
        Args:
            database: Database instance
        """
        self.database = database
    
    def get_daily_chart_data(self, date: datetime = None) -> Dict:
        """
        Get data formatted for daily pie/bar chart.
        
        Returns:
            Dictionary with category names and minutes
        """
        if date is None:
            date = datetime.now()
        
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        summary = self.database.get_category_summary(start, end)
        
        categories = [item['category_name'] for item in summary]
        minutes = [item['total_minutes'] for item in summary]
        
        total = sum(minutes) if minutes else 1
        
        percentages = [(m / total * 100) for m in minutes] if total > 0 else []
        
        return {
            'categories': categories,
            'minutes': minutes,
            'percentages': percentages,
            'total_minutes': total
        }
    
    def get_weekly_trend_data(self, weeks: int = 4) -> Dict:
        """
        Get weekly trend data for the last N weeks.
        
        Args:
            weeks: Number of weeks to include
        
        Returns:
            Dictionary with weekly summaries
        """
        today = datetime.now()
        days_since_monday = today.weekday()
        current_week_start = today - timedelta(days=days_since_monday)
        current_week_start = current_week_start.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        weekly_data = []
        
        for i in range(weeks):
            week_start = current_week_start - timedelta(weeks=i)
            week_end = week_start + timedelta(days=7)
            
            summary = self.database.get_category_summary(week_start, week_end)
            total_minutes = sum(item['total_minutes'] for item in summary)
            
            weekly_data.append({
                'week_start': week_start,
                'week_label': week_start.strftime('%b %d'),
                'total_minutes': total_minutes,
                'categories': {item['category_name']: item['total_minutes'] 
                             for item in summary}
            })
        
        return {
            'weeks': list(reversed(weekly_data)),  # Oldest first
            'categories': self._get_all_categories_from_data(weekly_data)
        }
    
    def _get_all_categories_from_data(self, weekly_data: List[Dict]) -> List[str]:
        """Extract all unique categories from weekly data."""
        categories = set()
        for week in weekly_data:
            categories.update(week['categories'].keys())
        return sorted(list(categories))
    
    def get_category_timeline(self, date: datetime, category: str = None) -> List[Dict]:
        """
        Get timeline of activities for a specific date.
        
        Args:
            date: Date to get timeline for
            category: Optional category filter
        
        Returns:
            List of activity entries with timestamps
        """
        activities = self.database.get_activities_by_date(date)
        
        if category:
            activities = [a for a in activities if a['category_name'] == category]
        
        return activities

