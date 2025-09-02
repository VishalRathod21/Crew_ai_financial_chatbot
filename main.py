#!/usr/bin/env python3
"""
CrewAI Financial Market Summary Generator
Main entry point for the financial market automation system
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Process
import logging

# Load environment variables
load_dotenv()

# Import agents
from agents.search_agent import SearchAgent
from agents.summary_agent import SummaryAgent
from agents.formatting_agent import FormattingAgent
from agents.send_agent import SendAgent

# Import utilities
from utils.logger import setup_logger

def main():
    """
    Main function to orchestrate the CrewAI financial market summary pipeline
    """
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Financial Market Summary Generation Pipeline")
    
    try:
        # Validate environment variables
        required_env_vars = [
            'TAVILY_API_KEY',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'LITELLM_API_KEY'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            sys.exit(1)
        
        # Initialize agents
        logger.info("Initializing CrewAI agents...")
        
        search_agent = SearchAgent()
        summary_agent = SummaryAgent()
        formatting_agent = FormattingAgent()
        send_agent = SendAgent()
        
        # Create crew
        crew = Crew(
            agents=[
                search_agent.agent,
                summary_agent.agent,
                formatting_agent.agent,
                send_agent.agent
            ],
            tasks=[
                search_agent.task,
                summary_agent.task,
                formatting_agent.task,
                send_agent.task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        logger.info("Starting CrewAI execution...")
        result = crew.kickoff()
        
        logger.info("Financial Market Summary Pipeline completed successfully")
        logger.info(f"Final result: {result}")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
