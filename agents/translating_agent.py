"""
Translating Agent - Translates content to Hindi, Arabic, and Hebrew
"""

import os
from datetime import datetime
from crewai import Agent, Task
from litellm import completion
import logging

logger = logging.getLogger(__name__)

class TranslatingAgent:
    def __init__(self):
        self.litellm_api_key = os.getenv('LITELLM_API_KEY')
        self.model = os.getenv('LITELLM_MODEL', 'gpt-3.5-turbo')
        
        self.agent = Agent(
            role='Multi-language Translator',
            goal='Translate financial market summaries into Hindi, Arabic, and Hebrew while maintaining formatting',
            backstory='You are an expert linguist specializing in financial terminology '
                     'across multiple languages. You ensure accurate translation while '
                     'preserving the technical accuracy and formatting of financial reports.',
            verbose=True,
            allow_delegation=False
        )
        
        self.task = Task(
            description='Translate the formatted financial market summary into Hindi, Arabic, '
                       'and Hebrew languages. Maintain all formatting including image placeholders '
                       'and ensure financial terms are accurately translated. Preserve the '
                       'professional tone and technical accuracy.',
            expected_output='Complete translations of the market summary in Hindi, Arabic, and Hebrew '
                          'with preserved formatting and accurate financial terminology.',
            agent=self.agent,
            execution_callback=self.translate_content
        )
        
        self.target_languages = {
            'hindi': 'हिन्दी',
            'arabic': 'العربية',
            'hebrew': 'עברית'
        }
    
    def translate_content(self, context=None):
        """
        Translate the formatted content into multiple languages
        """
        logger.info("Starting translation process...")
        
        try:
            # Extract formatted content from context
            formatted_data = self._extract_formatted_data(context)
            
            if not formatted_data:
                logger.warning("No formatted content available for translation")
                return self._create_fallback_translations()
            
            formatted_summary = formatted_data.get('formatted_summary', '')
            images = formatted_data.get('images', [])
            
            # Translate to each target language
            translations = {}
            
            for lang_code, lang_name in self.target_languages.items():
                try:
                    logger.info(f"Translating to {lang_name}...")
                    translation = self._translate_to_language(formatted_summary, lang_code, lang_name)
                    translations[lang_code] = {
                        'language': lang_name,
                        'content': translation,
                        'images': images  # Images remain the same
                    }
                except Exception as e:
                    logger.error(f"Translation to {lang_name} failed: {str(e)}")
                    translations[lang_code] = {
                        'language': lang_name,
                        'content': f"Translation failed: {str(e)}",
                        'images': images,
                        'error': str(e)
                    }
            
            logger.info(f"Translation completed for {len(translations)} languages")
            return {
                'original_content': formatted_summary,
                'translations': translations,
                'timestamp': datetime.now().isoformat(),
                'images': images
            }
            
        except Exception as e:
            logger.error(f"Translation process failed: {str(e)}")
            return self._create_error_translations(str(e))
    
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
    
    def _translate_to_language(self, content, lang_code, lang_name):
        """
        Translate content to a specific language using LiteLLM
        """
        # Create translation prompt with financial context
        prompt = f"""
        You are a professional financial translator. Translate the following financial market summary 
        into {lang_name} ({lang_code}). 

        Important guidelines:
        1. Maintain all formatting including line breaks and image placeholders
        2. Preserve financial terms accuracy
        3. Keep the professional tone
        4. Do not translate image URLs or chart references - keep them as is
        5. Ensure cultural appropriateness while maintaining technical accuracy

        Content to translate:
        {content}

        Provide only the translated content, maintaining exact formatting.
        """
        
        try:
            response = completion(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                api_key=self.litellm_api_key,
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more consistent translation
            )
            
            translation = response.choices[0].message.content.strip()
            return translation
            
        except Exception as e:
            logger.error(f"LLM translation to {lang_name} failed: {str(e)}")
            return self._create_fallback_translation(content, lang_name)
    
    def _create_fallback_translation(self, original_content, lang_name):
        """
        Create a fallback translation when LLM translation fails
        """
        fallback_messages = {
            'हिन्दी': 'वित्तीय बाजार सारांश - अनुवाद सेवा अनुपलब्ध',
            'العربية': 'ملخص السوق المالي - خدمة الترجمة غير متاحة',
            'עברית': 'סיכום שוק פיננסי - שירות תרגום לא זמין'
        }
        
        fallback_message = fallback_messages.get(lang_name, 'Financial Market Summary - Translation service unavailable')
        
        return f"{fallback_message}\n\n[Original Content]\n{original_content}"
    
    def _create_fallback_translations(self):
        """
        Create fallback translations when no formatted content is available
        """
        translations = {}
        
        for lang_code, lang_name in self.target_languages.items():
            translations[lang_code] = {
                'language': lang_name,
                'content': 'No content available for translation.',
                'images': [],
                'status': 'fallback'
            }
        
        return {
            'original_content': '',
            'translations': translations,
            'timestamp': datetime.now().isoformat(),
            'images': [],
            'status': 'fallback'
        }
    
    def _create_error_translations(self, error_message):
        """
        Create error translations when translation process fails
        """
        translations = {}
        
        for lang_code, lang_name in self.target_languages.items():
            translations[lang_code] = {
                'language': lang_name,
                'content': f'Translation error: {error_message}',
                'images': [],
                'status': 'error',
                'error': error_message
            }
        
        return {
            'original_content': '',
            'translations': translations,
            'timestamp': datetime.now().isoformat(),
            'images': [],
            'status': 'error',
            'error': error_message
        }
