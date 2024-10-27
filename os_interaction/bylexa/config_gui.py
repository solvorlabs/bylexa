# config_gui.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from .config import load_app_configs, save_app_configs, add_app_path, remove_app_path, edit_app_path, get_platform

class ConfigGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Bylexa Config Manager")
        self.platform = get_platform()
        
        # Listbox to display app configurations
        self.listbox = tk.Listbox(self.master, width=50, height=15)
        self.listbox.pack()

        self.refresh_button = tk.Button(self.master, text="Refresh", command=self.refresh)
        self.refresh_button.pack()

        self.add_button = tk.Button(self.master, text="Add Path", command=self.add_config)
        self.add_button.pack()

        self.remove_button = tk.Button(self.master, text="Remove Path", command=self.remove_config)
        self.remove_button.pack()

        self.edit_button = tk.Button(self.master, text="Edit Path", command=self.edit_config)  
        
        
          # Custom Scripts Tab Widgets
        self.script_listbox = tk.Listbox(self.script_tab, width=50, height=15)
        self.script_listbox.pack()

        self.script_refresh_button = tk.Button(self.script_tab, text="Refresh", command=self.refresh_scripts)
        self.script_refresh_button.pack()

        self.script_add_button = tk.Button(self.script_tab, text="Add Script", command=self.add_script)
        self.script_add_button.pack()

        self.script_remove_button = tk.Button(self.script_tab, text="Remove Script", command=self.remove_script)
        self.script_remove_button.pack()

        self.script_edit_button = tk.Button(self.script_tab, text="Edit Script", command=self.edit_script)
        self.script_edit_button.pack()
        
        # New button
        self.edit_button.pack()

        self.refresh()

    def refresh(self):
        """Refresh the listbox with current app configurations."""
        self.listbox.delete(0, tk.END)
        app_configs = load_app_configs().get(self.platform, {})
        for app, paths in app_configs.items():
            for path in paths:
                self.listbox.insert(tk.END, f"{app}: {path}")

    def add_config(self):
        """Prompt to add a new app path."""
        app_name = simpledialog.askstring("Input", "Enter app name:")
        path = simpledialog.askstring("Input", "Enter the path:")
        if app_name and path:
            add_app_path(app_name, path)
            self.refresh()
            messagebox.showinfo("Success", f"Added path '{path}' for app '{app_name}'")

    def remove_config(self):
        """Prompt to remove a selected path."""
        selected = self.listbox.get(tk.ACTIVE)
        if selected:
            app_name, path = selected.split(": ", 1)
            remove_app_path(app_name, path)
            self.refresh()
            messagebox.showinfo("Success", f"Removed path '{path}' for app '{app_name}'")

    def edit_config(self):
        """Prompt to edit a selected app path."""
        selected = self.listbox.get(tk.ACTIVE)
        if selected:
            app_name, old_path = selected.split(": ", 1)
            new_path = simpledialog.askstring("Input", f"Enter new path for '{app_name}':")
            if new_path:
                success = edit_app_path(app_name, old_path, new_path)
                if success:
                    self.refresh()
                    messagebox.showinfo("Success", f"Updated path for app '{app_name}'")
                else:
                    messagebox.showerror("Error", f"Failed to update path for app '{app_name}'")

def run_gui():
    """Run the Config GUI."""
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
