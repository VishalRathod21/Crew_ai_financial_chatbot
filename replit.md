# CrowdWisdomTrading AI Agent - Financial Market Summary Generator

## Overview

This is a CrewAI-based automation system that generates comprehensive daily financial market summaries in English. The system orchestrates specialized AI agents to search for real-time US financial market news, create summaries, enhance content with visual elements, and distribute reports via Telegram and PDF format.

The application follows a sequential agent workflow where each agent has a single responsibility: searching for financial news, summarizing content, formatting with charts/images, and distributing the final reports.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Agent-Based Architecture
The system uses CrewAI to orchestrate four specialized agents in a sequential workflow:

1. **Search Agent** - Fetches real-time US financial market news using Tavily/Serper APIs from the past hour
2. **Summary Agent** - Creates concise market summaries under 500 words using LiteLLM
3. **Formatting Agent** - Enhances content by finding and embedding 2 relevant financial charts/images
4. **Send Agent** - Distributes English reports via Telegram and generates local PDF copies

### LLM Integration
- **Primary Provider**: LiteLLM for flexible model access (supports OpenAI, Groq, Gemini)
- **Default Model**: GPT-3.5-turbo with fallback options
- **Usage**: Content summarization and content enhancement

### Data Flow
- Sequential agent execution using CrewAI's Process system
- Context passing between agents to maintain data continuity
- Error handling and logging at each stage
- Structured data extraction from agent outputs

### Content Management
- **PDF Generation**: Uses ReportLab for English PDF reports with custom styling
- **Image Processing**: PIL for chart/image handling and optimization
- **File Organization**: Structured output directory with timestamp-based naming

### Logging System
- Structured logging with rotating file handlers
- Multiple log levels and formatters for development and production
- Centralized logger configuration with module-specific tracking

## External Dependencies

### APIs and Services
- **Tavily API**: Primary search service for financial news aggregation
- **Serper API**: Alternative search service with Google integration
- **LiteLLM API**: Multi-provider LLM access for text processing
- **Telegram Bot API**: Message distribution and report delivery
- **Groq API**: Optional additional summarization capabilities

### Python Libraries
- **CrewAI**: Agent orchestration and workflow management
- **LiteLLM**: LLM provider abstraction layer
- **ReportLab**: PDF generation with multi-language support
- **PIL (Pillow)**: Image processing and optimization
- **Requests**: HTTP client for API interactions
- **Python-dotenv**: Environment variable management

### Environment Configuration
Required environment variables:
- `TAVILY_API_KEY`: For financial news search
- `TELEGRAM_BOT_TOKEN`: For report distribution
- `TELEGRAM_CHAT_ID`: Target chat for message delivery
- `LITELLM_API_KEY`: For LLM access
- `SERPER_API_KEY`: Optional alternative search
- `GROQ_API_KEY`: Optional additional processing
- `LITELLM_MODEL`: Configurable model selection

### File System Requirements
- Local storage for PDF output and logs
- Image caching for chart/visual content
- Rotating log file management
- Organized directory structure for reports