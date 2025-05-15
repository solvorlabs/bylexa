import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from . import config
from .plugins import plugin_manager
import requests
from urllib.parse import urljoin
import webbrowser
import logging

logger = logging.getLogger(__name__)

class ConfigGUI:
    def __init__(self):
        self.config_data = config.load_app_configs()
        
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
        self.init_plugins_tab()  # Add this line
        self.script_registry_url = "http://localhost:3000/api/scripts/registry"
        # self.script_registry_url = "https://bylexa.onrender.com/api/scripts/registry"
        self.init_script_browser_tab()

    def init_apps_tab(self):
        """Initialize the Applications tab"""
        self.apps_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_tab, text='Applications')

        # Create canvas and scrollbar
        canvas = tk.Canvas(self.apps_tab)
        scrollbar = ttk.Scrollbar(self.apps_tab, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Platform sections
        self.platform_frames = {}
        for platform in ['windows', 'darwin', 'linux']:
            frame = ttk.LabelFrame(self.scrollable_frame, text=f"{platform.capitalize()} Applications")
            frame.pack(fill='x', padx=5, pady=5)
            self.platform_frames[platform] = frame
            
            # Add new app button for each platform
            ttk.Button(
                frame,
                text="Add New Application",
                command=lambda p=platform: self.add_new_application(p)
            ).pack(pady=5)

            # Load existing applications
            self.load_platform_applications(platform)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def init_scripts_tab(self):
        """Initialize the Scripts tab"""
        self.scripts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.scripts_tab, text='Custom Scripts')

        # Scripts list frame
        list_frame = ttk.LabelFrame(self.scripts_tab, text="Available Scripts")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeview for scripts
        columns = ('Name', 'Path')
        self.scripts_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.scripts_tree.heading(col, text=col)
            self.scripts_tree.column(col, width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.scripts_tree.yview)
        self.scripts_tree.configure(yscrollcommand=scrollbar.set)

        self.scripts_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Buttons frame
        button_frame = ttk.Frame(self.scripts_tab)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Add Script", command=self.add_script).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Script", command=self.edit_script).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Remove Script", command=self.remove_script).pack(side='left', padx=5)

        # Load existing scripts
        self.load_scripts()

    def init_settings_tab(self):
        """Initialize the Settings tab"""
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text='Settings')

        # Settings frame
        settings_frame = ttk.LabelFrame(self.settings_tab, text="General Settings")
        settings_frame.pack(fill='x', padx=5, pady=5)

        # Token setting
        ttk.Label(settings_frame, text="User Token:").grid(row=0, column=0, padx=5, pady=5)
        self.token_entry = ttk.Entry(settings_frame, width=50)
        self.token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Load current token
        current_token = config.load_token()
        if current_token:
            self.token_entry.insert(0, current_token)

    def add_new_application(self, platform: str):
        """Add a new application to a platform"""
        app_name = simpledialog.askstring("New Application", "Enter application name:")
        if app_name:
            path = filedialog.askopenfilename(
                title=f"Select {app_name} executable",
                filetypes=[("Executable files", "*.exe *.app"), ("All files", "*.*")]
            )
            if path:
                if config.add_app_path(platform, app_name, path):
                    self.refresh_platform_applications(platform)
                    messagebox.showinfo("Success", f"Added {app_name} to {platform}")
                else:
                    messagebox.showerror("Error", f"Failed to add {app_name}")

    def load_platform_applications(self, platform: str):
        """Load applications for a specific platform"""
        platform_apps = self.config_data.get(platform, {})
        for app_name, paths in platform_apps.items():
            self.create_app_frame(platform, app_name, paths)

    def create_app_frame(self, platform: str, app_name: str, paths: List[str]):
        """Create a frame for an application with its paths"""
        app_frame = ttk.LabelFrame(self.platform_frames[platform], text=app_name)
        app_frame.pack(fill='x', padx=5, pady=2)

        for path in paths:
            path_frame = ttk.Frame(app_frame)
            path_frame.pack(fill='x', padx=5, pady=2)

            entry = ttk.Entry(path_frame, width=50)
            entry.insert(0, path)
            entry.pack(side='left', padx=5, expand=True)

            ttk.Button(
                path_frame,
                text="Browse",
                command=lambda e=entry: self.browse_path(e)
            ).pack(side='left', padx=2)

            ttk.Button(
                path_frame,
                text="Remove",
                command=lambda p=platform, a=app_name, ph=path: self.remove_path(p, a, ph)
            ).pack(side='left', padx=2)

    def browse_path(self, entry: ttk.Entry):
        """Browse for a file path"""
        path = filedialog.askopenfilename(
            filetypes=[("Executable files", "*.exe *.app"), ("All files", "*.*")]
        )
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def remove_path(self, platform: str, app_name: str, path: str):
        """Remove a path from an application"""
        if messagebox.askyesno("Confirm", f"Remove this path from {app_name}?"):
            if config.remove_app_path(platform, app_name, path):
                self.refresh_platform_applications(platform)
                messagebox.showinfo("Success", "Path removed successfully")
            else:
                messagebox.showerror("Error", "Failed to remove path")

    def refresh_platform_applications(self, platform: str):
        """Refresh the display of applications for a platform"""
        # Clear existing widgets
        for widget in self.platform_frames[platform].winfo_children():
            widget.destroy()

        # Add new application button
        ttk.Button(
            self.platform_frames[platform],
            text="Add New Application",
            command=lambda p=platform: self.add_new_application(p)
        ).pack(pady=5)

        # Reload applications
        self.config_data = config.load_app_configs()
        self.load_platform_applications(platform)

    def add_script(self):
        """Add a new custom script"""
        name = simpledialog.askstring("New Script", "Enter script name:")
        if name:
            path = filedialog.askopenfilename(
                title="Select Script File",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )
            if path:
                if config.add_custom_script(name, path):
                    self.load_scripts()
                    messagebox.showinfo("Success", f"Added script: {name}")
                else:
                    messagebox.showerror("Error", f"Failed to add script: {name}")

    def edit_script(self):
        """Edit an existing custom script"""
        selection = self.scripts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a script to edit")
            return

        item = self.scripts_tree.item(selection[0])
        name = item['values'][0]
        
        path = filedialog.askopenfilename(
            title="Select New Script File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if path:
            if config.update_custom_script(name, path):
                self.load_scripts()
                messagebox.showinfo("Success", f"Updated script: {name}")
            else:
                messagebox.showerror("Error", f"Failed to update script: {name}")

    def remove_script(self):
        """Remove a custom script"""
        selection = self.scripts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a script to remove")
            return

        item = self.scripts_tree.item(selection[0])
        name = item['values'][0]

        if messagebox.askyesno("Confirm", f"Remove script: {name}?"):
            if config.remove_custom_script(name):
                self.load_scripts()
                messagebox.showinfo("Success", f"Removed script: {name}")
            else:
                messagebox.showerror("Error", f"Failed to remove script: {name}")

    def load_scripts(self):
        """Load custom scripts into the treeview"""
        # Clear existing items
        for item in self.scripts_tree.get_children():
            self.scripts_tree.delete(item)

        # Load scripts from config
        scripts = config.get_custom_scripts()
        for name, path in scripts.items():
            self.scripts_tree.insert('', 'end', values=(name, path))

    def save_config(self):
        """Save all configuration changes"""
        try:
            # Save token if changed
            new_token = self.token_entry.get().strip()
            if new_token:
                config.save_token(new_token)

            # Configuration is saved automatically for other operations
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def init_plugins_tab(self):
        """Initialize the Plugins tab"""
        self.plugins_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plugins_tab, text='Plugins')

        # Create frames
        self.installed_frame = ttk.LabelFrame(self.plugins_tab, text="Installed Plugins")
        self.installed_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.available_frame = ttk.LabelFrame(self.plugins_tab, text="Available Plugins")
        self.available_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create treeviews
        columns = ('Name', 'Version', 'Status', 'Description')
        
        self.installed_tree = ttk.Treeview(self.installed_frame, columns=columns, show='headings')
        self.available_tree = ttk.Treeview(self.available_frame, columns=columns, show='headings')

        for tree in (self.installed_tree, self.available_tree):
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

        # Add scrollbars
        for tree, frame in [(self.installed_tree, self.installed_frame),
                           (self.available_tree, self.available_frame)]:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

        # Add buttons
        button_frame = ttk.Frame(self.plugins_tab)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Refresh", command=self.refresh_plugins).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Install", command=self.install_plugin).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Uninstall", command=self.uninstall_plugin).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Enable", command=self.enable_plugin).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Disable", command=self.disable_plugin).pack(side='left', padx=5)

        # Load plugins
        self.refresh_plugins()

    def refresh_plugins(self):
        """Refresh both installed and available plugins"""
        logger.info("Refreshing plugin lists...")

        # Clear existing items
        for tree in (self.installed_tree, self.available_tree):
            for item in tree.get_children():
                tree.delete(item)

        # Load installed plugins
        logger.info("Loading installed plugins...")
        for plugin_id, plugin in plugin_manager.plugins.items():
            metadata = plugin['metadata']
            status = "Enabled" if plugin['enabled'] else "Disabled"
            self.installed_tree.insert('', 'end', values=(
                metadata.get('name', 'Unknown'),
                metadata.get('version', 'N/A'),
                status,
                metadata.get('description', 'N/A')
            ))

        # Load available plugins
        logger.info("Loading available plugins...")
        available_plugins = plugin_manager.get_available_plugins()  # Returns list directly
        print(f"Available plugins: {available_plugins}")  # Debug log
        if available_plugins:  # Check if we got any plugins
            for plugin in available_plugins:
                plugin_id = plugin.get('_id')
                if not plugin_id:
                    logger.warning("Plugin ID is missing")
                    continue
                # Check if plugin is already installed
                plugin_name = plugin.get('name')
                # Check if plugin is not already installed
                if plugin_name and not any(p['metadata']['name'] == plugin_name 
                                        for p in plugin_manager.plugins.values()):
                    self.available_tree.insert('', 'end', values=(
                        plugin_id,
                        plugin_name,
                        plugin.get('version', 'N/A'),
                        'Not Installed',
                        plugin.get('description', 'N/A')
                    ), tags=(plugin.get('_id', plugin_id),))  # Add ID as tag for installation
        else:
            logger.warning("No available plugins found")

    def install_plugin(self):
        """Install selected plugin"""
        print("Install plugin triggered")  # Debug log

        selection = self.available_tree.selection()
        if not selection:
            print("No plugin selected")
            messagebox.showwarning("Warning", "Please select a plugin to install")
            return

        item = self.available_tree.item(selection[0])
        plugin_id = item['tags'][0]  # Get plugin ID from tags
        plugin_name = item['values'][1]  # Get plugin name from values
        print(f"Selected plugin: {plugin_name}")
        print(f"Plugin item values: {item['values']}")  # Debugging line

        print(f"Attempting to install plugin: {plugin_name}")
        if plugin_manager.install_plugin(plugin_id):
            print(f"Plugin {plugin_name} installed successfully")
            messagebox.showinfo("Success", f"Plugin {plugin_name} installed successfully")
            self.refresh_plugins()
            print("Plugin list refreshed")
        else:
            print(f"Failed to install plugin {plugin_name}")
            messagebox.showerror("Error", f"Failed to install plugin {plugin_name}")


    def uninstall_plugin(self):
        """Uninstall selected plugin"""
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a plugin to uninstall")
            return

        item = self.installed_tree.item(selection[0])
        plugin_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Uninstall plugin {plugin_name}?"):
            if plugin_manager.uninstall_plugin(plugin_name):
                messagebox.showinfo("Success", f"Plugin {plugin_name} uninstalled successfully")
                self.refresh_plugins()
            else:
                messagebox.showerror("Error", f"Failed to uninstall plugin {plugin_name}")

    def enable_plugin(self):
        """Enable selected plugin"""
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a plugin to enable")
            return

        item = self.installed_tree.item(selection[0])
        plugin_name = item['values'][0]
        
        if plugin_manager.enable_plugin(plugin_name):
            messagebox.showinfo("Success", f"Plugin {plugin_name} enabled successfully")
            self.refresh_plugins()
        else:
            messagebox.showerror("Error", f"Failed to enable plugin {plugin_name}")

    def disable_plugin(self):
        """Disable selected plugin"""
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a plugin to disable")
            return

        item = self.installed_tree.item(selection[0])
        plugin_name = item['values'][0]
        
        if plugin_manager.disable_plugin(plugin_name):
            messagebox.showinfo("Success", f"Plugin {plugin_name} disabled successfully")
            self.refresh_plugins()
        else:
            messagebox.showerror("Error", f"Failed to disable plugin {plugin_name}")
    
    
    def init_script_browser_tab(self):
        """Initialize the Script Browser tab"""
        self.script_browser_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.script_browser_tab, text='Script Browser')

        # Search frame
        search_frame = ttk.Frame(self.script_browser_tab)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_scripts).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Refresh", command=lambda: self.refresh_available_scripts()).pack(side='left', padx=5)

        # Split view for scripts
        paned = ttk.PanedWindow(self.script_browser_tab, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)

        # Scripts list frame
        list_frame = ttk.LabelFrame(paned, text="Available Scripts")
        paned.add(list_frame)

        # Create treeview for scripts
        columns = ('Name', 'Author', 'Rating', 'Downloads')
        self.scripts_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.scripts_tree.heading(col, text=col)
            self.scripts_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.scripts_tree.yview)
        self.scripts_tree.configure(yscrollcommand=scrollbar.set)
        self.scripts_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Script details frame
        details_frame = ttk.LabelFrame(paned, text="Script Details")
        paned.add(details_frame)

        # Details content
        self.script_details = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, width=40, height=20)
        self.script_details.pack(fill='both', expand=True, padx=5, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Install", command=self.install_selected_script).pack(side='left', padx=5)
        ttk.Button(button_frame, text="View Source", command=self.view_script_source).pack(side='left', padx=5)
        ttk.Button(button_frame, text="View Documentation", command=self.view_script_docs).pack(side='left', padx=5)

        # Bind selection event
        self.scripts_tree.bind('<<TreeviewSelect>>', self.on_script_select)

        # Load initial scripts
        self.refresh_available_scripts()

    def search_scripts(self):
        """Search for scripts based on the search term"""
        search_term = self.search_entry.get().strip()
        self.refresh_available_scripts(search_term)

    def refresh_available_scripts(self, search_term: str = ""):
        """Refresh the list of available scripts"""
        try:
            self.script_details.delete('1.0', tk.END)  # Clear details view
            params = {'q': search_term} if search_term else {}
            response = requests.get(self.script_registry_url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Server returned status code {response.status_code}")
                
            scripts = response.json().get('scripts', [])

            # Clear existing items
            for item in self.scripts_tree.get_children():
                self.scripts_tree.delete(item)

            # Add scripts to treeview
            for script in scripts:
                values = (
                    script.get('name', 'N/A'),
                    script.get('author', 'N/A'),
                    script.get('rating', 0),
                    script.get('downloads', 0)
                )
                self.scripts_tree.insert('', 'end', values=values, tags=(script.get('_id', ''),))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch scripts: {str(e)}")

    def on_script_select(self, event):
        """Handle script selection"""
        selection = self.scripts_tree.selection()
        if not selection:
            self.script_details.delete('1.0', tk.END)
            return

        try:
            script_id = self.scripts_tree.item(selection[0], 'tags')[0]
            if not script_id:  # Check if script_id is empty
                raise ValueError("Invalid script ID")

            response = requests.get(f"{self.script_registry_url}/{script_id}")
            if response.status_code != 200:
                raise Exception(f"Server returned status code {response.status_code}")

            script_details = response.json()
            if not script_details:
                raise ValueError("No script details received")

            # Update details view
            self.script_details.delete('1.0', tk.END)
            details_text = f"""Name: {script_details.get('name', 'N/A')}
                            Author: {script_details.get('author', 'N/A')}
                            Version: {script_details.get('version', 'N/A')}
                            Rating: {script_details.get('rating', 0)} ({script_details.get('num_ratings', 0)} ratings)
                            Downloads: {script_details.get('downloads', 0)}

                            Description: {script_details.get('description', 'No description available')}

                            Requirements: {', '.join(script_details.get('requirements', ['None']))}

                            Keywords: {', '.join(script_details.get('keywords', ['None']))}
                            """
            self.script_details.insert('1.0', details_text)

        except Exception as e:
            self.script_details.delete('1.0', tk.END)
            self.script_details.insert('1.0', f"Error loading script details: {str(e)}")
            print(f"Error in on_script_select: {str(e)}")  # For debugging

    def install_selected_script(self):
        """Install the selected script"""
        selection = self.scripts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a script to install")
            return

        try:
            script_id = self.scripts_tree.item(selection[0], 'tags')[0]
            
            # Download and install script
            response = requests.get(f"{self.script_registry_url}/{script_id}/download")
            if response.status_code == 200:
                script_data = response.json()
                
                # Save script file
                scripts_dir = Path(config.load_app_configs().get('scripts_directory', 'scripts'))
                if not scripts_dir.is_absolute():
                    scripts_dir = Path.home() / '.bylexa' / scripts_dir
                
                scripts_dir.mkdir(parents=True, exist_ok=True)
                script_path = scripts_dir / f"{script_data['name']}.py"
                
                with open(script_path, 'w') as f:
                    f.write(script_data['source'])

                # Add to custom scripts
                config.add_custom_script(script_data['name'], str(script_path))
                
                messagebox.showinfo("Success", f"Script '{script_data['name']}' installed successfully")
                self.load_scripts()  # Refresh scripts list
            else:
                messagebox.showerror("Error", "Failed to download script")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to install script: {str(e)}")

    def view_script_source(self):
        """View the source code of the selected script"""
        selection = self.scripts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a script to view")
            return

        try:
            script_id = self.scripts_tree.item(selection[0], 'tags')[0]
            url = urljoin(self.script_registry_url, f"/api/scripts/registry/{script_id}/source")
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open source view: {str(e)}")

    def view_script_docs(self):
        """View the documentation of the selected script"""
        selection = self.scripts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a script to view docs")
            return

        try:
            script_id = self.scripts_tree.item(selection[0], 'tags')[0]
            url = urljoin(self.script_registry_url, f"/api/scripts/registry/{script_id}/docs")
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open documentation: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def run_gui():
    """Main entry point for the GUI application"""
    try:
        gui = ConfigGUI()
        gui.run()
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    run_gui()