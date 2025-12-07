"""Popup controller for activity logging with improved UX."""
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable
from utils.config import Config
from data.database import Database


class PopupController:
    """Manages activity logging popup with improved UX."""
    
    def __init__(self, root: tk.Tk, database: Database, config: Config, 
                 logger=None, on_submit: Callable = None):
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
        popup.geometry("400x450")
        popup.configure(bg="#f9f9f9")
        popup.transient(self.root)
        popup.grab_set()  # Modal dialog
        
        self._popup_window = popup
        
        # Center window
        popup.update_idletasks()
        w = popup.winfo_width()
        h = popup.winfo_height()
        ws = popup.winfo_screenwidth()
        hs = popup.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        popup.geometry(f"+{x}+{y}")
        
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
    
    def _submit_activity(self, category: str, description: str):
        """Submit activity to database."""
        log_id = self.database.add_activity_log(
            category_name=category,
            description=description,
            duration_minutes=self.config.interval_minutes
        )
        
        self._last_category = category
        
        if self.logger:
            self.logger.info(f"Activity logged: {category} - {description}")
        
        if self.on_submit:
            self.on_submit(log_id, category, description)
        
        messagebox.showinfo("Saved!", f"Activity logged: {category}")

