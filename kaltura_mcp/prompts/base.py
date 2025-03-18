"""
Base prompt class for the Kaltura-MCP Server intelligent prompting library.
"""
from typing import Dict, Any, List, Optional, Union
import json
import yaml


class BasePrompt:
    """Base class for all prompts."""
    
    def __init__(self, name: str, description: str):
        """Initialize the prompt with a name and description."""
        self.name = name
        self.description = description
        self.system_message = ""
        self.user_message_template = ""
        self.examples = []
        self.required_tools = []
        self.required_resources = []
    
    def set_system_message(self, system_message: str) -> 'BasePrompt':
        """Set the system message for the prompt."""
        self.system_message = system_message
        return self
    
    def set_user_message_template(self, user_message_template: str) -> 'BasePrompt':
        """Set the user message template for the prompt."""
        self.user_message_template = user_message_template
        return self
    
    def add_example(self, user_message: str, assistant_message: str) -> 'BasePrompt':
        """Add an example to the prompt."""
        self.examples.append({
            "user": user_message,
            "assistant": assistant_message
        })
        return self
    
    def add_required_tool(self, tool_name: str) -> 'BasePrompt':
        """Add a required tool to the prompt."""
        self.required_tools.append(tool_name)
        return self
    
    def add_required_resource(self, resource_uri: str) -> 'BasePrompt':
        """Add a required resource to the prompt."""
        self.required_resources.append(resource_uri)
        return self
    
    def format_user_message(self, **kwargs) -> str:
        """Format the user message template with the given parameters."""
        return self.user_message_template.format(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the prompt to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "system_message": self.system_message,
            "user_message_template": self.user_message_template,
            "examples": self.examples,
            "required_tools": self.required_tools,
            "required_resources": self.required_resources
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the prompt to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """Convert the prompt to a YAML string."""
        return yaml.dump(self.to_dict(), sort_keys=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BasePrompt':
        """Create a prompt from a dictionary."""
        prompt = cls(data["name"], data["description"])
        
        if "system_message" in data:
            prompt.set_system_message(data["system_message"])
        
        if "user_message_template" in data:
            prompt.set_user_message_template(data["user_message_template"])
        
        if "examples" in data:
            for example in data["examples"]:
                prompt.add_example(example["user"], example["assistant"])
        
        if "required_tools" in data:
            for tool in data["required_tools"]:
                prompt.add_required_tool(tool)
        
        if "required_resources" in data:
            for resource in data["required_resources"]:
                prompt.add_required_resource(resource)
        
        return prompt
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BasePrompt':
        """Create a prompt from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'BasePrompt':
        """Create a prompt from a YAML string."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'BasePrompt':
        """Create a prompt from a file (JSON or YAML)."""
        with open(file_path, "r") as f:
            content = f.read()
        
        if file_path.endswith(".json"):
            return cls.from_json(content)
        elif file_path.endswith((".yaml", ".yml")):
            return cls.from_yaml(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")