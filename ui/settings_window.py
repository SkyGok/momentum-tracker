"""Settings window for configuration management."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Optional

from utils.config import Config
from data.database import Database


class SettingsWindow:
    """Settings management window."""
    
    def __init__(self, parent: tk.Tk, config: Config, database: Database,
                 on_close: Optional[Callable] = None):
        """
        Initialize settings window.
        
        Args:
            parent: Parent window
            config: Configuration instance
            database: Database instance
            on_close: Callback when settings are saved
        """
        self.parent = parent
        self.config = config
        self.database = database
        self.on_close = on_close
        
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up settings UI."""
        # Notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Categories tab
        categories_frame = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(categories_frame, text="Categories")
        self._setup_categories_tab(categories_frame)
        
        # Timer tab
        timer_frame = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(timer_frame, text="Timer")
        self._setup_timer_tab(timer_frame)
        
        # Appearance tab
        appearance_frame = tk.Frame(notebook, bg="#f5f5f5")
        notebook.add(appearance_frame, text="Appearance")
        self._setup_appearance_tab(appearance_frame)
        
        # Buttons
        button_frame = tk.Frame(self.window, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=self._save_settings,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            width=15,
            padx=10,
            pady=5
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            bg="#9E9E9E",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            width=15,
            padx=10,
            pady=5
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def _setup_categories_tab(self, parent: tk.Frame):
        """Set up categories management tab."""
        # List frame
        list_frame = tk.Frame(parent, bg="#f5f5f5")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.categories_listbox = tk.Listbox(
            list_frame,
            font=("Helvetica", 11),
            yscrollcommand=scrollbar.set,
            bg="white",
            selectmode=tk.SINGLE
        )
        self.categories_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.categories_listbox.yview)
        
        # Buttons
        btn_frame = tk.Frame(parent, bg="#f5f5f5")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        add_btn = tk.Button(
            btn_frame,
            text="+ Add Category",
            command=self._add_category,
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=10,
            pady=5
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = tk.Button(
            btn_frame,
            text="✏ Edit",
            command=self._edit_category,
            bg="#FF9800",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=10,
            pady=5
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            btn_frame,
            text="🗑 Delete",
            command=self._delete_category,
            bg="#F44336",
            fg="white",
            font=("Helvetica", 10),
            relief="flat",
            padx=10,
            pady=5
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
    
    def _setup_timer_tab(self, parent: tk.Frame):
        """Set up timer settings tab."""
        content_frame = tk.Frame(parent, bg="#f5f5f5")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Interval setting
        interval_frame = tk.Frame(content_frame, bg="#f5f5f5")
        interval_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            interval_frame,
            text="Tracking Interval (minutes):",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        ).pack(side=tk.LEFT, padx=10)
        
        self.interval_var = tk.IntVar(value=self.config.interval_minutes)
        interval_spinbox = tk.Spinbox(
            interval_frame,
            from_=5,
            to=60,
            increment=5,
            textvariable=self.interval_var,
            font=("Helvetica", 11),
            width=10
        )
        interval_spinbox.pack(side=tk.LEFT, padx=10)
        
        # Popup settings
        popup_frame = tk.Frame(content_frame, bg="#f5f5f5")
        popup_frame.pack(fill=tk.X, pady=10)
        
        self.popup_enabled_var = tk.BooleanVar(value=self.config.get("popup_enabled", True))
        popup_check = tk.Checkbutton(
            popup_frame,
            text="Enable automatic popups",
            variable=self.popup_enabled_var,
            bg="#f5f5f5",
            font=("Helvetica", 11)
        )
        popup_check.pack(anchor=tk.W, padx=10)
        
        # Sound settings
        sound_frame = tk.Frame(content_frame, bg="#f5f5f5")
        sound_frame.pack(fill=tk.X, pady=10)
        
        self.sound_enabled_var = tk.BooleanVar(value=self.config.get("sound_enabled", False))
        sound_check = tk.Checkbutton(
            sound_frame,
            text="Enable sound notifications",
            variable=self.sound_enabled_var,
            bg="#f5f5f5",
            font=("Helvetica", 11)
        )
        sound_check.pack(anchor=tk.W, padx=10)
    
    def _setup_appearance_tab(self, parent: tk.Frame):
        """Set up appearance settings tab."""
        content_frame = tk.Frame(parent, bg="#f5f5f5")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Theme selection
        theme_frame = tk.Frame(content_frame, bg="#f5f5f5")
        theme_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            theme_frame,
            text="Theme:",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        ).pack(side=tk.LEFT, padx=10)
        
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_light = tk.Radiobutton(
            theme_frame,
            text="Light",
            variable=self.theme_var,
            value="light",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        )
        theme_light.pack(side=tk.LEFT, padx=10)
        
        theme_dark = tk.Radiobutton(
            theme_frame,
            text="Dark",
            variable=self.theme_var,
            value="dark",
            bg="#f5f5f5",
            font=("Helvetica", 11)
        )
        theme_dark.pack(side=tk.LEFT, padx=10)
        
        # Note: Dark theme implementation would require more UI changes
        note_label = tk.Label(
            content_frame,
            text="Note: Dark theme requires app restart to fully apply.",
            bg="#f5f5f5",
            font=("Helvetica", 9),
            fg="#666",
            justify=tk.LEFT
        )
        note_label.pack(anchor=tk.W, padx=10, pady=10)
    
    def _load_settings(self):
        """Load current settings into UI."""
        # Load categories
        categories = self.config.categories
        self.categories_listbox.delete(0, tk.END)
        for cat in categories:
            self.categories_listbox.insert(tk.END, cat)
    
    def _add_category(self):
        """Add a new category."""
        name = simpledialog.askstring("Add Category", "Enter category name:")
        if name and name.strip():
            name = name.strip()
            if name not in self.config.categories:
                self.categories_listbox.insert(tk.END, name)
            else:
                messagebox.showwarning("Duplicate", "Category already exists.")
    
    def _edit_category(self):
        """Edit selected category."""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to edit.")
            return
        
        index = selection[0]
        old_name = self.categories_listbox.get(index)
        new_name = simpledialog.askstring("Edit Category", "Enter new name:", initialvalue=old_name)
        
        if new_name and new_name.strip():
            new_name = new_name.strip()
            if new_name != old_name and new_name in self.config.categories:
                messagebox.showwarning("Duplicate", "Category already exists.")
                return
            self.categories_listbox.delete(index)
            self.categories_listbox.insert(index, new_name)
    
    def _delete_category(self):
        """Delete selected category."""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to delete.")
            return
        
        index = selection[0]
        name = self.categories_listbox.get(index)
        
        if messagebox.askyesno("Confirm Delete", f"Delete category '{name}'?"):
            self.categories_listbox.delete(index)
    
    def _save_settings(self):
        """Save all settings."""
        try:
            # Save categories
            categories = list(self.categories_listbox.get(0, tk.END))
            self.config.set("categories", categories)
            
            # Save timer settings
            self.config.set("interval_minutes", self.interval_var.get())
            self.config.set("popup_enabled", self.popup_enabled_var.get())
            self.config.set("sound_enabled", self.sound_enabled_var.get())
            
            # Save appearance
            self.config.set("theme", self.theme_var.get())
            
            messagebox.showinfo("Saved", "Settings saved successfully!")
            
            if self.on_close:
                self.on_close()
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings:\n{e}")

