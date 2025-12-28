"""Reports view for displaying past activity reports."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from controllers.activity_controller import ActivityController
from controllers.analytics_controller import AnalyticsController


class ReportsView:
    """View for displaying past activity reports."""
    
    def __init__(self, parent: tk.Frame, activity_controller: ActivityController,
                 analytics_controller: AnalyticsController):
        """
        Initialize reports view.
        
        Args:
            parent: Parent frame
            activity_controller: Activity controller instance
            analytics_controller: Analytics controller instance
        """
        self.parent = parent
        self.activity_controller = activity_controller
        self.analytics_controller = analytics_controller
        self.current_period_days: Optional[int] = None
        self.current_graph_type: str = "pie"  # pie, dot, column
        self.current_summary_data: Optional[list] = None
        
        self._setup_ui()
        self._load_report(7)  # Default to 7 days
    
    def _setup_ui(self):
        """Set up the reports UI."""
        # Period selection buttons
        period_frame = tk.Frame(self.parent, bg="#f5f5f5")
        period_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            period_frame,
            text="Select Period:",
            bg="#f5f5f5",
            font=("Helvetica", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        # Period buttons
        self.period_7_btn = tk.Button(
            period_frame,
            text="Past 7 Days",
            command=lambda: self._load_report(7),
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=15,
            pady=8,
            width=12
        )
        self.period_7_btn.pack(side=tk.LEFT, padx=5)
        
        self.period_14_btn = tk.Button(
            period_frame,
            text="Past 14 Days",
            command=lambda: self._load_report(14),
            bg="#9E9E9E",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=15,
            pady=8,
            width=12
        )
        self.period_14_btn.pack(side=tk.LEFT, padx=5)
        
        self.period_30_btn = tk.Button(
            period_frame,
            text="Past 1 Month",
            command=lambda: self._load_report(30),
            bg="#9E9E9E",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=15,
            pady=8,
            width=12
        )
        self.period_30_btn.pack(side=tk.LEFT, padx=5)
        
        # Summary frame
        summary_frame = tk.LabelFrame(
            self.parent,
            text="Summary",
            bg="#f5f5f5",
            font=("Helvetica", 11, "bold"),
            padx=10,
            pady=10
        )
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_label = tk.Label(
            summary_frame,
            text="Loading...",
            bg="#f5f5f5",
            font=("Helvetica", 10),
            justify=tk.LEFT,
            anchor="w"
        )
        self.summary_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Graph type selection buttons
        graph_frame = tk.Frame(self.parent, bg="#f5f5f5")
        graph_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            graph_frame,
            text="Graph Type:",
            bg="#f5f5f5",
            font=("Helvetica", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        self.graph_pie_btn = tk.Button(
            graph_frame,
            text="📊 Pie Chart",
            command=lambda: self._switch_graph_type("pie"),
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=15,
            pady=8,
            width=12
        )
        self.graph_pie_btn.pack(side=tk.LEFT, padx=5)
        
        self.graph_dot_btn = tk.Button(
            graph_frame,
            text="📈 Dot Graph",
            command=lambda: self._switch_graph_type("dot"),
            bg="#9E9E9E",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=15,
            pady=8,
            width=12
        )
        self.graph_dot_btn.pack(side=tk.LEFT, padx=5)
        
        self.graph_column_btn = tk.Button(
            graph_frame,
            text="📊 Column Chart",
            command=lambda: self._switch_graph_type("column"),
            bg="#9E9E9E",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=15,
            pady=8,
            width=12
        )
        self.graph_column_btn.pack(side=tk.LEFT, padx=5)
        
        # Chart display frame
        chart_frame = tk.Frame(self.parent, bg="white", relief=tk.RAISED, bd=2)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chart_frame = chart_frame
        self.chart_canvas = None
        
        # Activities list frame
        list_frame = tk.LabelFrame(
            self.parent,
            text="Activities",
            bg="#f5f5f5",
            font=("Helvetica", 11, "bold"),
            padx=10,
            pady=10
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable list
        scroll_frame = tk.Frame(list_frame, bg="#f5f5f5")
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.activities_listbox = tk.Listbox(
            scroll_frame,
            font=("Helvetica", 10),
            yscrollcommand=scrollbar.set,
            bg="white",
            selectmode=tk.SINGLE
        )
        self.activities_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.activities_listbox.yview)
    
    def _update_button_styles(self, active_days: int):
        """Update button styles to show which period is active."""
        buttons = {
            7: self.period_7_btn,
            14: self.period_14_btn,
            30: self.period_30_btn
        }
        
        for days, btn in buttons.items():
            if days == active_days:
                btn.config(bg="#2196F3", fg="white")
            else:
                btn.config(bg="#9E9E9E", fg="white")
    
    def _update_graph_button_styles(self, active_type: str):
        """Update graph button styles to show which type is active."""
        buttons = {
            "pie": self.graph_pie_btn,
            "dot": self.graph_dot_btn,
            "column": self.graph_column_btn
        }
        
        for graph_type, btn in buttons.items():
            if graph_type == active_type:
                btn.config(bg="#4CAF50", fg="white")
            else:
                btn.config(bg="#9E9E9E", fg="white")
    
    def _switch_graph_type(self, graph_type: str):
        """Switch the graph display type."""
        self.current_graph_type = graph_type
        self._update_graph_button_styles(graph_type)
        self._update_chart()
    
    def _update_chart(self):
        """Update the chart display based on current graph type and data."""
        if not self.current_summary_data:
            return
        
        # Clear existing chart
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        if not self.current_summary_data:
            no_data_label = tk.Label(
                self.chart_frame,
                text="No data available for chart.",
                bg="white",
                font=("Helvetica", 12),
                fg="#999"
            )
            no_data_label.pack(expand=True)
            return
        
        # Prepare data
        categories = [item['category_name'] for item in self.current_summary_data]
        minutes = [item['total_minutes'] for item in self.current_summary_data]
        
        # Create figure
        fig = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        # Color palette
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4', '#795548', '#607D8B']
        
        if self.current_graph_type == "pie":
            # Pie chart with labels outside
            wedges, texts, autotexts = ax.pie(
                minutes,
                labels=categories,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(categories)],
                pctdistance=0.85,  # Distance of percentage labels from center
                labeldistance=1.1,  # Distance of category labels from center
                textprops={'fontsize': 10}
            )
            
            # Make labels more readable and movable
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            for text in texts:
                text.set_fontsize(10)
                text.set_fontweight('bold')
            
            # Add legend on the side for better readability
            ax.legend(wedges, categories, title="Categories", 
                     loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                     fontsize=9)
            
            ax.set_title(f"Activity Distribution - Past {self.current_period_days} days", 
                        fontsize=12, fontweight='bold')
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
        
        elif self.current_graph_type == "dot":
            # Dot/Scatter plot (using line plot with markers)
            ax.plot(categories, minutes, marker='o', linestyle='-', linewidth=2, 
                   markersize=10, color='#2196F3', markerfacecolor='#4CAF50')
            ax.set_xlabel('Categories', fontsize=10)
            ax.set_ylabel('Minutes', fontsize=10)
            ax.set_title(f"Activity Time by Category - Past {self.current_period_days} days",
                        fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
        
        elif self.current_graph_type == "column":
            # Column/Bar chart
            bars = ax.bar(categories, minutes, color=colors[:len(categories)])
            ax.set_xlabel('Categories', fontsize=10)
            ax.set_ylabel('Minutes', fontsize=10)
            ax.set_title(f"Activity Time by Category - Past {self.current_period_days} days",
                        fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}m',
                       ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        
        # Display chart
        self.chart_canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _load_report(self, days: int):
        """Load report for the specified number of days."""
        try:
            self.current_period_days = days
            self._update_button_styles(days)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get activities
            activities = self.activity_controller.database.get_activities_by_date_range(
                start_date, end_date
            )
            
            # Get summary by category
            summary = self.activity_controller.database.get_category_summary(
                start_date, end_date
            )
            
            # Store summary data for chart
            self.current_summary_data = summary
            
            # Update summary label
            total_minutes = sum(item['total_minutes'] for item in summary)
            total_hours = total_minutes / 60
            total_entries = len(activities)
            
            period_label = f"{days} days" if days < 30 else "1 month"
            summary_text = (
                f"Period: Past {period_label} | "
                f"Total Entries: {total_entries} | "
                f"Total Time: {total_minutes} min ({total_hours:.1f} hours)"
            )
            
            if summary:
                category_breakdown = " | ".join([
                    f"{item['category_name']}: {item['total_minutes']}m"
                    for item in summary[:5]  # Show top 5 categories
                ])
                summary_text += f"\nCategories: {category_breakdown}"
            
            self.summary_label.config(text=summary_text)
            
            # Update chart
            self._update_graph_button_styles(self.current_graph_type)
            self._update_chart()
            
            # Update activities list
            self.activities_listbox.delete(0, tk.END)
            
            if not activities:
                self.activities_listbox.insert(0, f"No activities found for the past {period_label}.")
                return
            
            # Group activities by date
            activities_by_date = {}
            for activity in activities:
                # Parse date from logged_at
                logged_at = activity['logged_at']
                if isinstance(logged_at, str):
                    try:
                        dt = datetime.fromisoformat(logged_at.replace(' ', 'T'))
                        date_key = dt.strftime('%Y-%m-%d')
                        date_display = dt.strftime('%A, %B %d, %Y')
                    except:
                        date_key = logged_at[:10] if len(logged_at) >= 10 else logged_at
                        date_display = date_key
                else:
                    date_key = str(logged_at)[:10]
                    date_display = date_key
                
                if date_key not in activities_by_date:
                    activities_by_date[date_key] = {
                        'display': date_display,
                        'activities': []
                    }
                
                activities_by_date[date_key]['activities'].append(activity)
            
            # Sort dates (newest first)
            sorted_dates = sorted(activities_by_date.keys(), reverse=True)
            
            # Display activities grouped by date
            for date_key in sorted_dates:
                date_info = activities_by_date[date_key]
                
                # Add date header
                self.activities_listbox.insert(tk.END, "")
                self.activities_listbox.insert(
                    tk.END,
                    f"━━━ {date_info['display']} ━━━"
                )
                
                # Add activities for this date
                for activity in date_info['activities']:
                    time_str = activity['logged_at']
                    if isinstance(time_str, str):
                        try:
                            dt = datetime.fromisoformat(time_str.replace(' ', 'T'))
                            time_display = dt.strftime("%H:%M")
                        except:
                            time_display = time_str[:5] if len(time_str) >= 5 else time_str
                    else:
                        time_display = str(time_str)[:5] if len(str(time_str)) >= 5 else str(time_str)
                    
                    category = activity['category_name']
                    desc = activity['description'] or "(no description)"
                    duration = activity['duration_minutes']
                    
                    entry_text = f"  [{time_display}] {category} - {desc} ({duration} min)"
                    self.activities_listbox.insert(tk.END, entry_text)
            
            # Scroll to top
            self.activities_listbox.see(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load report:\n{e}")
