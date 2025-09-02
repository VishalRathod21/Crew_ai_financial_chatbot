"""
Formatting Agent - Adds charts and images to the summary
"""

import os
import requests
from datetime import datetime
from crewai import Agent, Task
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class FormattingAgent:
    def __init__(self):
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        
        self.agent = Agent(
            role='Content Formatter and Visual Enhancer',
            goal='Find relevant financial charts and images to enhance the market summary',
            backstory='You are a content specialist who enhances financial reports '
                     'by finding and integrating relevant charts, graphs, and visual '
                     'elements that support the narrative and improve readability.',
            verbose=True,
            allow_delegation=False
        )
        
        self.task = Task(
            description='Find 2 relevant financial charts or images related to the '
                       'market summary content. Insert them at logical places in the '
                       'summary to enhance understanding. Ensure images are appropriate '
                       'and add value to the financial narrative.',
            expected_output='An enhanced summary with 2 relevant financial charts or images '
                          'embedded at appropriate locations, along with image URLs and captions.',
            agent=self.agent,
            execution_callback=self.format_content
        )
    
    def format_content(self, context=None):
        """
        Format the summary content with relevant charts and images
        """
        logger.info("Formatting content with charts and images...")
        
        try:
            # Extract summary from context
            summary_data = self._extract_summary_data(context)
            
            if not summary_data:
                logger.warning("No summary data available for formatting")
                return self._create_fallback_formatted_content()
            
            summary_text = summary_data.get('summary', '')
            
            # Find relevant financial images/charts
            images = self._find_financial_images(summary_text)
            
            # Format the summary with images
            formatted_content = self._insert_images_in_summary(summary_text, images)
            
            logger.info(f"Successfully formatted content with {len(images)} images")
            return {
                'formatted_summary': formatted_content,
                'images': images,
                'timestamp': datetime.now().isoformat(),
                'original_summary': summary_text
            }
            
        except Exception as e:
            logger.error(f"Content formatting failed: {str(e)}")
            return self._create_error_formatted_content(str(e))
    
    def _extract_summary_data(self, context):
        """
        Extract summary data from the context provided by previous agent
        """
        if not context:
            return None
        
        if isinstance(context, dict):
            return context
        elif isinstance(context, list) and len(context) > 0:
            # Look for summary data in context list
            for item in context:
                if isinstance(item, dict) and 'summary' in item:
                    return item
        
        return None
    
    def _find_financial_images(self, summary_text):
        """
        Find relevant financial images/charts using search APIs
        """
        logger.info("Searching for relevant financial images...")
        
        images = []
        
        try:
            # Extract key terms from summary for image search
            search_terms = self._extract_search_terms(summary_text)
            
            # Search for financial charts and images
            if self.serper_api_key:
                serper_images = self._search_images_serper(search_terms)
                images.extend(serper_images)
            
            if self.tavily_api_key and len(images) < 2:
                tavily_images = self._search_images_tavily(search_terms)
                images.extend(tavily_images)
            
            # If no images found, use fallback financial charts
            if len(images) < 2:
                fallback_images = self._get_fallback_images()
                images.extend(fallback_images)
            
            # Limit to 2 images as requested
            return images[:2]
            
        except Exception as e:
            logger.error(f"Image search failed: {str(e)}")
            return self._get_fallback_images()[:2]
    
    def _extract_search_terms(self, summary_text):
        """
        Extract relevant search terms from the summary for image search
        """
        # Common financial terms to look for
        financial_terms = [
            'stock market', 'trading', 'earnings', 'S&P 500', 'Dow Jones',
            'NASDAQ', 'NYSE', 'futures', 'commodities', 'bonds', 'forex',
            'cryptocurrency', 'bitcoin', 'market chart', 'financial graph'
        ]
        
        # Find terms mentioned in the summary
        found_terms = []
        summary_lower = summary_text.lower()
        
        for term in financial_terms:
            if term in summary_lower:
                found_terms.append(term)
        
        # Default search terms if none found
        if not found_terms:
            found_terms = ['stock market chart', 'financial market graph']
        
        return found_terms[:3]  # Limit to top 3 terms
    
    def _search_images_serper(self, search_terms):
        """
        Search for images using Serper API
        """
        logger.info("Searching images with Serper API...")
        
        try:
            url = "https://google.serper.dev/images"
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            images = []
            
            for term in search_terms[:2]:  # Search for top 2 terms
                payload = {
                    "q": f"{term} financial chart",
                    "num": 5
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                for img in data.get('images', [])[:1]:  # One image per term
                    if self._is_valid_image_url(img.get('imageUrl', '')):
                        images.append({
                            'url': img.get('imageUrl'),
                            'title': img.get('title', term),
                            'source': 'Serper',
                            'search_term': term
                        })
            
            return images
            
        except Exception as e:
            logger.error(f"Serper image search failed: {str(e)}")
            return []
    
    def _search_images_tavily(self, search_terms):
        """
        Search for images using Tavily API
        """
        logger.info("Searching images with Tavily API...")
        
        try:
            url = "https://api.tavily.com/search"
            
            images = []
            
            for term in search_terms[:2]:
                payload = {
                    "api_key": self.tavily_api_key,
                    "query": f"{term} financial chart graph",
                    "search_depth": "basic",
                    "include_images": True,
                    "max_results": 3
                }
                
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                for result in data.get('results', [])[:1]:
                    images_list = result.get('images', [])
                    if images_list:
                        img_url = images_list[0]
                        if self._is_valid_image_url(img_url):
                            images.append({
                                'url': img_url,
                                'title': f"Financial Chart - {term}",
                                'source': 'Tavily',
                                'search_term': term
                            })
            
            return images
            
        except Exception as e:
            logger.error(f"Tavily image search failed: {str(e)}")
            return []
    
    def _get_fallback_images(self):
        """
        Provide fallback financial chart URLs when search fails
        """
        return [
            {
                'url': 'https://via.placeholder.com/600x400/0066cc/ffffff?text=Stock+Market+Chart',
                'title': 'Stock Market Performance Chart',
                'source': 'Fallback',
                'search_term': 'stock market'
            },
            {
                'url': 'https://via.placeholder.com/600x400/009900/ffffff?text=Trading+Volume+Graph',
                'title': 'Trading Volume Analysis',
                'source': 'Fallback',
                'search_term': 'trading volume'
            }
        ]
    
    def _is_valid_image_url(self, url):
        """
        Validate if the URL is a valid image URL
        """
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for common image extensions
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']
            return any(url.lower().endswith(ext) for ext in image_extensions) or 'image' in url.lower()
            
        except Exception:
            return False
    
    def _insert_images_in_summary(self, summary_text, images):
        """
        Insert images at logical places in the summary
        """
        if not images:
            return summary_text
        
        # Split summary into paragraphs
        paragraphs = summary_text.split('\n\n')
        
        # Insert first image after first paragraph
        if len(paragraphs) >= 1 and len(images) >= 1:
            image_1 = images[0]
            image_text = f"\n\n[Chart: {image_1['title']}]\n{image_1['url']}\n"
            paragraphs.insert(1, image_text)
        
        # Insert second image in middle or at end
        if len(paragraphs) >= 3 and len(images) >= 2:
            image_2 = images[1]
            image_text = f"\n\n[Chart: {image_2['title']}]\n{image_2['url']}\n"
            middle_pos = len(paragraphs) // 2
            paragraphs.insert(middle_pos, image_text)
        
        return '\n\n'.join(paragraphs)
    
    def _create_fallback_formatted_content(self):
        """
        Create fallback formatted content when no summary is available
        """
        return {
            'formatted_summary': "Unable to format content due to missing summary data.",
            'images': [],
            'timestamp': datetime.now().isoformat(),
            'original_summary': '',
            'status': 'fallback'
        }
    
    def _create_error_formatted_content(self, error_message):
        """
        Create error formatted content when formatting fails
        """
        return {
            'formatted_summary': f"Error formatting content: {error_message}",
            'images': [],
            'timestamp': datetime.now().isoformat(),
            'original_summary': '',
            'status': 'error',
            'error': error_message
        }
