from crewai import Agent
from langchain.tools import Tool
from typing import Dict, Any, List

class AgentFactory:
    """Factory class for creating CrewAI Agents from configuration."""
    
    def __init__(self, tools_dict: Dict[str, Tool] = None):
        """
        Initialize the agent factory.
        
        Args:
            tools_dict: Dictionary mapping tool names to tool objects
        """
        self.tools_dict = tools_dict or {}
    
    def create_agent(self, agent_config: Dict[str, Any]) -> Agent:
        """
        Create a CrewAI Agent from a configuration dictionary.
        
        Args:
            agent_config: Dictionary containing agent configuration
            
        Returns:
            CrewAI Agent object
        """
        # Extract tool objects based on tool names in config
        agent_tools = []
        if "tools" in agent_config and agent_config["tools"]:
            for tool_name in agent_config["tools"]:
                if tool_name in self.tools_dict:
                    agent_tools.append(self.tools_dict[tool_name])
                else:
                    print(f"Warning: Tool '{tool_name}' not found in available tools.")
        
        # Create the agent
        agent = Agent(
            role=agent_config.get("role", ""),
            goal=agent_config.get("goal", ""),
            backstory=agent_config.get("backstory", ""),
            verbose=agent_config.get("verbose", True),
            allow_delegation=agent_config.get("allow_delegation", False),
            tools=agent_tools
        )
        
        return agent
    
    def create_agents_from_config(self, agents_config: Dict[str, Dict[str, Any]]) -> Dict[str, Agent]:
        """
        Create multiple agents from a configuration dictionary.
        
        Args:
            agents_config: Dictionary mapping agent names to their configurations
            
        Returns:
            Dictionary mapping agent names to agent objects
        """
        agents = {}
        for agent_name, config in agents_config.items():
            agents[agent_name] = self.create_agent(config)
        
        return agents