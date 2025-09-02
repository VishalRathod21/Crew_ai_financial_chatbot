"""
Logger Utility - Structured logging setup for the financial market automation system
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name='crowdwisdom_ai', level=logging.INFO):
    """
    Setup structured logging for the application
    
    Args:
        name (str): Logger name
        level: Logging level
    
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers if logger is already configured
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating log files)
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = os.path.join(log_dir, f'{name}_errors_{datetime.now().strftime("%Y%m%d")}.log')
    
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    return logger

def log_function_call(func):
    """
    Decorator to log function calls and execution time
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('crowdwisdom_ai')
        start_time = datetime.now()
        
        logger.debug(f"Calling function: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Function {func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper

def log_api_call(api_name, endpoint, method='GET'):
    """
    Log API calls with standardized format
    
    Args:
        api_name (str): Name of the API service
        endpoint (str): API endpoint
        method (str): HTTP method
    """
    logger = logging.getLogger('crowdwisdom_ai')
    logger.info(f"API Call | {api_name} | {method} {endpoint}")

def log_api_response(api_name, status_code, response_time=None, data_size=None):
    """
    Log API responses with standardized format
    
    Args:
        api_name (str): Name of the API service
        status_code (int): HTTP status code
        response_time (float): Response time in seconds
        data_size (int): Size of response data
    """
    logger = logging.getLogger('crowdwisdom_ai')
    
    message = f"API Response | {api_name} | Status: {status_code}"
    
    if response_time:
        message += f" | Time: {response_time:.2f}s"
    
    if data_size:
        message += f" | Size: {data_size} bytes"
    
    if status_code >= 200 and status_code < 300:
        logger.info(message)
    elif status_code >= 400:
        logger.error(message)
    else:
        logger.warning(message)

def log_agent_execution(agent_name, task_description, status='started'):
    """
    Log CrewAI agent execution events
    
    Args:
        agent_name (str): Name of the agent
        task_description (str): Description of the task
        status (str): Execution status (started, completed, failed)
    """
    logger = logging.getLogger('crowdwisdom_ai')
    
    if status == 'started':
        logger.info(f"Agent Execution | {agent_name} | Started | {task_description}")
    elif status == 'completed':
        logger.info(f"Agent Execution | {agent_name} | Completed | {task_description}")
    elif status == 'failed':
        logger.error(f"Agent Execution | {agent_name} | Failed | {task_description}")
    else:
        logger.debug(f"Agent Execution | {agent_name} | {status} | {task_description}")

def log_pipeline_event(event_type, message, data=None):
    """
    Log pipeline-level events
    
    Args:
        event_type (str): Type of event (start, complete, error, milestone)
        message (str): Event message
        data (dict): Optional additional data
    """
    logger = logging.getLogger('crowdwisdom_ai')
    
    log_message = f"Pipeline | {event_type.upper()} | {message}"
    
    if data:
        log_message += f" | Data: {data}"
    
    if event_type.lower() == 'error':
        logger.error(log_message)
    elif event_type.lower() in ['start', 'complete']:
        logger.info(log_message)
    else:
        logger.debug(log_message)

class StructuredLogger:
    """
    Structured logger class for consistent logging across the application
    """
    
    def __init__(self, name='crowdwisdom_ai'):
        self.logger = setup_logger(name)
    
    def info(self, message, **kwargs):
        """Log info message with optional structured data"""
        if kwargs:
            message += f" | {kwargs}"
        self.logger.info(message)
    
    def error(self, message, exception=None, **kwargs):
        """Log error message with optional exception and structured data"""
        if exception:
            message += f" | Exception: {str(exception)}"
        if kwargs:
            message += f" | {kwargs}"
        self.logger.error(message)
    
    def warning(self, message, **kwargs):
        """Log warning message with optional structured data"""
        if kwargs:
            message += f" | {kwargs}"
        self.logger.warning(message)
    
    def debug(self, message, **kwargs):
        """Log debug message with optional structured data"""
        if kwargs:
            message += f" | {kwargs}"
        self.logger.debug(message)
    
    def api_call(self, api_name, endpoint, method='GET'):
        """Log API call"""
        log_api_call(api_name, endpoint, method)
    
    def api_response(self, api_name, status_code, response_time=None, data_size=None):
        """Log API response"""
        log_api_response(api_name, status_code, response_time, data_size)
    
    def agent_execution(self, agent_name, task_description, status='started'):
        """Log agent execution"""
        log_agent_execution(agent_name, task_description, status)
    
    def pipeline_event(self, event_type, message, data=None):
        """Log pipeline event"""
        log_pipeline_event(event_type, message, data)
