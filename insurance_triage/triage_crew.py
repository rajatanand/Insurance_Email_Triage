import json
import datetime
from typing import Dict, List, Any
from crewai import Crew, Process
from crewai import Agent, Task, Crew
efrom langchain.tools import Tool

from insurance_triage.utils.config_loader import ConfigLoader
from insurance_triage.agents.agent_factory import AgentFactory
from insurance_triage.tasks.task_factory import TaskFactory
from insurance_triage.tools.email_tools import EmailTools

class InsuranceEmailTriageCrew:
    """Main class for the insurance email triage system."""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the insurance email triage crew.
        
        Args:
            config_dir: Optional directory for configuration files
        """
        # Load configurations
        self.config_loader = ConfigLoader(config_dir)
        self.configs = self.config_loader.load_all_configs()
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agents
        agent_factory = AgentFactory(self.tools)
        self.agents_dict = agent_factory.create_agents_from_config(self.configs.get('agents', {}))
        self.agents = list(self.agents_dict.values())
        
        # Initialize task factory
        self.task_factory = TaskFactory(self.agents_dict)
    
    def _create_tools(self) -> Dict[str, Tool]:
        """Create and initialize tools from the tools configuration."""
        tools_dict = {}
        
        # Define standard tools
        tools_dict["email_extraction_tool"] = Tool(
            name="Email Data Extraction",
            func=EmailTools.extract_email_data,
            description="Extract structured data from email content including policy numbers, claim IDs, and categorization."
        )
        
        tools_dict["email_summary_tool"] = Tool(
            name="Email Summarization",
            func=EmailTools.generate_email_summary,
            description="Generate a concise summary of an email highlighting key points and relevant information."
        )
        
        tools_dict["email_routing_tool"] = Tool(
            name="Email Routing Determination",
            func=EmailTools.determine_routing,
            description="Determine the appropriate team, priority, and handling requirements for an email."
        )
        
        tools_dict["response_template_tool"] = Tool(
            name="Response Template Suggestion",
            func=EmailTools.suggest_response_template,
            description="Suggest an appropriate response template based on email content and type."
        )
        
        return tools_dict
    
    def process_single_email(self, email_content: str, email_metadata: Dict = None):
        """Process a single email through the triage system."""
        if email_metadata is None:
            email_metadata = {
                "sender": "unknown@example.com",
                "received_time": datetime.datetime.now().isoformat(),
                "subject": "Unknown Subject",
                "has_attachments": False
            }
        
        # Create tasks for this email
        tasks = self.task_factory.create_tasks_from_config(
            self.configs.get('tasks', {}),
            email_content
        )
        
        # Create and run the crew
        crew_config = self.configs.get('config', {}).get('crew', {})
        process_type_str = crew_config.get('process', 'sequential')
        process_type = Process.sequential if process_type_str.lower() == 'sequential' else Process.hierarchical
        
        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=crew_config.get('verbose', True),
            process=process_type
        )
        
        result = crew.kickoff()
        
        # Format the results
        try:
            # Extract results from each task
            classification_data = json.loads(tasks[0].output) if isinstance(tasks[0].output, str) else tasks[0].output
            insights_data = tasks[1].output
            compliance_data = tasks[2].output
            routing_data = json.loads(tasks[3].output) if isinstance(tasks[3].output, str) else tasks[3].output
            
            # Parse insights data - it might be a string or a dict
            if isinstance(insights_data, str):
                # Try to extract summary and template from the string
                summary = insights_data
                template = ""
                
                # Look for a pattern like "Summary: ... Template: ..." in the output
                if "Summary:" in insights_data and "Template:" in insights_data:
                    parts = insights_data.split("Template:", 1)
                    summary = parts[0].replace("Summary:", "").strip()
                    template = parts[1].strip()
            else:
                summary = insights_data.get("summary", "")
                template = insights_data.get("template", "")
            
            # Combine into a comprehensive output
            triage_result = {
                "email_metadata": email_metadata,
                "classification": classification_data,
                "summary": summary,
                "suggested_response": template,
                "compliance_issues": compliance_data,
                "routing": routing_data,
                "processed_timestamp": datetime.datetime.now().isoformat()
            }
            
            return triage_result
            
        except Exception as e:
            return {
                "error": f"Error formatting results: {str(e)}",
                "raw_results": [task.output for task in tasks]
            }
    
    def batch_process_emails(self, emails: List[Dict[str, Any]]):
        """Process multiple emails in batch."""
        results = []
        for email in emails:
            content = email.get("content", "")
            metadata = {
                "sender": email.get("sender", "unknown@example.com"),
                "received_time": email.get("received_time", datetime.datetime.now().isoformat()),
                "subject": email.get("subject", "Unknown Subject"),
                "has_attachments": email.get("has_attachments", False)
            }
            
            result = self.process_single_email(content, metadata)
            results.append(result)
            
        return results