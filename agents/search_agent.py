"""
Search Agent - Fetches financial news and market data
"""

import os
import requests
from datetime import datetime, timedelta
from crewai import Agent, Task
from litellm import completion
import logging
from serpapi import GoogleSearch

logger = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self):
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        
        self.agent = Agent(
            role='Financial News Searcher',
            goal='Fetch the latest US financial market news and data from the past hour',
            backstory='You are an expert financial news aggregator who specializes in '
                     'collecting real-time market updates, trading activities, and '
                     'significant financial events from reliable sources.',
            verbose=True,
            allow_delegation=False
        )
        
        self.task = Task(
            description='Search for the latest US financial market news from the past hour. '
                       'Focus on major market movements, trading activities, earnings reports, '
                       'economic indicators, and significant financial events. '
                       'Gather information from multiple reliable financial sources.',
            expected_output='A comprehensive collection of financial news articles and market data '
                          'from the past hour, including headlines, summaries, and relevant market metrics.',
            agent=self.agent,
            execution_callback=self.execute_search
        )
    
    def execute_search(self, context=None):
        """
        Execute the search for financial news using Tavily and/or Serper APIs
        """
        logger.info("Executing financial news search...")
        
        try:
            news_data = []
            
            # Use Tavily API if available
            if self.tavily_api_key:
                tavily_results = self._search_tavily()
                news_data.extend(tavily_results)
            
            # Use Serper API if available and Tavily didn't return enough results
            if self.serper_api_key and len(news_data) < 10:
                serper_results = self._search_serper()
                news_data.extend(serper_results)
            
            # Optional: Use Groq for additional summarization
            if self.groq_api_key and news_data:
                enhanced_data = self._enhance_with_groq(news_data)
                news_data = enhanced_data
            
            logger.info(f"Successfully gathered {len(news_data)} news items")
            return {
                'news_data': news_data,
                'timestamp': datetime.now().isoformat(),
                'search_summary': f"Found {len(news_data)} relevant financial news items"
            }
            
        except Exception as e:
            logger.error(f"Search execution failed: {str(e)}")
            return {
                'news_data': [],
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _search_tavily(self):
        """
        Search financial news using Tavily API
        """
        logger.info("Searching with Tavily API...")
        
        try:
            url = "https://api.tavily.com/search"
            
            # Calculate time range (last hour)
            now = datetime.now()
            one_hour_ago = now - timedelta(hours=1)
            
            payload = {
                "api_key": self.tavily_api_key,
                "query": "US financial markets trading news earnings economic indicators",
                "search_depth": "advanced",
                "include_answer": True,
                "include_images": True,
                "max_results": 10,
                "days": 1  # Search within last day, then filter by hour
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            news_items = []
            for result in data.get('results', []):
                news_items.append({
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'published_date': result.get('published_date', ''),
                    'source': 'Tavily'
                })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            return []
    
    def _search_serper(self):
        """
        Search financial news using Serper API
        """
        logger.info("Searching with Serper API...")
        
        try:
            url = "https://google.serper.dev/search"
            
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                "q": "US stock market financial news today trading earnings",
                "num": 10,
                "tbm": "nws"  # News search
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            news_items = []
            for result in data.get('news', []):
                news_items.append({
                    'title': result.get('title', ''),
                    'content': result.get('snippet', ''),
                    'url': result.get('link', ''),
                    'published_date': result.get('date', ''),
                    'source': 'Serper'
                })
            
            return news_items
            
        except Exception as e:
            logger.error(f"Serper search failed: {str(e)}")
            return []
    
    def _enhance_with_groq(self, news_data):
        """
        Use Groq API to enhance and summarize the collected news
        """
        logger.info("Enhancing results with Groq API...")
        
        try:
            # Prepare news text for summarization
            news_text = "\n\n".join([
                f"Title: {item['title']}\nContent: {item['content']}"
                for item in news_data[:5]  # Limit to top 5 to avoid token limits
            ])
            
            response = completion(
                model="groq/llama-3.1-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"Analyze and summarize these financial news items, highlighting key market movements and trends:\n\n{news_text}"
                }],
                api_key=self.groq_api_key
            )
            
            enhanced_summary = response.choices[0].message.content
            
            # Add the enhanced summary to the news data
            news_data.append({
                'title': 'AI-Enhanced Market Analysis',
                'content': enhanced_summary,
                'url': '',
                'published_date': datetime.now().isoformat(),
                'source': 'Groq AI'
            })
            
            return news_data
            
        except Exception as e:
            logger.error(f"Groq enhancement failed: {str(e)}")
            return news_data
