from crewai import Task
from typing import Dict, Any, List

class TaskFactory:
    """Factory class for creating CrewAI Tasks from configuration."""
    
    def __init__(self, agents_dict: Dict[str, Any] = None):
        """
        Initialize the task factory.
        
        Args:
            agents_dict: Dictionary mapping agent names to agent objects
        """
        self.agents_dict = agents_dict or {}
        self.tasks_dict = {}  # Will store created tasks for context references
    
    def create_task(self, task_name: str, task_config: Dict[str, Any], email_content: str = None) -> Task:
        """
        Create a CrewAI Task from a configuration dictionary.
        
        Args:
            task_name: Name of the task
            task_config: Dictionary containing task configuration
            email_content: Optional email content to include in task description
            
        Returns:
            CrewAI Task object
        """
        # Get the agent for this task
        agent_name = task_config.get("agent")
        if agent_name not in self.agents_dict:
            raise ValueError(f"Agent '{agent_name}' not found for task '{task_name}'")
        
        agent = self.agents_dict[agent_name]
        
        # Prepare description with email content if provided
        description = task_config.get("description", "")
        if email_content:
            description = description + f"\n\nEmail Content:\n{email_content}"
        
        # Process context (dependencies on other tasks)
        context = []
        if "context" in task_config and task_config["context"]:
            for context_task_name in task_config["context"]:
                if context_task_name in self.tasks_dict:
                    context.append(self.tasks_dict[context_task_name])
                else:
                    print(f"Warning: Context task '{context_task_name}' not found for task '{task_name}'")
        
        # Create the task
        task = Task(
            description=description,
            agent=agent,
            expected_output=task_config.get("expected_output", ""),
            context=context
        )
        
        # Store the task for potential use as context in other tasks
        self.tasks_dict[task_name] = task
        
        return task
    
    def create_tasks_from_config(self, tasks_config: Dict[str, Dict[str, Any]], email_content: str = None) -> List[Task]:
        """
        Create multiple tasks from a configuration dictionary.
        
        Args:
            tasks_config: Dictionary mapping task names to their configurations
            email_content: Optional email content to include in task descriptions
            
        Returns:
            List of task objects in the order they were defined
        """
        tasks = []
        for task_name, config in tasks_config.items():
            task = self.create_task(task_name, config, email_content)
            tasks.append(task)
        
        return tasks