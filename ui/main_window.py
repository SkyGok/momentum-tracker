"""Main application window with dashboard."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from controllers.activity_controller import ActivityController
from controllers.analytics_controller import AnalyticsController
from controllers.popup_controller import PopupController
from ui.calendar_view import CalendarView
from utils.config import Config


class MainWindow:
    """Main application window with dashboard and controls."""
    
    def __init__(self, root: tk.Tk, activity_controller: ActivityController,
                 analytics_controller: AnalyticsController, popup_controller: PopupController,
                 config: Config, on_settings: callable = None):
        """
        Initialize main window.
        
        Args:
            root: Tkinter root window
            activity_controller: Activity controller instance
            analytics_controller: Analytics controller instance
            popup_controller: Popup controller instance
            config: Configuration instance
            on_settings: Callback to open settings
        """
        self.root = root
        self.activity_controller = activity_controller
        self.analytics_controller = analytics_controller
        self.popup_controller = popup_controller
        self.config = config
        self.on_settings = on_settings
        
        self._setup_ui()
        self._refresh_dashboard()
    
    def _setup_ui(self):
        """Set up the main window UI."""
        self.root.title(self.config.get("app_name", "Momentum Tracker"))
        self.root.geometry("800x600")
        self.root.configure(bg="#e8f5e9")
        
        # Top bar
        top_frame = tk.Frame(self.root, bg="#4CAF50", height=60)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(
            top_frame,
            text="Momentum Tracker",
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Settings button
        if self.on_settings:
            settings_btn = tk.Button(
                top_frame,
                text="⚙ Settings",
                command=self.on_settings,
                bg="#66BB6A",
                fg="white",
                font=("Helvetica", 10),
                relief="flat",
                padx=10,
                pady=5
            )
            settings_btn.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Main content area with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard tab
        dashboard_frame = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(dashboard_frame, text="Dashboard")
        self._setup_dashboard_tab(dashboard_frame)
        
        # Today's Summary tab
        today_frame = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(today_frame, text="Today")
        self._setup_today_tab(today_frame)
        
        # Calendar tab
        calendar_frame = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(calendar_frame, text="Calendar")
        self.calendar_view = CalendarView(calendar_frame, self.activity_controller)
        
        # Bottom action bar
        bottom_frame = tk.Frame(self.root, bg="#e8f5e9", height=80)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_frame.pack_propagate(False)
        
        log_now_btn = tk.Button(
            bottom_frame,
            text="📝 Log Activity Now",
            command=self.popup_controller.show_popup,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            width=20,
            padx=15,
            pady=10
        )
        log_now_btn.pack(side=tk.LEFT, padx=20, pady=15)
        
        refresh_btn = tk.Button(
            bottom_frame,
            text="🔄 Refresh",
            command=self._refresh_dashboard,
            bg="#FF9800",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=10,
            pady=5
        )
        refresh_btn.pack(side=tk.RIGHT, padx=20, pady=15)
        
        status_label = tk.Label(
            bottom_frame,
            text=f"Auto-asks every {self.config.interval_minutes} minutes",
            bg="#e8f5e9",
            font=("Helvetica", 9, "italic"),
            fg="#666"
        )
        status_label.pack(side=tk.RIGHT, padx=10)
    
    def _setup_dashboard_tab(self, parent: tk.Frame):
        """Set up the dashboard tab with charts."""
        # Summary stats frame
        stats_frame = tk.Frame(parent, bg="#f5f5f5")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Loading...",
            bg="#f5f5f5",
            font=("Helvetica", 11),
            justify=tk.LEFT
        )
        self.stats_label.pack(side=tk.LEFT, padx=10)
        
        # Chart frame
        chart_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chart_frame = chart_frame
        self.chart_canvas = None
    
    def _setup_today_tab(self, parent: tk.Frame):
        """Set up today's activities tab."""
        # Scrollable list
        list_frame = tk.Frame(parent, bg="#f5f5f5")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.activities_listbox = tk.Listbox(
            list_frame,
            font=("Helvetica", 10),
            yscrollcommand=scrollbar.set,
            bg="white",
            selectmode=tk.SINGLE
        )
        self.activities_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.activities_listbox.yview)
    
    def _refresh_dashboard(self):
        """Refresh dashboard data and charts."""
        try:
            # Get today's summary
            summary = self.activity_controller.get_today_summary()
            
            # Update stats
            total_hours = summary['total_minutes'] / 60
            stats_text = (
                f"Today: {summary['total_entries']} entries | "
                f"{summary['total_minutes']} min ({total_hours:.1f} hrs) tracked"
            )
            self.stats_label.config(text=stats_text)
            
            # Update chart
            self._update_chart(summary)
            
            # Update today's list
            self._update_today_list(summary['activities'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh dashboard:\n{e}")
    
    def _update_chart(self, summary: dict):
        """Update the pie chart with today's data."""
        # Clear existing chart
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        if not summary['summary']:
            # No data - show message
            no_data_label = tk.Label(
                self.chart_frame,
                text="No data for today yet.\nLog some activities to see charts!",
                bg="white",
                font=("Helvetica", 12),
                fg="#999"
            )
            no_data_label.pack(expand=True)
            return
        
        # Create pie chart
        fig = Figure(figsize=(6, 5), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        categories = [item['category_name'] for item in summary['summary']]
        minutes = [item['total_minutes'] for item in summary['summary']]
        
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4']
        ax.pie(
            minutes,
            labels=categories,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(categories)]
        )
        ax.set_title("Today's Activity Distribution", fontsize=12, fontweight='bold')
        
        self.chart_canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _update_today_list(self, activities: list):
        """Update the today's activities list."""
        self.activities_listbox.delete(0, tk.END)
        
        if not activities:
            self.activities_listbox.insert(0, "No activities logged today yet.")
            return
        
        for activity in activities:
            time_str = activity['logged_at']
            if isinstance(time_str, str):
                # Try to parse
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
            self.activities_listbox.insert(tk.END, entry_text)
        
        # Scroll to bottom (most recent)
        self.activities_listbox.see(tk.END)

