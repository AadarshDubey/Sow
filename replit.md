# Overview

The SoW Audit Assistant is an AI-powered contract analysis tool specifically designed for auditing Statement of Work (SoW) documents in fixed-price projects. The application helps identify scope creep risks, vague language, missing sections, and quality issues before contracts are finalized. It provides comprehensive analysis including vagueness detection, risk assessment, quality checking, and generates detailed audit reports with redline suggestions.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application with wide layout configuration
- **UI Components**: Sidebar for file upload and processing options, main content area for results display
- **Visualization**: Plotly for interactive charts and graphs displaying audit results
- **State Management**: Streamlit session state for persisting audit results and document content across interactions

## Backend Architecture
- **Modular Design**: Separate classes for each major functionality (DocumentParser, SectionValidator, VaguenessDetector, RiskAssessor, QualityChecker, ReportGenerator)
- **Document Processing Pipeline**: Sequential processing through multiple analysis agents
- **AI Integration**: Google Gemini API client for enhanced analysis capabilities
- **Structured Data Models**: Pydantic models for type-safe API responses from AI services

## Document Processing Architecture
- **Multi-format Support**: Handles PDF (PyPDF2), DOCX (python-docx), and TXT files
- **Text Extraction**: Format-specific parsers with error handling and validation
- **Section Detection**: Regex-based pattern matching for identifying document sections
- **Structure Analysis**: Hierarchical parsing of headings, lists, and content organization

## Analysis Engine Architecture
- **Section Validation**: Template-based checking against required SoW sections (objectives, scope, deliverables, timeline, acceptance criteria, assumptions, pricing, change control)
- **Vagueness Detection**: Multi-layered pattern matching for ambiguous language, vague quantities, and scope expansion risks
- **Risk Assessment**: Categorized risk patterns (high/medium/low) with business impact analysis
- **Quality Checking**: Grammar, spelling, consistency, and professionalism assessment

## AI Enhancement Architecture
- **Gemini Integration**: Google Generative AI client for advanced analysis
- **Structured Responses**: Pydantic models ensure consistent AI output format
- **Batch Processing**: Efficient handling of multiple analysis items
- **Fallback Strategy**: Graceful degradation when AI services are unavailable

## Report Generation Architecture
- **Multi-section Reports**: Executive summary, detailed findings, risk analysis, quality assessment, recommendations, and redline suggestions
- **Export Capabilities**: Structured text reports with potential for PDF/Word export
- **Customizable Output**: Optional redline suggestions and detailed appendices

# External Dependencies

## AI Services
- **Google Gemini API**: Advanced natural language processing for enhanced vagueness detection, risk assessment, and quality analysis
- **Authentication**: API key-based authentication via environment variables (GOOGLE_API_KEY or GEMINI_API_KEY)

## Document Processing Libraries
- **PyPDF2**: PDF text extraction and processing
- **python-docx**: Microsoft Word document parsing and text extraction
- **Built-in Text Processing**: Native Python text file handling

## Web Framework and UI
- **Streamlit**: Primary web application framework with built-in state management
- **Plotly**: Interactive data visualization for audit results and metrics
- **Pandas**: Data manipulation and analysis for structured results

## Data Validation and Modeling
- **Pydantic**: Type validation and structured data models for AI responses
- **JSON**: Data serialization and configuration management

## Logging and Error Handling
- **Python Logging**: Application-wide logging configuration
- **Exception Handling**: Comprehensive error handling across all modules

## Development and Runtime
- **Python Standard Library**: Core functionality including regex, datetime, collections, and I/O operations
- **Environment Variables**: Configuration management for API keys and settings