"""
Send Agent - Distributes the final report via Telegram and saves PDF locally
"""

import os
import json
from datetime import datetime
from crewai import Agent, Task
import requests
import logging
from utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)

class SendAgent:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.pdf_generator = PDFGenerator()
        
        self.agent = Agent(
            role='Report Distributor',
            goal='Send final market reports via Telegram and save PDF copies locally',
            backstory='You are a communication specialist responsible for distributing '
                     'financial market reports through multiple channels. You ensure '
                     'reports reach their intended audience and maintain local archives.',
            verbose=True,
            allow_delegation=False
        )
        
        self.task = Task(
            description='Send the final English financial market summary to Telegram '
                       'channel and save a comprehensive PDF version locally. Include '
                       'charts and ensure proper formatting for distribution.',
            expected_output='Successful distribution of the report via Telegram and creation '
                          'of a local PDF file with English content and images.',
            agent=self.agent,
            execution_callback=self.distribute_report
        )
    
    def distribute_report(self, context=None):
        """
        Distribute the final report via Telegram and save PDF locally
        """
        logger.info("Starting report distribution...")
        
        try:
            # Extract formatted data from context
            formatted_data = self._extract_formatted_data(context)
            
            if not formatted_data:
                logger.warning("No formatted data available for distribution")
                return self._create_fallback_distribution()
            
            # Generate timestamp for file naming
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create PDF report
            pdf_result = self._create_pdf_report(formatted_data, timestamp)
            
            # Send to Telegram
            telegram_result = self._send_to_telegram(formatted_data)
            
            # Prepare distribution summary
            distribution_summary = {
                'pdf_created': pdf_result.get('success', False),
                'pdf_path': pdf_result.get('file_path', ''),
                'telegram_sent': telegram_result.get('success', False),
                'telegram_message_id': telegram_result.get('message_id', ''),
                'timestamp': datetime.now().isoformat(),
                'content_type': 'English-only',
                'images_included': len(formatted_data.get('images', []))
            }
            
            logger.info("Report distribution completed successfully")
            return distribution_summary
            
        except Exception as e:
            logger.error(f"Report distribution failed: {str(e)}")
            return self._create_error_distribution(str(e))
    
    def _extract_formatted_data(self, context):
        """
        Extract formatted data from the context provided by previous agent
        """
        if not context:
            return None
        
        if isinstance(context, dict):
            return context
        elif isinstance(context, list) and len(context) > 0:
            # Look for formatted data in context list
            for item in context:
                if isinstance(item, dict) and 'formatted_summary' in item:
                    return item
        
        return None
    
    def _create_pdf_report(self, formatted_data, timestamp):
        """
        Create a comprehensive PDF report with formatted content and images
        """
        logger.info("Creating PDF report...")
        
        try:
            # Prepare data for PDF generation
            pdf_data = {
                'title': f'Financial Market Summary - {datetime.now().strftime("%B %d, %Y")}',
                'formatted_summary': formatted_data.get('formatted_summary', ''),
                'images': formatted_data.get('images', []),
                'timestamp': timestamp
            }
            
            # Generate PDF
            pdf_path = self.pdf_generator.create_report(pdf_data)
            
            return {
                'success': True,
                'file_path': pdf_path,
                'message': 'PDF report created successfully'
            }
            
        except Exception as e:
            logger.error(f"PDF creation failed: {str(e)}")
            return {
                'success': False,
                'file_path': '',
                'error': str(e),
                'message': 'PDF creation failed'
            }
    
    def _send_to_telegram(self, formatted_data):
        """
        Send the report to Telegram channel
        """
        logger.info("Sending report to Telegram...")
        
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured")
            return {
                'success': False,
                'message': 'Telegram credentials not configured',
                'message_id': ''
            }
        
        try:
            # Prepare message content
            formatted_summary = formatted_data.get('formatted_summary', '')
            images = formatted_data.get('images', [])
            
            # Create main message
            message = f"📈 *Financial Market Summary*\n"
            message += f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
            
            # Add formatted content (truncated for Telegram limits)
            if len(formatted_summary) > 2000:
                message += formatted_summary[:2000] + "...\n\n"
            else:
                message += formatted_summary + "\n\n"
            
            # Send main message
            main_result = self._send_telegram_message(message)
            
            # Send images if available
            for image in images[:2]:  # Telegram has media limits
                self._send_telegram_image(image)
            
            return {
                'success': main_result.get('success', False),
                'message_id': main_result.get('message_id', ''),
                'message': 'Report sent to Telegram successfully'
            }
            
        except Exception as e:
            logger.error(f"Telegram sending failed: {str(e)}")
            return {
                'success': False,
                'message_id': '',
                'error': str(e),
                'message': 'Telegram sending failed'
            }
    
    def _send_telegram_message(self, text):
        """
        Send a text message to Telegram
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            data = {
                'chat_id': self.telegram_chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                return {
                    'success': True,
                    'message_id': result['result']['message_id']
                }
            else:
                return {
                    'success': False,
                    'message_id': '',
                    'error': result.get('description', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Telegram message sending failed: {str(e)}")
            return {
                'success': False,
                'message_id': '',
                'error': str(e)
            }
    
    def _send_telegram_image(self, image_data):
        """
        Send an image to Telegram
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendPhoto"
            
            data = {
                'chat_id': self.telegram_chat_id,
                'photo': image_data.get('url', ''),
                'caption': image_data.get('title', 'Financial Chart')
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('ok', False)
            
        except Exception as e:
            logger.error(f"Telegram image sending failed: {str(e)}")
            return False
    
    def _create_fallback_distribution(self):
        """
        Create fallback distribution result when no data is available
        """
        return {
            'pdf_created': False,
            'pdf_path': '',
            'telegram_sent': False,
            'telegram_message_id': '',
            'timestamp': datetime.now().isoformat(),
            'content_type': 'English-only',
            'images_included': 0,
            'status': 'fallback',
            'message': 'No formatted data available for distribution'
        }
    
    def _create_error_distribution(self, error_message):
        """
        Create error distribution result when distribution fails
        """
        return {
            'pdf_created': False,
            'pdf_path': '',
            'telegram_sent': False,
            'telegram_message_id': '',
            'timestamp': datetime.now().isoformat(),
            'content_type': 'English-only',
            'images_included': 0,
            'status': 'error',
            'error': error_message,
            'message': f'Distribution failed: {error_message}'
        }
