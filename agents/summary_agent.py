"""
Summary Agent - Creates concise financial market summaries
"""

import os
from datetime import datetime
from crewai import Agent, Task
from litellm import completion
import logging

logger = logging.getLogger(__name__)

class SummaryAgent:
    def __init__(self):
        self.litellm_api_key = os.getenv('LITELLM_API_KEY')
        self.model = os.getenv('LITELLM_MODEL', 'gpt-3.5-turbo')
        
        self.agent = Agent(
            role='Financial Market Summarizer',
            goal='Create clear, concise summaries of financial market updates under 500 words',
            backstory='You are an experienced financial analyst who excels at distilling '
                     'complex market information into digestible summaries for investors '
                     'and traders. You focus on key trends, significant movements, and '
                     'actionable insights.',
            verbose=True,
            allow_delegation=False
        )
        
        self.task = Task(
            description='Analyze the collected financial news and create a comprehensive '
                       'summary under 500 words. Focus on key market movements, trading '
                       'activities, major news events, and their potential impact. '
                       'Ensure the summary is clear, relevant, and actionable.',
            expected_output='A well-structured financial market summary under 500 words '
                          'that highlights key developments, market trends, and significant events.',
            agent=self.agent,
            execution_callback=self.create_summary
        )
    
    def create_summary(self, context=None):
        """
        Create a financial market summary from the search results
        """
        logger.info("Creating financial market summary...")
        
        try:
            # Get search results from context
            search_data = self._extract_search_data(context)
            
            if not search_data:
                logger.warning("No search data available for summarization")
                return self._create_fallback_summary()
            
            # Prepare news content for summarization
            news_content = self._prepare_news_content(search_data)
            
            # Generate summary using LiteLLM
            summary = self._generate_llm_summary(news_content)
            
            logger.info("Successfully created financial market summary")
            return {
                'summary': summary,
                'timestamp': datetime.now().isoformat(),
                'word_count': len(summary.split()),
                'source_count': len(search_data.get('news_data', []))
            }
            
        except Exception as e:
            logger.error(f"Summary creation failed: {str(e)}")
            return self._create_error_summary(str(e))
    
    def _extract_search_data(self, context):
        """
        Extract search data from the context provided by previous agent
        """
        if not context:
            return None
        
        # Handle different context formats
        if isinstance(context, dict):
            return context
        elif isinstance(context, list) and len(context) > 0:
            return context[0] if isinstance(context[0], dict) else None
        
        return None
    
    def _prepare_news_content(self, search_data):
        """
        Prepare news content for LLM summarization
        """
        news_items = search_data.get('news_data', [])
        
        if not news_items:
            return "No recent financial news available."
        
        # Combine news items into structured text
        content_parts = []
        
        for i, item in enumerate(news_items[:10], 1):  # Limit to top 10 items
            title = item.get('title', 'No title')
            content = item.get('content', 'No content')
            source = item.get('source', 'Unknown')
            
            content_parts.append(f"{i}. {title}\n   Source: {source}\n   Summary: {content}\n")
        
        return "\n".join(content_parts)
    
    def _generate_llm_summary(self, news_content):
        """
        Generate summary using LiteLLM
        """
        prompt = f"""
        You are a financial market analyst. Based on the following news items, create a comprehensive market summary under 500 words.

        Focus on:
        1. Key market movements and trends
        2. Significant trading activities
        3. Important earnings or economic reports
        4. Market sentiment and outlook
        5. Any major events affecting financial markets

        News Items:
        {news_content}

        Create a clear, professional summary that provides actionable insights for investors and traders.
        """
        
        try:
            response = completion(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                api_key=self.litellm_api_key,
                max_tokens=600,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Ensure summary is under 500 words
            words = summary.split()
            if len(words) > 500:
                summary = " ".join(words[:500]) + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"LLM summary generation failed: {str(e)}")
            return self._create_manual_summary(news_content)
    
    def _create_manual_summary(self, news_content):
        """
        Create a basic summary when LLM fails
        """
        lines = news_content.split('\n')
        headlines = [line for line in lines if line.strip() and not line.startswith('   ')]
        
        summary = "Financial Market Summary:\n\n"
        summary += "Key developments in today's market:\n"
        
        for headline in headlines[:5]:  # Top 5 headlines
            if headline.strip():
                summary += f"• {headline.strip()}\n"
        
        summary += "\nThis summary was generated from available financial news sources."
        
        return summary
    
    def _create_fallback_summary(self):
        """
        Create a fallback summary when no data is available
        """
        return {
            'summary': "Unable to generate market summary due to lack of available financial news data. "
                      "Please check your news data sources and API connections.",
            'timestamp': datetime.now().isoformat(),
            'word_count': 0,
            'source_count': 0,
            'status': 'fallback'
        }
    
    def _create_error_summary(self, error_message):
        """
        Create an error summary when summarization fails
        """
        return {
            'summary': f"Error generating financial market summary: {error_message}",
            'timestamp': datetime.now().isoformat(),
            'word_count': 0,
            'source_count': 0,
            'status': 'error',
            'error': error_message
        }
