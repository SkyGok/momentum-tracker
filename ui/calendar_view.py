"""Calendar view for filtering and viewing activities by date."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from calendar import monthcalendar, month_name
from typing import Optional, Callable

from controllers.activity_controller import ActivityController


class CalendarView:
    """Calendar widget for date selection and activity viewing."""
    
    def __init__(self, parent: tk.Frame, activity_controller: ActivityController):
        """
        Initialize calendar view.
        
        Args:
            parent: Parent frame
            activity_controller: Activity controller instance
        """
        self.parent = parent
        self.activity_controller = activity_controller
        self.selected_date: Optional[datetime] = None
        self.current_month = datetime.now().replace(day=1)
        
        self._setup_ui()
        self._update_calendar()
    
    def _setup_ui(self):
        """Set up the calendar UI."""
        # Month navigation
        nav_frame = tk.Frame(self.parent, bg="#f5f5f5")
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        prev_btn = tk.Button(
            nav_frame,
            text="◀",
            command=self._prev_month,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 12),
            relief="flat",
            width=3
        )
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.month_label = tk.Label(
            nav_frame,
            text="",
            bg="#f5f5f5",
            font=("Helvetica", 14, "bold")
        )
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        next_btn = tk.Button(
            nav_frame,
            text="▶",
            command=self._next_month,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 12),
            relief="flat",
            width=3
        )
        next_btn.pack(side=tk.LEFT, padx=5)
        
        today_btn = tk.Button(
            nav_frame,
            text="Today",
            command=self._go_to_today,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=10
        )
        today_btn.pack(side=tk.RIGHT, padx=5)
        
        # Calendar grid
        calendar_frame = tk.Frame(self.parent, bg="#f5f5f5")
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = tk.Label(
                calendar_frame,
                text=day,
                bg="#E0E0E0",
                font=("Helvetica", 10, "bold"),
                width=10,
                height=2
            )
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        # Calendar days (will be populated)
        self.day_buttons = {}
        for row in range(6):
            for col in range(7):
                btn = tk.Button(
                    calendar_frame,
                    text="",
                    bg="white",
                    font=("Helvetica", 10),
                    width=10,
                    height=3,
                    relief=tk.RAISED,
                    command=lambda r=row, c=col: self._on_date_click(r, c)
                )
                btn.grid(row=row+1, column=col, sticky="nsew", padx=1, pady=1)
                self.day_buttons[(row, col)] = btn
        
        # Configure grid weights
        for i in range(7):
            calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(7):
            calendar_frame.grid_rowconfigure(i+1, weight=1)
        
        # Activity timeline frame
        timeline_frame = tk.LabelFrame(
            self.parent,
            text="Selected Date Activities",
            bg="#f5f5f5",
            font=("Helvetica", 11, "bold")
        )
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable timeline
        timeline_scroll = tk.Scrollbar(timeline_frame)
        timeline_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.timeline_listbox = tk.Listbox(
            timeline_frame,
            font=("Helvetica", 10),
            yscrollcommand=timeline_scroll.set,
            bg="white"
        )
        self.timeline_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        timeline_scroll.config(command=self.timeline_listbox.yview)
    
    def _update_calendar(self):
        """Update calendar display for current month."""
        # Update month label
        month_text = f"{month_name[self.current_month.month]} {self.current_month.year}"
        self.month_label.config(text=month_text)
        
        # Get calendar matrix
        cal = monthcalendar(self.current_month.year, self.current_month.month)
        today = datetime.now()
        
        # Clear all buttons
        for btn in self.day_buttons.values():
            btn.config(text="", bg="white", state=tk.NORMAL)
        
        # Fill calendar
        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                if day == 0:
                    continue
                
                date = datetime(self.current_month.year, self.current_month.month, day)
                btn = self.day_buttons[(row, col)]
                btn.config(text=str(day))
                
                # Highlight today
                if date.date() == today.date():
                    btn.config(bg="#E3F2FD", relief=tk.SOLID, bd=2)
                
                # Highlight selected date
                if self.selected_date and date.date() == self.selected_date.date():
                    btn.config(bg="#4CAF50", fg="white")
    
    def _prev_month(self):
        """Go to previous month."""
        if self.current_month.month == 1:
            self.current_month = self.current_month.replace(year=self.current_month.year - 1, month=12)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month - 1)
        self._update_calendar()
    
    def _next_month(self):
        """Go to next month."""
        if self.current_month.month == 12:
            self.current_month = self.current_month.replace(year=self.current_month.year + 1, month=1)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month + 1)
        self._update_calendar()
    
    def _go_to_today(self):
        """Go to current month and select today."""
        self.current_month = datetime.now().replace(day=1)
        self.selected_date = datetime.now()
        self._update_calendar()
        self._load_date_activities(self.selected_date)
    
    def _on_date_click(self, row: int, col: int):
        """Handle date button click."""
        btn = self.day_buttons[(row, col)]
        if not btn['text']:
            return
        
        day = int(btn['text'])
        self.selected_date = datetime(
            self.current_month.year,
            self.current_month.month,
            day
        )
        
        self._update_calendar()
        self._load_date_activities(self.selected_date)
    
    def _load_date_activities(self, date: datetime):
        """Load and display activities for selected date."""
        self.timeline_listbox.delete(0, tk.END)
        
        try:
            activities = self.activity_controller.database.get_activities_by_date(date)
            
            if not activities:
                self.timeline_listbox.insert(0, f"No activities logged for {date.strftime('%Y-%m-%d')}")
                return
            
            # Group by time
            for activity in activities:
                time_str = activity['logged_at']
                if isinstance(time_str, str):
                    try:
                        dt = datetime.fromisoformat(time_str.replace(' ', 'T'))
                        time_display = dt.strftime("%H:%M")
                    except:
                        time_display = time_str
                else:
                    time_display = time_str
                
                category = activity['category_name']
                desc = activity['description'] or "(no description)"
                duration = activity['duration_minutes']
                
                entry_text = f"[{time_display}] {category} - {desc} ({duration} min)"
                self.timeline_listbox.insert(tk.END, entry_text)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not load activities:\n{e}")

