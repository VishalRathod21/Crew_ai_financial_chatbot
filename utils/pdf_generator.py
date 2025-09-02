"""
PDF Generator Utility - Creates comprehensive PDF reports with multi-language support
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import requests
from PIL import Image as PILImage
import io
import logging

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self):
        self.output_dir = "output"
        self.styles = getSampleStyleSheet()
        self._setup_output_directory()
        self._setup_styles()
    
    def _setup_output_directory(self):
        """
        Ensure output directory exists
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _setup_styles(self):
        """
        Setup custom styles for PDF generation
        """
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.lightblue,
            borderPadding=5
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            firstLineIndent=0,
            leftIndent=0
        )
        
        # Multi-language style for non-Latin scripts
        self.multilang_style = ParagraphStyle(
            'MultiLang',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=0,  # Will be adjusted per language
            rightIndent=0,
            leftIndent=0
        )
    
    def create_report(self, pdf_data):
        """
        Create a comprehensive PDF report with English content
        """
        logger.info("Generating PDF report...")
        
        try:
            # Generate filename with timestamp
            timestamp = pdf_data.get('timestamp', datetime.now().strftime("%Y%m%d_%H%M%S"))
            filename = f"financial_market_summary_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build PDF content
            story = []
            
            # Add title
            title = pdf_data.get('title', 'Financial Market Summary')
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 20))
            
            # Add generation timestamp
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 30))
            
            # Add formatted English content
            self._add_formatted_content(story, pdf_data)
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report created successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise
    
    def _add_formatted_content(self, story, pdf_data):
        """
        Add the formatted English content to the PDF
        """
        # Section header
        story.append(Paragraph("📈 Financial Market Summary", self.heading_style))
        story.append(Spacer(1, 20))
        
        # Formatted content
        formatted_summary = pdf_data.get('formatted_summary', '')
        if formatted_summary:
            # Split content by image placeholders and add them properly
            content_parts = self._split_content_by_images(formatted_summary)
            
            for part in content_parts:
                if part.startswith('[Chart:'):
                    # This is an image placeholder
                    self._add_image_placeholder(story, part)
                else:
                    # This is text content
                    if part.strip():
                        # Split into paragraphs
                        paragraphs = part.split('\n\n')
                        for para in paragraphs:
                            if para.strip():
                                story.append(Paragraph(para.strip(), self.normal_style))
                                story.append(Spacer(1, 12))
        
        # Add images from data
        images = pdf_data.get('images', [])
        if images:
            story.append(Spacer(1, 20))
            story.append(Paragraph("📊 Related Charts and Graphs", self.heading_style))
            story.append(Spacer(1, 15))
            
            for img in images:
                self._add_image_to_story(story, img)
    
    
    def _split_content_by_images(self, content):
        """
        Split content by image placeholders
        """
        import re
        
        # Find image placeholders like [Chart: Title]
        parts = re.split(r'(\[Chart:.*?\])', content)
        return [part for part in parts if part.strip()]
    
    def _add_image_placeholder(self, story, placeholder_text):
        """
        Add an image placeholder to the story
        """
        story.append(Paragraph(f"<i>{placeholder_text}</i>", self.styles['Italic']))
        story.append(Spacer(1, 8))
    
    def _add_image_to_story(self, story, image_data):
        """
        Add an actual image to the PDF story
        """
        try:
            url = image_data.get('url', '')
            title = image_data.get('title', 'Chart')
            
            if not url or 'placeholder' in url.lower():
                # Skip placeholder images
                story.append(Paragraph(f"📊 {title} (Chart not available)", self.styles['Italic']))
                story.append(Spacer(1, 15))
                return
            
            # Download and process image
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Convert to PIL Image
            img_data = io.BytesIO(response.content)
            pil_img = PILImage.open(img_data)
            
            # Resize if necessary
            max_width = 400
            max_height = 300
            
            if pil_img.width > max_width or pil_img.height > max_height:
                pil_img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
            
            # Convert back to bytes
            img_buffer = io.BytesIO()
            pil_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Create ReportLab Image
            rl_img = Image(img_buffer, width=pil_img.width, height=pil_img.height)
            
            # Add image and title
            story.append(Paragraph(f"📊 {title}", self.styles['Italic']))
            story.append(Spacer(1, 8))
            story.append(rl_img)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            logger.warning(f"Failed to add image {image_data.get('title', 'Unknown')}: {str(e)}")
            story.append(Paragraph(f"📊 {title} (Image could not be loaded)", self.styles['Italic']))
            story.append(Spacer(1, 15))
    
    def create_sample_report(self):
        """
        Create a sample report for testing purposes
        """
        sample_data = {
            'title': 'Sample Financial Market Summary',
            'formatted_summary': 'This is a sample financial market summary for testing purposes.\n\nMarket performance was mixed today with technology stocks showing strength.\n\n[Chart: Stock Market Performance]\nOverall market sentiment remains cautiously optimistic.',
            'images': [
                {
                    'url': 'https://via.placeholder.com/400x300/0066cc/ffffff?text=Sample+Chart',
                    'title': 'Sample Market Chart'
                }
            ],
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        return self.create_report(sample_data)
