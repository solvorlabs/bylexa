# plugin_validator.py - Plugin Testing System

import json
import logging
import inspect
import ast
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)

class PluginValidator:
    """Comprehensive validation system for Bylexa plugins."""
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.validation_results = {}
    
    def validate_plugin_structure(self, plugin_path: Path) -> Dict[str, Any]:
        """Validate plugin directory structure and metadata."""
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {},
            "commands": [],
            "flows": [],
            "scripts": []
        }
        
        # Check required files
        required_files = ["main.py", "plugin.json"]
        for file_name in required_files:
            file_path = plugin_path / file_name
            if not file_path.exists():
                results["errors"].append(f"Missing required file: {file_name}")
                results["valid"] = False
        
        # Validate plugin.json
        plugin_json_path = plugin_path / "plugin.json"
        if plugin_json_path.exists():
            try:
                with open(plugin_json_path, 'r') as f:
                    metadata = json.load(f)
                results["metadata"] = metadata
                
                # Check required metadata fields
                required_fields = ["name", "version", "description", "author"]
                for field in required_fields:
                    if field not in metadata:
                        results["errors"].append(f"Missing metadata field: {field}")
                        results["valid"] = False
                
                # Validate version format
                if "version" in metadata:
                    try:
                        version_parts = metadata["version"].split(".")
                        if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
                            results["warnings"].append("Version should follow semantic versioning (x.y.z)")
                    except:
                        results["errors"].append("Invalid version format")
                        results["valid"] = False
                        
            except json.JSONDecodeError as e:
                results["errors"].append(f"Invalid plugin.json: {str(e)}")
                results["valid"] = False
        
        # Validate main.py structure
        main_py_path = plugin_path / "main.py"
        if main_py_path.exists():
            try:
                with open(main_py_path, 'r') as f:
                    source_code = f.read()
                
                # Parse AST to analyze structure
                tree = ast.parse(source_code)
                
                # Check for Plugin class
                plugin_class_found = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if node.name == "Plugin":
                            plugin_class_found = True
                            # Check if it inherits from PluginBase
                            if node.bases:
                                for base in node.bases:
                                    if isinstance(base, ast.Name) and base.id == "PluginBase":
                                        break
                                else:
                                    results["warnings"].append("Plugin class should inherit from PluginBase")
                
                if not plugin_class_found:
                    results["errors"].append("No Plugin class found in main.py")
                    results["valid"] = False
                
                # Analyze decorators for commands
                commands = self._extract_commands_from_ast(tree)
                results["commands"] = commands
                
            except SyntaxError as e:
                results["errors"].append(f"Syntax error in main.py: {str(e)}")
                results["valid"] = False
            except Exception as e:
                results["errors"].append(f"Error analyzing main.py: {str(e)}")
                results["valid"] = False
        
        # Check for flows directory
        flows_dir = plugin_path / "flows"
        if flows_dir.exists():
            results["flows"] = self._validate_flows(flows_dir)
        
        # Check for scripts directory  
        scripts_dir = plugin_path / "scripts"
        if scripts_dir.exists():
            results["scripts"] = self._validate_scripts(scripts_dir)
        
        return results
    
    def _extract_commands_from_ast(self, tree: ast.AST) -> List[Dict]:
        """Extract command information from AST."""
        commands = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for plugin_command decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name) and decorator.func.id == "plugin_command":
                            command_info = {
                                "name": node.name,
                                "description": "",
                                "parameters": {}
                            }
                            
                            # Extract decorator arguments
                            for keyword in decorator.keywords:
                                if keyword.arg == "description":
                                    if isinstance(keyword.value, ast.Constant):
                                        command_info["description"] = keyword.value.value
                                elif keyword.arg == "parameters":
                                    # Would need more complex parsing for parameters
                                    pass
                            
                            commands.append(command_info)
        
        return commands
    
    def _validate_flows(self, flows_dir: Path) -> List[Dict]:
        """Validate flow definitions."""
        flows = []
        
        for flow_file in flows_dir.glob("*.json"):
            try:
                with open(flow_file, 'r') as f:
                    flow_data = json.load(f)
                
                flow_info = {
                    "file": flow_file.name,
                    "valid": True,
                    "errors": [],
                    "metadata": flow_data
                }
                
                # Validate flow structure
                required_flow_fields = ["name", "trigger_phrases", "steps"]
                for field in required_flow_fields:
                    if field not in flow_data:
                        flow_info["errors"].append(f"Missing field: {field}")
                        flow_info["valid"] = False
                
                # Validate steps
                if "steps" in flow_data:
                    for i, step in enumerate(flow_data["steps"]):
                        if "action" not in step:
                            flow_info["errors"].append(f"Step {i} missing 'action' field")
                            flow_info["valid"] = False
                
                flows.append(flow_info)
                
            except json.JSONDecodeError as e:
                flows.append({
                    "file": flow_file.name,
                    "valid": False,
                    "errors": [f"Invalid JSON: {str(e)}"],
                    "metadata": {}
                })
        
        return flows
    
    def _validate_scripts(self, scripts_dir: Path) -> List[Dict]:
        """Validate individual scripts."""
        scripts = []
        
        for script_file in scripts_dir.glob("*.py"):
            try:
                with open(script_file, 'r') as f:
                    source_code = f.read()
                
                script_info = {
                    "file": script_file.name,
                    "valid": True,
                    "errors": [],
                    "functions": []
                }
                
                # Parse AST
                tree = ast.parse(source_code)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = {
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "docstring": ast.get_docstring(node)
                        }
                        script_info["functions"].append(func_info)
                
                # Check for required functions
                function_names = [f["name"] for f in script_info["functions"]]
                if "run" not in function_names and "execute" not in function_names:
                    script_info["errors"].append("Script should have 'run' or 'execute' function")
                    script_info["valid"] = False
                
                scripts.append(script_info)
                
            except SyntaxError as e:
                scripts.append({
                    "file": script_file.name,
                    "valid": False,
                    "errors": [f"Syntax error: {str(e)}"],
                    "functions": []
                })
        
        return scripts
    
    def test_plugin_functionality(self, plugin_path: Path) -> Dict[str, Any]:
        """Test actual plugin functionality."""
        from bylexa.plugin_dev_kit import PluginManager
        
        results = {
            "load_success": False,
            "commands_work": False,
            "errors": [],
            "command_results": {}
        }
        
        try:
            # Create temporary plugin manager
            temp_dir = Path(tempfile.mkdtemp())
            temp_plugin_dir = temp_dir / plugin_path.name
            shutil.copytree(plugin_path, temp_plugin_dir)
            
            # Initialize plugin manager
            plugin_manager = PluginManager(temp_dir)
            plugin_manager.load_plugin(plugin_path.name)
            
            if plugin_path.name in plugin_manager.plugins:
                results["load_success"] = True
                
                # Test each command
                plugin_instance = plugin_manager.plugins[plugin_path.name]["instance"]
                commands = plugin_instance.get_commands()
                
                for cmd_name, cmd_info in commands.items():
                    try:
                        # Create test parameters
                        test_params = {}
                        if "parameters" in cmd_info:
                            for param_name, param_info in cmd_info["parameters"].items():
                                if param_info.get("type") == "str":
                                    test_params[param_name] = "test_value"
                                elif param_info.get("type") == "int":
                                    test_params[param_name] = 42
                                elif param_info.get("type") == "bool":
                                    test_params[param_name] = True
                        
                        # Execute command
                        method = getattr(plugin_instance, cmd_name)
                        result = method(test_params)
                        
                        results["command_results"][cmd_name] = {
                            "success": True,
                            "result": str(result)
                        }
                        
                    except Exception as e:
                        results["command_results"][cmd_name] = {
                            "success": False,
                            "error": str(e)
                        }
                
                results["commands_work"] = any(
                    cmd["success"] for cmd in results["command_results"].values()
                )
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            results["errors"].append(f"Plugin loading error: {str(e)}")
        
        return results
    
    def generate_validation_report(self, plugin_path: Path) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        plugin_name = plugin_path.name
        
        report = {
            "plugin_name": plugin_name,
            "plugin_path": str(plugin_path),
            "timestamp": str(Path().resolve()),
            "overall_status": "unknown",
            "structure_validation": {},
            "functionality_test": {},
            "recommendations": []
        }
        
        # Structure validation
        report["structure_validation"] = self.validate_plugin_structure(plugin_path)
        
        # Functionality testing
        if report["structure_validation"]["valid"]:
            report["functionality_test"] = self.test_plugin_functionality(plugin_path)
        
        # Overall status
        if (report["structure_validation"]["valid"] and 
            report["functionality_test"].get("load_success", False)):
            report["overall_status"] = "valid"
        elif report["structure_validation"]["valid"]:
            report["overall_status"] = "structure_valid"
        else:
            report["overall_status"] = "invalid"
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        structure = report["structure_validation"]
        functionality = report["functionality_test"]
        
        if structure.get("errors"):
            recommendations.append("Fix structural errors before proceeding")
        
        if structure.get("warnings"):
            recommendations.append("Address warnings to improve plugin quality")
        
        if not structure.get("commands"):
            recommendations.append("Add plugin commands with @plugin_command decorator")
        
        if not functionality.get("load_success", False):
            recommendations.append("Fix plugin loading issues")
        
        if not functionality.get("commands_work", False):
            recommendations.append("Ensure plugin commands execute successfully")
        
        if not structure.get("flows") and not structure.get("scripts"):
            recommendations.append("Consider adding flows or scripts for enhanced functionality")
        
        return recommendations


# Plugin Development Assistant
class PluginDevelopmentAssistant:
    """Assistant for guiding plugin development."""
    
    def __init__(self):
        self.validator = None
    
    def create_plugin_template(self, plugin_name: str, plugin_dir: Path) -> Path:
        """Create a plugin template structure."""
        plugin_path = plugin_dir / plugin_name
        plugin_path.mkdir(parents=True, exist_ok=True)
        
        # Create plugin.json
        metadata = {
            "name": plugin_name,
            "version": "1.0.0",
            "description": f"Description for {plugin_name}",
            "author": "Your Name",
            "keywords": ["automation", "utility"],
            "requirements": [],
            "bylexa_version": ">=1.0.0"
        }
        
        with open(plugin_path / "plugin.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create main.py template
        main_py_content = f'''
from bylexa.plugin_dev_kit import PluginBase, plugin_command

class Plugin(PluginBase):
    """
    {plugin_name} plugin for Bylexa.
    """
    
    @plugin_command(
        description="Example command for {plugin_name}",
        parameters={{
            "message": {{"type": "str", "default": "Hello World"}}
        }}
    )
    def say_hello(self, params):
        """Say hello with a custom message."""
        message = params.get("message", "Hello World")
        return f"{plugin_name} says: {{message}}"
    
    @plugin_command(
        description="Get plugin status",
        parameters={{}}
    )
    def get_status(self, params):
        """Get the current status of the plugin."""
        return {{
            "status": "active",
            "plugin": "{plugin_name}",
            "version": self.metadata.get("version", "unknown")
        }}
'''
        
        with open(plugin_path / "main.py", 'w') as f:
            f.write(main_py_content)
        
        # Create flows directory with example
        flows_dir = plugin_path / "flows"
        flows_dir.mkdir(exist_ok=True)
        
        example_flow = {
            "name": f"{plugin_name} Example Flow",
            "description": f"Example automation flow for {plugin_name}",
            "trigger_phrases": [
                f"start {plugin_name} flow",
                f"run {plugin_name} automation"
            ],
            "steps": [
                {
                    "action": "say_hello",
                    "parameters": {"message": "Flow started!"}
                },
                {
                    "action": "get_status",
                    "parameters": {}
                }
            ]
        }
        
        with open(flows_dir / "example_flow.json", 'w') as f:
            json.dump(example_flow, f, indent=2)
        
        # Create scripts directory with example
        scripts_dir = plugin_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        example_script = f'''
def run(context, **kwargs):
    """
    Example script for {plugin_name}.
    
    Args:
        context: Execution context with user input and system state
        **kwargs: Additional parameters
    
    Returns:
        Result message or data
    """
    user_input = context.get("user_input", "")
    
    # Process user input and extract relevant information
    if "hello" in user_input.lower():
        return f"{plugin_name} script: Hello there!"
    elif "status" in user_input.lower():
        return f"{plugin_name} script: All systems operational"
    else:
        return f"{plugin_name} script: Processed input: {{user_input}}"

def get_required_permissions():
    """Return list of required permissions for this script."""
    return ["file_read", "network_access"]

def get_trigger_patterns():
    """Return patterns that should trigger this script."""
    return [
        r".*{plugin_name.lower()}.*hello.*",
        r".*{plugin_name.lower()}.*status.*"
    ]
'''
        
        with open(scripts_dir / "example_script.py", 'w') as f:
            f.write(example_script)
        
        # Create README
        readme_content = f'''# {plugin_name} Plugin

## Description
{metadata["description"]}

## Commands
- `say_hello`: Example command that says hello
- `get_status`: Get plugin status

## Flows
- `example_flow`: Demonstrates basic flow automation

## Scripts
- `example_script`: Context-aware script example

## Installation
1. Copy this plugin to your Bylexa plugins directory
2. Restart Bylexa or reload plugins
3. Use voice commands like "start {plugin_name} flow"

## Development
This plugin was created using the Bylexa Plugin Development Kit.
'''
        
        with open(plugin_path / "README.md", 'w') as f:
            f.write(readme_content)
        
        return plugin_path


# Testing Framework
def run_comprehensive_plugin_tests(plugins_dir: Path):
    """Run comprehensive tests on all plugins."""
    validator = PluginValidator(plugins_dir)
    
    results = {
        "total_plugins": 0,
        "valid_plugins": 0,
        "invalid_plugins": 0,
        "detailed_results": {}
    }
    
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir():
            results["total_plugins"] += 1
            
            print(f"\n{'='*60}")
            print(f"Testing Plugin: {plugin_dir.name}")
            print('='*60)
            
            report = validator.generate_validation_report(plugin_dir)
            results["detailed_results"][plugin_dir.name] = report
            
            print(f"Status: {report['overall_status'].upper()}")
            
            if report["structure_validation"]["errors"]:
                print("❌ Structure Errors:")
                for error in report["structure_validation"]["errors"]:
                    print(f"  - {error}")
            
            if report["structure_validation"]["warnings"]:
                print("⚠️  Warnings:")
                for warning in report["structure_validation"]["warnings"]:
                    print(f"  - {warning}")
            
            if report["structure_validation"]["commands"]:
                print("✅ Commands Found:")
                for cmd in report["structure_validation"]["commands"]:
                    print(f"  - {cmd['name']}: {cmd['description']}")
            
            if report["functionality_test"]:
                print(f"🔧 Load Success: {report['functionality_test']['load_success']}")
                print(f"🔧 Commands Work: {report['functionality_test']['commands_work']}")
            
            if report["recommendations"]:
                print("💡 Recommendations:")
                for rec in report["recommendations"]:
                    print(f"  - {rec}")
            
            if report["overall_status"] == "valid":
                results["valid_plugins"] += 1
            else:
                results["invalid_plugins"] += 1
    
    print(f"\n{'='*60}")
    print("OVERALL RESULTS")
    print('='*60)
    print(f"Total Plugins: {results['total_plugins']}")
    print(f"Valid Plugins: {results['valid_plugins']}")
    print(f"Invalid Plugins: {results['invalid_plugins']}")
    
    return results


if __name__ == "__main__":
    # Example usage
    plugins_dir = Path("test_plugins")
    
    # Create example plugin
    assistant = PluginDevelopmentAssistant()
    example_plugin = assistant.create_plugin_template("ExamplePlugin", plugins_dir)
    print(f"Created example plugin at: {example_plugin}")
    
    # Run comprehensive tests
    results = run_comprehensive_plugin_tests(plugins_dir)