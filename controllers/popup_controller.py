"""Popup controller for activity logging with improved UX."""
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable
from utils.config import Config
from data.database import Database


class PopupController:
    """Manages activity logging popup with improved UX."""
    
    def __init__(self, root: tk.Tk, database: Database, config: Config, 
                 logger=None, on_submit: Callable = None, on_snooze: Callable = None):
        """
        Initialize popup controller.
        
        Args:
            root: Tkinter root window
            database: Database instance
            config: Configuration instance
            logger: Logger instance
            on_submit: Callback when activity is logged
        """
        self.root = root
        self.database = database
        self.config = config
        self.logger = logger
        self.on_submit = on_submit
        self.on_snooze = on_snooze
        self._last_category: Optional[str] = None
        self._popup_window: Optional[tk.Toplevel] = None
    
    def show_popup(self):
        """Show the activity logging popup."""
        # Prevent multiple popups
        if self._popup_window and self._popup_window.winfo_exists():
            self._popup_window.lift()
            self._popup_window.focus_force()
            return
        
        popup = tk.Toplevel(self.root)
        popup.title("What did you just do?")
        popup.title("What did you just do?")
        
        # Calculate position based on mouse cursor
        w, h = 400, 480  # Increased height for snooze options
        
        try:
            # Get mouse position
            mx, my = self.root.winfo_pointerxy()
            
            # Center on mouse
            x = mx - (w // 2)
            y = my - (h // 2)
            
            # Basic clamping to avoid going off-screen (top-left check)
            # For robust multi-monitor clamping, we'd need more complex logic/libraries,
            # but centering on mouse is usually safe enough for "active screen".
            x = max(0, x)
            y = max(0, y)
            
        except Exception:
            # Fallback to center of screen
            ws = self.root.winfo_screenwidth()
            hs = self.root.winfo_screenheight()
            x = (ws // 2) - (w // 2)
            y = (hs // 2) - (h // 2)

        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.configure(bg="#f9f9f9")
        popup.transient(self.root)
        popup.grab_set()  # Modal dialog
        
        self._popup_window = popup
        
        # Title
        title_label = tk.Label(
            popup,
            text="What did you just do?",
            font=("Helvetica", 12, "bold"),
            bg="#f9f9f9"
        )
        title_label.pack(pady=15)
        
        # Quick action buttons
        quick_frame = tk.Frame(popup, bg="#f9f9f9")
        quick_frame.pack(pady=10)
        
        if self._last_category:
            same_btn = tk.Button(
                quick_frame,
                text=f"Same as last ({self._last_category})",
                command=lambda: self._quick_submit(self._last_category, ""),
                bg="#E3F2FD",
                fg="#1976D2",
                font=("Helvetica", 9),
                relief="flat",
                padx=10,
                pady=5
            )
            same_btn.pack(side=tk.LEFT, padx=5)
        
        skip_btn = tk.Button(
            quick_frame,
            text="Didn't track",
            command=lambda: self._quick_submit("", ""),
            bg="#FFF3E0",
            fg="#F57C00",
            font=("Helvetica", 9),
            relief="flat",
            padx=10,
            pady=5
        )
        skip_btn.pack(side=tk.LEFT, padx=5)

        # Snooze button
        snooze_btn = tk.Button(
            quick_frame,
            text="Do Not Disturb",
            command=lambda: self._show_snooze_menu(popup),
            bg="#FFEBEE",
            fg="#D32F2F",
            font=("Helvetica", 9),
            relief="flat",
            padx=10,
            pady=5
        )
        snooze_btn.pack(side=tk.LEFT, padx=5)
        
        # Category selection
        tk.Label(
            popup,
            text="Select category:",
            font=("Helvetica", 10),
            bg="#f9f9f9"
        ).pack(pady=(15, 5))
        
        categories = self.config.categories
        selected_category = tk.StringVar(value=categories[0] if categories else "")
        
        category_frame = tk.Frame(popup, bg="#f9f9f9")
        category_frame.pack(pady=5)
        
        # Create radio buttons in a grid
        cols = 2
        for i, cat in enumerate(categories):
            row = i // cols
            col = i % cols
            rb = tk.Radiobutton(
                category_frame,
                text=cat,
                variable=selected_category,
                value=cat,
                bg="#f9f9f9",
                font=("Helvetica", 10),
                anchor="w"
            )
            rb.grid(row=row, column=col, sticky="w", padx=20, pady=3)
        
        # Description field
        tk.Label(
            popup,
            text="Add details (optional):",
            font=("Helvetica", 10),
            bg="#f9f9f9"
        ).pack(pady=(15, 5))
        
        detail_entry = tk.Entry(popup, width=45, font=("Helvetica", 10))
        detail_entry.pack(pady=5)
        detail_entry.focus()
        
        # Button frame
        button_frame = tk.Frame(popup, bg="#f9f9f9")
        button_frame.pack(pady=20)
        
        def submit(event=None):
            category = selected_category.get()
            description = detail_entry.get().strip()
            
            if not category:
                messagebox.showwarning("Missing Category", "Please select a category.")
                return
            
            try:
                self._submit_activity(category, description)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save activity:\n{e}")
                if self.logger:
                    self.logger.error(f"Error submitting activity: {e}", exc_info=True)
        
        submit_btn = tk.Button(
            button_frame,
            text="Submit",
            command=submit,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            width=15,
            padx=10,
            pady=8
        )
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            bg="#9E9E9E",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            width=15,
            padx=10,
            pady=8
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        popup.bind("<Return>", submit)
        popup.bind("<Escape>", lambda e: popup.destroy())
        
        # Clean up on close
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)
        
        # Removed default centering code as we now position based on mouse at creation time
        # but we need to ensure geometry is applied if not already
        pass
        
        # Ensure it's on top and focused
        popup.lift()
        popup.focus_force()
    
    def _quick_submit(self, category: str, description: str):
        """Quick submit without showing full popup."""
        if category:
            try:
                self._submit_activity(category, description)
                if self._popup_window:
                    self._popup_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save activity:\n{e}")
        else:
            # "Didn't track" - just close
            if self._popup_window:
                self._popup_window.destroy()
    
    def _submit_activity(self, category: str, description: str, duration: int = None):
        """Submit activity to database."""
        if duration is None:
            duration = self.config.interval_minutes
            
        log_id = self.database.add_activity_log(
            category_name=category,
            description=description,
            duration_minutes=duration
        )
        
        self._last_category = category
        
        if self.logger:
            self.logger.info(f"Activity logged: {category} - {description} ({duration}m)")
        
        if self.on_submit:
            self.on_submit(log_id, category, description)
        
        messagebox.showinfo("Saved!", f"Activity logged: {category}")

    def _show_snooze_menu(self, parent):
        """Show focus mode / snooze dialog."""
        # Create a new top-level window for Focus Mode
        dialog = tk.Toplevel(parent)
        dialog.title("Focus Mode")
        dialog.geometry("350x450")
        dialog.configure(bg="#f9f9f9")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center near parent
        x = parent.winfo_x() + 50
        y = parent.winfo_y() + 50
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(
            dialog,
            text="Focus Mode / Do Not Disturb",
            font=("Helvetica", 12, "bold"),
            bg="#f9f9f9"
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text="I will be doing...",
            font=("Helvetica", 10),
            bg="#f9f9f9"
        ).pack(pady=(5, 5))
        
        # Category Dropdown
        categories = self.config.categories
        selected_category = tk.StringVar(value="")
        
        cat_frame = tk.Frame(dialog, bg="#f9f9f9")
        cat_frame.pack(fill=tk.X, padx=30)
        
        category_cb = tk.OptionMenu(cat_frame, selected_category, *categories)
        category_cb.config(bg="white", width=20)
        category_cb.pack(fill=tk.X)
        
        tk.Label(dialog, text="(Optional: Select to log automatically)", 
                 font=("Helvetica", 8, "italic"), bg="#f9f9f9", fg="#666").pack()

        # Description
        tk.Label(dialog, text="Details:", bg="#f9f9f9").pack(pady=(10, 0))
        detail_entry = tk.Entry(dialog, width=30)
        detail_entry.pack(pady=5)

        # Duration Selection
        tk.Label(
            dialog,
            text="For the next...",
            font=("Helvetica", 10, "bold"),
            bg="#f9f9f9"
        ).pack(pady=(15, 5))
        
        duration_var = tk.IntVar(value=60)
        
        dur_frame = tk.Frame(dialog, bg="#f9f9f9")
        dur_frame.pack(pady=5)
        
        durations = [
            ("30m", 30),
            ("1h", 60),
            ("2h", 120),
            ("4h", 240),
            ("Until Tmrw", 480) # effectively 8h
        ]
        
        for i, (label, mins) in enumerate(durations):
            tk.Radiobutton(
                dur_frame,
                text=label,
                variable=duration_var,
                value=mins,
                bg="#f9f9f9",
                indicatoron=0,
                width=8,
                selectcolor="#E3F2FD" 
            ).grid(row=i//3, column=i%3, padx=2, pady=2)

        # Action Buttons
        btn_frame = tk.Frame(dialog, bg="#f9f9f9")
        btn_frame.pack(pady=20, fill=tk.X, padx=20)
        
        def confirm():
            mins = duration_var.get()
            cat = selected_category.get()
            desc = detail_entry.get().strip()
            
            # Log if category provided
            if cat:
                self._submit_activity(cat, desc, duration=mins)
            
            # Start snooze
            self._snooze(mins)
            dialog.destroy()
            
        confirm_btn = tk.Button(
            btn_frame,
            text="Start Focus",
            command=confirm,
            bg="#D32F2F", # Red/Color for DND
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            height=2
        )
        confirm_btn.pack(fill=tk.X, pady=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#f9f9f9",
            fg="black",
            relief="flat"
        )
        cancel_btn.pack(fill=tk.X)

    def _snooze(self, minutes: int):
        """Handle snooze action."""
        if self.on_snooze:
            self.on_snooze(minutes)
            
        if self._popup_window:
            self._popup_window.destroy()
            
        # Optional: Show confirmation?
        # messagebox.showinfo("Snoozed", f"Momentum Tracker snoozed for {minutes} minutes.")

