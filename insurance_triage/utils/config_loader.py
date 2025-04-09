import os
import yaml
from typing import Dict, Any

class ConfigLoader:
    """Load and parse YAML configuration files for the email triage system."""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the config loader.
        
        Args:
            config_dir: Directory where config files are stored.
                        Defaults to 'config' in the parent directory.
        """
        if config_dir is None:
            # Get the directory of this file
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Go one level up and into the config directory
            self.config_dir = os.path.join(os.path.dirname(current_dir), 'config')
        else:
            self.config_dir = config_dir
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load a specific configuration file.
        
        Args:
            config_file: Name of the config file (e.g., 'agents.yaml')
            
        Returns:
            Dictionary containing the configuration
        """
        config_path = os.path.join(self.config_dir, config_file)
        
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {config_path}: {e}")
    
    def load_all_configs(self) -> Dict[str, Any]:
        """
        Load all configuration files in the config directory.
        
        Returns:
            Dictionary containing all configurations
        """
        all_configs = {}
        config_files = [
            'agents.yaml',
            'tasks.yaml',
            'tools.yaml',
            'config.yaml'
        ]
        
        for config_file in config_files:
            try:
                config_data = self.load_config(config_file)
                config_name = os.path.splitext(config_file)[0]  # Remove extension
                all_configs[config_name] = config_data
            except FileNotFoundError:
                print(f"Warning: Config file {config_file} not found. Skipping.")
                
        return all_configs