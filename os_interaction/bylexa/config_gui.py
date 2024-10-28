import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from pathlib import Path
from typing import Dict, Any, List

class ConfigGUI:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_data = self.load_config()
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Bylexa Configuration")
        self.root.geometry("800x600")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # Initialize tabs
        self.init_apps_tab()
        self.init_scripts_tab()
        self.init_settings_tab()

        # Add save button at bottom
        self.save_button = tk.Button(self.root, text="Save Configuration", command=self.save_config)
        self.save_button.pack(pady=10)

    def init_apps_tab(self):
        """Initialize the Applications tab with scrollable content"""
        self.apps_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_tab, text='Applications')

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(self.apps_tab)
        scrollbar = ttk.Scrollbar(self.apps_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create frames for different platforms
        self.windows_frame = ttk.LabelFrame(scrollable_frame, text="Windows Applications")
        self.windows_frame.pack(fill='x', padx=5, pady=5)

        self.mac_frame = ttk.LabelFrame(scrollable_frame, text="MacOS Applications")
        self.mac_frame.pack(fill='x', padx=5, pady=5)

        self.linux_frame = ttk.LabelFrame(scrollable_frame, text="Linux Applications")
        self.linux_frame.pack(fill='x', padx=5, pady=5)

        # Add entry fields for each platform
        self.app_entries = {
            'windows': self.create_app_entries(self.windows_frame, 'windows'),
            'darwin': self.create_app_entries(self.mac_frame, 'darwin'),
            'linux': self.create_app_entries(self.linux_frame, 'linux')
        }

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_app_entries(self, parent: ttk.LabelFrame, platform: str) -> Dict[str, List[ttk.Entry]]:
        """Create entry fields for applications with multiple paths"""
        entries = {}
        
        # Add new app button
        def add_new_app():
            app_name = simpledialog.askstring("New Application", "Enter application name:")
            if app_name:
                entries[app_name] = self.add_app_entries(parent, platform, app_name, [""])

        ttk.Button(parent, text="Add Application", command=add_new_app).pack(pady=5)

        # Add existing apps
        platform_apps = self.config_data.get(platform, {})
        for app_name, paths in platform_apps.items():
            entries[app_name] = self.add_app_entries(parent, platform, app_name, paths)

        return entries

    def add_app_entries(self, parent: ttk.LabelFrame, platform: str, app_name: str, paths: List[str]) -> List[ttk.Entry]:
        """Add entry fields for an application with multiple paths"""
        app_frame = ttk.LabelFrame(parent, text=app_name)
        app_frame.pack(fill='x', padx=5, pady=2)

        entries = []
        
        def add_path_entry():
            self.create_path_entry(app_frame, "", entries)

        for path in paths:
            self.create_path_entry(app_frame, path, entries)

        # Add button for additional paths
        ttk.Button(app_frame, text="Add Path", command=add_path_entry).pack(pady=2)

        return entries

    def create_path_entry(self, parent: ttk.Frame, path: str, entries: List[ttk.Entry]):
        """Create a single path entry with browse button"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=5, pady=2)

        entry = ttk.Entry(frame, width=50)
        entry.pack(side='left', padx=5, fill='x', expand=True)
        entry.insert(0, path)
        entries.append(entry)

        def browse_path():
            file_path = filedialog.askopenfilename()
            if file_path:
                entry.delete(0, tk.END)
                entry.insert(0, file_path)

        ttk.Button(frame, text="Browse", command=browse_path).pack(side='right', padx=5)

    def init_scripts_tab(self):
        """Initialize the Scripts tab"""
        self.script_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.script_tab, text='Scripts')

        # Create script list
        self.script_frame = ttk.LabelFrame(self.script_tab, text="Custom Scripts")
        self.script_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Script listbox with scrollbar
        self.script_listbox = tk.Listbox(self.script_frame, width=50, height=15)
        self.script_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(self.script_frame, orient="vertical", command=self.script_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.script_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons frame
        button_frame = ttk.Frame(self.script_tab)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Add Script", command=self.add_script).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Remove Script", command=self.remove_script).pack(side='left', padx=5)

        # Load existing scripts
        self.load_scripts()

    def init_settings_tab(self):
        """Initialize the Settings tab"""
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text='Settings')

        # Add general settings
        settings_frame = ttk.LabelFrame(self.settings_tab, text="General Settings")
        settings_frame.pack(fill='x', padx=5, pady=5)

        # Default platform setting
        ttk.Label(settings_frame, text="Default Platform:").grid(row=0, column=0, padx=5, pady=5)
        self.platform_var = tk.StringVar(value=self.config_data.get('default_platform', 'windows'))
        platform_combo = ttk.Combobox(settings_frame, textvariable=self.platform_var)
        platform_combo['values'] = ('windows', 'darwin', 'linux')
        platform_combo.grid(row=0, column=1, padx=5, pady=5)

        # User token setting
        ttk.Label(settings_frame, text="User Token:").grid(row=1, column=0, padx=5, pady=5)
        self.token_entry = ttk.Entry(settings_frame, width=50)
        self.token_entry.grid(row=1, column=1, padx=5, pady=5)
        if 'user_token' in self.config_data:
            self.token_entry.insert(0, self.config_data['user_token'])

    def add_script(self):
        """Add a new script to the configuration"""
        file_path = filedialog.askopenfilename(
            title="Select Script",
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if file_path:
            self.script_listbox.insert(tk.END, file_path)

    def remove_script(self):
        """Remove selected script from the configuration"""
        selection = self.script_listbox.curselection()
        if selection:
            self.script_listbox.delete(selection)

    def load_config(self) -> Dict[str, Any]:
        """Load the configuration file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
            return {}

    def load_scripts(self):
        """Load existing scripts into the listbox"""
        scripts = self.config_data.get('scripts', [])
        for script in scripts:
            self.script_listbox.insert(tk.END, script)

    def save_config(self):
        """Save the configuration"""
        try:
            # Update config data with current values
            for platform, app_dict in self.app_entries.items():
                self.config_data[platform] = {}
                for app_name, entries in app_dict.items():
                    # Filter out empty paths
                    paths = [entry.get() for entry in entries if entry.get().strip()]
                    if paths:  # Only save apps with at least one path
                        self.config_data[platform][app_name] = paths

            # Update scripts
            self.config_data['scripts'] = list(self.script_listbox.get(0, tk.END))
            
            # Update settings
            self.config_data['default_platform'] = self.platform_var.get()
            self.config_data['user_token'] = self.token_entry.get()

            # Save to file
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=4)

            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def run_gui():
    config_path = os.path.expanduser("~/.config/bylexa/config.json")
    gui = ConfigGUI(config_path)
    gui.run()

if __name__ == "__main__":
    run_gui()