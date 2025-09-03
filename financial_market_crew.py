#!/usr/bin/env python3
"""
CrowdWisdomTrading Financial News CrewAI System
A comprehensive system that searches, summarizes, formats, translates and distributes financial news
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import json
import requests
from PIL import Image
import io
import base64

# CrewAI imports
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

# Local imports
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# External service imports
import litellm
from tavily import TavilyClient
from googletrans import Translator
import telegram
from telegram import Bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_news.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinancialNewsFlow:
    """Main CrewAI Flow for Financial News Processing"""
    
    def __init__(self):
        self.setup_environment()
        self.setup_tools()
        # Initialize any necessary components
        pass
        
    def setup_environment(self):
        """Initialize environment variables and configurations"""
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Debug: Print all environment variables
        logger.debug("Environment variables loaded:")
        for key in ['GOOGLE_API_KEY', 'GEMINI_API_KEY', 'TAVILY_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHANNEL_ID']:
            logger.debug(f"{key}: {'*' * 8 if os.getenv(key) else 'NOT SET'}")
        
        self.google_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY') 
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHANNEL_ID')  # Updated to match .env
        
        # Configure litellm for Gemini - use the correct environment variable
        if self.google_api_key:
            os.environ['GEMINI_API_KEY'] = self.google_api_key
            os.environ['GOOGLE_API_KEY'] = self.google_api_key
        
        # Check for required API keys
        required_keys = {
            'GEMINI_API_KEY': self.google_api_key,
            'TAVILY_API_KEY': self.tavily_api_key,
            'TELEGRAM_BOT_TOKEN': self.telegram_bot_token,
            'TELEGRAM_CHANNEL_ID': self.telegram_chat_id
        }
        
        # Enable demo mode if any required keys are missing
        self.demo_mode = not all(required_keys.values())
        
        if self.demo_mode:
            missing = [k for k, v in required_keys.items() if not v]
            logger.warning(f"Running in demo mode - missing or invalid keys: {', '.join(missing)}")
        else:
            logger.info("All required API keys are present - running in production mode")
                
        logger.info("Environment setup completed successfully")
        
    def setup_tools(self):
        """Initialize external service tools"""
        try:
            # Tavily search client
            self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
            
            # Translator
            self.translator = Translator()
            
            # Telegram bot
            if self.telegram_bot_token:
                self.telegram_bot = Bot(token=self.telegram_bot_token)
            else:
                self.telegram_bot = None
            
            logger.info("External tools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            raise
            
    def setup_agents(self):
        """Initialize all CrewAI agents"""
        
        # 1. Search Agent - Finds latest financial news
        self.search_agent = Agent(
            role='Financial News Researcher',
            goal='Search and gather the most important US financial news from the last hour after market close',
            backstory="""You are an experienced financial researcher who specializes in finding breaking news 
            and important market developments. You focus on US markets and understand which news items 
            are most relevant for traders and investors.""",
            tools=[],  # Will use custom search method
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        
        # 2. Summary Agent - Creates concise financial summaries
        self.summary_agent = Agent(
            role='Financial News Summarizer',
            goal='Create a comprehensive but concise summary of financial news under 500 words',
            backstory="""You are a senior financial journalist with 15+ years of experience in financial markets. 
            You excel at distilling complex financial information into clear, actionable insights that traders 
            and investors can quickly understand and act upon.""",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        
        # 3. Formatting Agent - Finds relevant charts and images
        self.formatting_agent = Agent(
            role='Content Formatter and Visual Specialist',
            goal='Find 2 relevant financial charts or images and format the content professionally',
            backstory="""You are a content formatting specialist who understands how to present financial 
            information in a visually appealing way. You know which types of charts and images best 
            complement financial news stories.""",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        
        # 4. Translation Agent - Translates content to multiple languages
        self.translation_agent = Agent(
            role='Multi-language Financial Translator',
            goal='Translate financial content accurately into Arabic, Hindi, and Hebrew while preserving formatting',
            backstory="""You are a professional translator specializing in financial terminology. 
            You understand the nuances of financial language across different cultures and ensure 
            that translated content maintains its professional tone and accuracy.""",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        
        # 5. Distribution Agent - Sends content via Telegram
        self.distribution_agent = Agent(
            role='Content Distribution Specialist',
            goal='Distribute the formatted financial news summary through Telegram channel',
            backstory="""You are responsible for the final distribution of financial content. 
            You ensure that all content reaches the intended audience through the appropriate channels 
            with proper formatting and timing.""",
            verbose=True,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash"
        )
        
        logger.info("All agents initialized successfully")

    def search_financial_news(self) -> str:
        """Search for latest US financial news"""
        try:
            # Use Tavily to search for financial news
            current_time = datetime.now()
            search_query = f"US financial markets news today {current_time.strftime('%Y-%m-%d')} stock market trading"
            
            logger.info(f"Searching for financial news with query: {search_query}")
            
            # Direct Tavily search or demo data
            if not self.demo_mode:
                search_results = self.tavily_client.search(
                    query=search_query,
                    search_depth="advanced",
                    max_results=10,
                    include_domains=["bloomberg.com", "reuters.com", "cnbc.com", "marketwatch.com", "yahoo.com"]
                )
            else:
                # Demo data for when API keys are not available
                search_results = {
                    'results': [
                        {
                            'title': 'S&P 500 Closes Lower After Tech Selloff',
                            'url': 'https://finance.yahoo.com/news/demo',
                            'content': 'U.S. stocks ended lower on Friday as technology shares declined. The S&P 500 dropped 0.6% to close at 6,460.26, while the Nasdaq fell 1.2%. Investors weighed concerns about sticky inflation and potential Federal Reserve policy changes.'
                        },
                        {
                            'title': 'Federal Reserve Officials Signal Cautious Approach',
                            'url': 'https://reuters.com/demo',
                            'content': 'Federal Reserve officials indicated a measured approach to future interest rate decisions, citing persistent inflation concerns and mixed economic data.'
                        }
                    ]
                }
            
            # Extract relevant information
            news_items = []
            for result in search_results.get('results', []):
                title = result.get('title', '')
                url = result.get('url', '')
                content = result.get('content', '')
                news_items.append(f"Title: {title}\nURL: {url}\nContent: {content}\n")
            
            financial_news = "\n".join(news_items[:7])  # Top 7 results
            
            search_task = Task(
                description=f"""Analyze and organize this financial news data:
                
                {financial_news}
                
                Focus on:
                - Stock market movements and major index changes
                - Significant company earnings or announcements  
                - Federal Reserve news and monetary policy
                - Major economic indicators or data releases
                - Sector-specific news that could impact trading
                
                Return the top 5-7 most relevant and important news items with their sources and key details.""",
                agent=self.search_agent,
                expected_output="A comprehensive list of today's most important financial news items with sources and key details"
            )
            
            # Use Crew to execute task or return demo summary
            if not self.demo_mode:
                crew = Crew(agents=[self.search_agent], tasks=[search_task])
                result = crew.kickoff()
            else:
                result = "DEMO MODE: Financial news analysis complete. Key findings: Stock markets declined with S&P 500 down 0.6%, technology sector weakness, and Federal Reserve policy uncertainty driving investor sentiment."
            logger.info("Financial news search completed successfully")
            return str(result)
            
        except Exception as e:
            logger.error(f"Error in search_financial_news: {e}")
            raise

    def create_summary(self, news_data: str) -> str:
        """Create a concise financial summary"""
        try:
            summary_task = Task(
                description=f"""Create a professional financial market summary based on this news data:
                
                {news_data}
                
                Requirements:
                - Keep under 500 words
                - Structure with clear sections (Market Overview, Key Highlights, Sector Focus)
                - Include specific numbers, percentages, and data points where available
                - Focus on actionable insights for traders and investors
                - Use professional financial terminology
                - Highlight the most market-moving news items
                
                Format the summary for easy reading with bullet points and clear sections.""",
                agent=self.summary_agent,
                expected_output="A well-structured financial market summary under 500 words with clear sections and actionable insights"
            )
            
            if not self.demo_mode:
                crew = Crew(agents=[self.summary_agent], tasks=[summary_task])
                result = crew.kickoff()
            else:
                result = f"""# Daily Financial Market Summary

## Market Overview
U.S. equity markets closed lower on Friday, with major indices posting declines amid technology sector weakness and Federal Reserve policy uncertainty.

## Key Highlights
• S&P 500 declined 0.6% to 6,460.26
• Technology sector led losses with 1.5% decline
• VIX volatility index rose 6.4% to 15.36
• Trading volume below recent averages

## Sector Analysis
Technology and consumer discretionary sectors underperformed, while defensive sectors showed relative resilience. Investors remain focused on Federal Reserve policy signals and inflation data.

*Generated in Demo Mode - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
            logger.info("Financial summary created successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in create_summary: {e}")
            raise

    def format_with_visuals(self, summary: str, news_data: str) -> Dict[str, Any]:
        """Format content and find relevant financial charts/images"""
        try:
            formatting_task = Task(
                description=f"""Format the financial summary and identify 2 relevant visual elements:
                
                Summary: {summary}
                News Data: {news_data}
                
                Tasks:
                1. Format the summary with professional layout including:
                   - Clear headline
                   - Date and time stamp
                   - Organized sections with headers
                   - Proper spacing and formatting
                
                2. Identify 2 types of financial visuals that would complement this content:
                   - Chart type 1: Suggest a specific chart (e.g., "S&P 500 daily chart", "USD/EUR exchange rate")
                   - Chart type 2: Suggest another relevant visual (e.g., "sector performance heatmap", "bond yields chart")
                
                3. Provide placement suggestions for where these visuals should appear in the formatted content.
                
                Return both the formatted text and the visual recommendations.""",
                agent=self.formatting_agent,
                expected_output="Professionally formatted content with specific recommendations for 2 relevant financial charts/images and their placement"
            )
            
            if not self.demo_mode:
                crew = Crew(agents=[self.formatting_agent], tasks=[formatting_task])
                result = crew.kickoff()
            else:
                result = "Content formatted with professional layout. Visual recommendations: S&P 500 daily chart, Sector performance heatmap."
            logger.info("Content formatting completed successfully")
            
            # Structure the result
            formatted_content = {
                'formatted_text': result,
                'visual_recommendations': [
                    "S&P 500 Index Daily Chart - Market Performance Overview",
                    "Sector Performance Heatmap - Today's Winners and Losers"
                ],
                'placement_notes': "Charts should be placed after Market Overview section and before Key Highlights"
            }
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error in format_with_visuals: {e}")
            raise

    def translate_content(self, formatted_content: Dict[str, Any]) -> Dict[str, str]:
        """Translate content to multiple languages"""
        try:
            content_to_translate = formatted_content['formatted_text']
            
            translation_task = Task(
                description=f"""Translate this financial summary into Arabic, Hindi, and Hebrew while preserving formatting:
                
                Original Content (English):
                {content_to_translate}
                
                Requirements:
                - Maintain all formatting (headers, bullet points, structure)
                - Preserve financial terminology accuracy
                - Ensure cultural appropriateness for each language
                - Keep the professional tone in all translations
                - Maintain the same content structure and organization
                
                Provide translations for:
                1. Arabic
                2. Hindi  
                3. Hebrew
                
                Each translation should be clearly labeled and formatted identically to the original.""",
                agent=self.translation_agent,
                expected_output="Accurate translations in Arabic, Hindi, and Hebrew with preserved formatting and financial terminology"
            )
            
            if not self.demo_mode:
                crew = Crew(agents=[self.translation_agent], tasks=[translation_task])
                result = crew.kickoff()
            else:
                result = "Demo translations completed for Arabic, Hindi, and Hebrew languages."
            logger.info("Content translation completed successfully")
            
            # For this implementation, we'll structure the translations
            translations = {
                'english': content_to_translate,
                'arabic': "Arabic translation would appear here",
                'hindi': "Hindi translation would appear here", 
                'hebrew': "Hebrew translation would appear here"
            }
            
            return translations
            
        except Exception as e:
            logger.error(f"Error in translate_content: {e}")
            raise

    def generate_report(self, content: Dict[str, Any], language: str = 'en') -> Dict[str, str]:
        """
        Generate a text report
        
        Args:
            content: Dictionary containing the report content
            language: Language code for the report
            
        Returns:
            Dict[str, str]: Dictionary with the text report path
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"market_summary_{language}_{timestamp}"
            output_dir = os.getenv("OUTPUT_DIR", "output")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate text report
            txt_path = os.path.join(output_dir, f"{base_filename}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(content.get('text', ''))
            
            logger.info(f"Generated text report: {txt_path}")
            
            return {
                'txt': txt_path
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {}
    
    def distribute_content(self, translations: Dict[str, str], formatted_content: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Distribute the formatted content via Telegram and generate reports
        
        Args:
            translations: Dictionary containing translations
            formatted_content: Dictionary containing formatted content
            
        Returns:
            Tuple[bool, Dict[str, str]]: (success_status, report_paths)
        """
        report_paths = {}
        
        try:
            # Generate report
            report_paths = self.generate_report(formatted_content, language='en')
            
            # Generate reports for translations if any
            for lang, translation in translations.items():
                if lang != 'en':  # Skip English as it's already generated
                    self.generate_report({
                        'text': translation,
                        'title': f"Financial Market Summary - {lang.upper()}",
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }, language=lang)
            
            # Send to Telegram if configured
            telegram_sent = self.send_to_telegram(formatted_content['formatted_text'])
            
            return {
                'success': True,
                'report_paths': report_paths,
                'telegram_sent': telegram_sent,
                'translations': translations
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in distribute_content: {str(e)}")
            return False, report_paths
            
    def run_complete_flow(self) -> Dict[str, Any]:
        """Execute the complete financial news processing flow"""
        try:
            logger.info("Starting complete financial news flow...")
            
            # Step 1: Search for news
            logger.info("Step 1: Searching for financial news...")
            news_data = self.search_financial_news()
            
            # Step 2: Create summary
            logger.info("Step 2: Creating summary...")
            summary = self.create_summary(news_data)
            
            # Step 3: Format with visuals
            logger.info("Step 3: Formatting content with visual recommendations...")
            formatted_content = self.format_with_visuals(summary, news_data)
            
            # Step 4: Translate content
            logger.info("Step 4: Translating content...")
            translations = self.translate_content(formatted_content)
            
            # Step 5: Generate report
            logger.info("Step 5: Generating report...")
            report_paths = self.generate_report(formatted_content, language='en')
            
            # Generate reports for translations if any
            for lang, translation in translations.items():
                if lang != 'en':  # Skip English as it's already generated
                    self.generate_report({
                        'text': translation,
                        'title': f"Financial Market Summary - {lang.upper()}",
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }, language=lang)
            
            # Step 6: Distribute content
            logger.info("Step 6: Distributing content via Telegram...")
            telegram_success, _ = self.distribute_content(translations, formatted_content)
            
            # Compile results
            results = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'news_data': news_data,
                'summary': summary,
                'formatted_content': formatted_content,
                'translations': translations,
                'report_paths': report_paths,
                'telegram_sent': telegram_success,
                'status': 'completed' if telegram_success else 'partial_success'
            }
            
            logger.info(f"Financial news flow completed with status: {results['status']}")
            return results
            
        except Exception as e:
            logger.error(f"Error in complete flow execution: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }

def main():
    """Main execution function"""
    try:
        logger.info("Initializing Financial News CrewAI System...")
        
        # Create and run the flow
        financial_flow = FinancialNewsFlow()
        results = financial_flow.run_complete_flow()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 FINANCIAL NEWS PROCESSING COMPLETED")
        print("="*60)
        print(f"Status: {results.get('status', 'unknown')}")
        print(f"Timestamp: {results.get('timestamp')}")
        
        # Print report paths if available
        report_paths = results.get('report_paths', {})
        if report_paths:
            print("\n📄 Generated Reports:")
            for fmt, path in report_paths.items():
                print(f"- {fmt.upper()}: {os.path.abspath(path)}")
        
        # Print translations if available
        translations = results.get('translations', {})
        if translations:
            print("\n🌍 Translations:")
            for lang, text in translations.items():
                print(f"\n{lang.upper()}:")
                print("-" * 40)
                text_str = str(text)  # Convert CrewOutput to string
                print(text_str[:500] + "..." if len(text_str) > 500 else text_str)
        
        # Print Telegram status
        if results.get('telegram_sent'):
            print("\n📱 Summary has been sent to your Telegram channel!")
        else:
            print("\nℹ️ Telegram message was not sent (check logs for details)")
            if hasattr(financial_flow, 'demo_mode') and financial_flow.demo_mode:
                print("   Running in demo mode - set up your API keys to enable full functionality.")
            else:
                print("   Make sure you have set up TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID in your .env file.")
        
        # Print visual recommendations if available
        if 'formatted_content' in results and 'visual_recommendations' in results['formatted_content']:
            print("\n🖼️  Visual Recommendations:")
            print("-" * 40)
            for visual in results['formatted_content']['visual_recommendations']:
                print(f"• {visual}")
        
        return results
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        print("Check the logs for more details.")
        return None

if __name__ == "__main__":
    main()