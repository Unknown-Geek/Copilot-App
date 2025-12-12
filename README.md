# Code Multilingual Documentation Generator

A comprehensive solution for automated code documentation generation and multilingual translation. This project consists of a Flask backend API, VS Code extension, and utilizes free, open-source language processing libraries for sentiment analysis and translation capabilities.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [VS Code Extension](#vs-code-extension)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

### Documentation Generation

- Automatic code analysis and documentation generation
- Support for multiple programming languages (Python, JavaScript, Java, C++, Go, Rust, TypeScript)
- Code complexity metrics and analysis using Radon
- Syntax highlighting with Pygments
- Multiple export formats: Markdown, HTML, JSON, PDF, DOCX
- Template-based documentation generation

### Translation Services

- Multilingual documentation translation using deep-translator
- Support for 11 languages: Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Hindi, Russian
- Automatic language detection using langdetect
- Confidence scoring for translations
- Batch translation capabilities

### Code Analysis

- Sentiment analysis using TextBlob and NLTK VADER
- Language detection
- Code metrics and complexity scoring
- Function and class counting
- Line count statistics

### Security Features

- JWT-based authentication
- Rate limiting and request throttling
- OAuth integration with GitHub
- Secure session management
- Input validation and sanitization

### GitHub Integration

- Repository information retrieval
- OAuth authentication flow
- Repository scanning and analysis
- Batch processing support

## Architecture

## Architecture

The project follows a modular architecture with three main components:

```
copilot-app/
├── backend/              # Flask REST API server
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── models/          # Data models
│   ├── utils/           # Utilities and middleware
│   └── tests/           # Test suite
├── vscode-extension/     # VS Code extension
│   ├── src/             # TypeScript source
│   └── dist/            # Compiled extension
└── frontend/            # React frontend (optional)
```

### Backend Services

- **Documentation Generator**: Code parsing and documentation generation
- **Translator Service**: Multilingual translation using deep-translator
- **Sentiment Service**: Code sentiment analysis using TextBlob/NLTK
- **Code Analyzer**: Metrics and complexity analysis using Radon
- **GitHub Service**: Repository integration and OAuth
- **Export Services**: Multiple format exporters (Markdown, HTML, JSON, PDF, DOCX)

### VS Code Extension

- Command palette integration
- Context menu actions
- Keyboard shortcuts
- Real-time documentation preview
- Configurable settings
- Status bar indicators

## Installation

### Prerequisites

**Option 1: Docker (Recommended)**
- Docker 20.10 or higher
- Docker Compose 2.0 or higher

**Option 2: Manual Installation**
- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Git

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/copilot-app.git
cd copilot-app
```

2. Create environment file:
```bash
cp .env.docker.example .env
# Edit .env with your settings (optional for basic usage)
```

3. Build and start services:
```bash
# Using Docker Compose
docker-compose up -d

# Or using Make (if available)
make up
```

4. Access the backend:
```
Backend API: http://localhost:5001
Health Check: http://localhost:5001/api/config
```

**Docker Commands:**
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose build

# Development mode (with hot reload)
docker-compose -f docker-compose.dev.yml up

# Run tests in container
docker-compose exec backend python -m pytest tests/ -v
```

### Manual Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/copilot-app.git
cd copilot-app
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv backend/venv
backend/venv/Scripts/activate

# Linux/macOS
python -m venv backend/venv
source backend/venv/bin/activate
```

3. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Download required NLTK data:
```bash
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

5. Set up environment variables (optional):
```bash
# Create .env file in backend directory
cp .env.example .env
# Edit .env with your configuration
```

6. Start the backend server:
```bash
python server.py
```

The server will start on `http://localhost:5001`

### VS Code Extension Setup

1. Navigate to the extension directory:

```bash
cd vscode-extension
```

2. Install dependencies:

```bash
npm install
```

3. Compile the extension:

```bash
npm run compile
```

4. Install the extension:
   - Press `F5` to open Extension Development Host
   - Or package and install: `vsce package` then install the .vsix file

## Usage

### Using the Backend API

#### Generate Documentation

```bash
curl -X POST http://localhost:5001/api/analyze/documentation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello World\")",
    "language": "python",
    "title": "Hello World Function",
    "description": "A simple greeting function"
  }'
```

#### Translate Text

```bash
curl -X POST http://localhost:5001/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a Python function",
    "target_language": "es"
  }'
```

#### Analyze Code Sentiment

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "# This is great code\ndef excellent_function():\n    pass",
    "language": "python"
  }'
```

### Using the VS Code Extension

#### Commands

Access commands via Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`):

1. **DocGen: Generate Documentation**

   - Generates documentation for the current file or selected code
   - Shortcut: `Ctrl+K Ctrl+G` (Windows/Linux) or `Cmd+K Cmd+G` (macOS)

2. **DocGen: Translate Documentation**

   - Translates generated documentation to target language
   - Select from 11 supported languages

3. **DocGen: Analyze Code**

   - Performs sentiment analysis on code

4. **DocGen: Export Documentation**
   - Exports documentation in various formats

#### Context Menu

Right-click in the editor to access:

- Generate Documentation
- Analyze Code

#### Configuration

Configure the extension in VS Code settings:

```json
{
  "docgen.backendUrl": "http://localhost:5001",
  "docgen.defaultTargetLanguage": "es",
  "docgen.defaultExportFormat": "markdown",
  "docgen.showStatusBar": true
}
```

## API Reference

### Endpoints

#### POST /api/analyze/documentation/generate

Generate documentation for source code.

**Request Body:**

```json
{
  "code": "string (required)",
  "language": "string (required)",
  "title": "string (optional)",
  "description": "string (optional)",
  "template": "string (optional, default: 'default')",
  "format": "string (optional, default: 'markdown')"
}
```

**Response:**

```json
{
  "status": "success",
  "documentation": "string",
  "format": "markdown",
  "template": "default"
}
```

#### POST /api/translate

Translate text to target language.

**Request Body:**

```json
{
  "text": "string (required)",
  "target_language": "string (required)"
}
```

**Response:**

```json
{
  "status": "success",
  "translated_text": "string",
  "detected_language": "string",
  "confidence": 0.99
}
```

#### POST /api/analyze

Analyze code sentiment and metrics.

**Request Body:**

```json
{
  "code": "string (required)",
  "language": "string (required)"
}
```

**Response:**

```json
{
  "sentiment": "positive",
  "confidence_scores": {
    "positive": 0.8,
    "neutral": 0.15,
    "negative": 0.05
  },
  "metrics": {}
}
```

### Supported Languages

**Programming Languages:**

- Python
- JavaScript/TypeScript
- Java
- C++
- Go
- Rust

**Translation Languages:**

- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)
- Russian (ru)

## VS Code Extension

### Installation from VSIX

1. Download the latest `.vsix` file from releases
2. Open VS Code
3. Go to Extensions (`Ctrl+Shift+X`)
4. Click on the `...` menu
5. Select "Install from VSIX..."
6. Choose the downloaded file

### Extension Features

- **Real-time Documentation Generation**: Generate documentation as you code
- **Multilingual Support**: Translate documentation to 11 languages
- **Code Analysis**: Sentiment analysis and metrics
- **Multiple Export Formats**: Markdown, HTML, JSON, PDF, DOCX
- **Customizable Templates**: Use built-in or custom templates
- **Status Bar Integration**: Quick access to documentation tools
- **Keyboard Shortcuts**: Fast workflow with shortcuts

## Configuration

### Backend Configuration

Environment variables can be set in a `.env` file:

```properties
# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Security
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-secret-key

# GitHub OAuth (optional)
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Extension Configuration

Settings available in VS Code:

- `docgen.backendUrl`: Backend API URL (default: `http://localhost:5001`)
- `docgen.defaultTargetLanguage`: Default translation language (default: `es`)
- `docgen.defaultExportFormat`: Default export format (default: `markdown`)
- `docgen.showStatusBar`: Show status bar item (default: `true`)

## Development

### Backend Development

1. Install development dependencies:

```bash
pip install pytest pytest-cov requests-mock
```

2. Run tests:

```bash
cd backend
python -m pytest tests/ -v
```

3. Run with auto-reload:

```bash
python server.py
# Server runs in debug mode with auto-reload
```

### Docker Development

**Development Mode:**
```bash
# Start with hot reload
docker-compose -f docker-compose.dev.yml up

# Access running container
docker-compose exec backend bash

# View logs
docker-compose logs -f backend
```

**Using Makefile:**
```bash
# Build images
make build

# Start production
make prod

# Start development
make dev

# Run tests
make test

# View logs
make logs

# Clean everything
make clean
```

### Extension Development

1. Install dependencies:
```bash
cd vscode-extension
npm install
```

2. Start watch mode:
```bash
npm run watch
```

3. Debug extension:
   - Press `F5` in VS Code
   - This opens Extension Development Host
   - Test your changes in the new window

4. Package extension:
```bash
npm run package
# Creates .vsix file in the directory
```

## Deployment

### Deploy with Docker

**Production Deployment:**

1. Build production image:
```bash
docker-compose build
```

2. Run in production:
```bash
docker-compose up -d
```

3. Configure reverse proxy (nginx/traefik):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Deploy to Render (Free Tier)

1. Push to GitHub with all Docker files

2. Connect repository to Render:
   - Go to https://render.com
   - Create new Web Service
   - Connect GitHub repository
   - Render auto-detects `render.yaml`

3. Configuration (auto-detected from render.yaml):
   - **Environment**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Build Command**: Auto
   - **Start Command**: Auto

4. Environment variables (set in Render dashboard):
   - `JWT_SECRET_KEY`: Generate secure key
   - `SECRET_KEY`: Generate secure key

**Render Features:**
- Automatic HTTPS
- Custom domains
- Auto-deploy on git push
- Free SSL certificates

### Deploy to Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

3. Configure environment variables in Railway dashboard

### Deploy to Heroku

1. Create Heroku app:
```bash
heroku create your-app-name
heroku stack:set container
```

2. Push to Heroku:
```bash
git push heroku main
```

3. Set environment variables:
```bash
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set SECRET_KEY=your-secret-key
```

## Testing

### Backend Tests

The backend includes comprehensive test coverage:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_api.py -v
```

**Test Coverage:**

- API endpoint tests
- Service layer tests
- Security tests
- Documentation generation tests
- Translation tests
- GitHub integration tests

### Current Test Status

- **Total Tests**: 37
- **Passing**: 28
- **Failing**: 9 (outdated Azure-related tests)
- **Coverage**: Core functionality fully tested

## Dependencies

### Backend Dependencies

**Core:**

- Flask 2.0.3 - Web framework
- Flask-CORS 3.0.10 - CORS support
- Flask-JWT-Extended 4.5.2 - JWT authentication
- Flask-Limiter 3.5.0 - Rate limiting

**Analysis & Processing:**

- Radon 6.0.1 - Code metrics
- Pygments 2.16.1 - Syntax highlighting
- TextBlob 0.17.1 - Sentiment analysis
- NLTK 3.8.1 - Natural language processing
- deep-translator 1.11.4 - Translation
- langdetect 1.0.9 - Language detection

**Export:**

- Markdown 3.0+ - Markdown processing
- python-docx 0.8.11 - DOCX generation
- ReportLab 4.0.4 - PDF generation

**Testing:**

- pytest 7.3.1 - Testing framework
- pytest-cov 4.1.0 - Coverage reporting
- requests-mock 1.11.0 - HTTP mocking

### Extension Dependencies

- TypeScript 5.3.2
- esbuild 0.19.8
- @types/vscode 1.85.0
- @types/node 20.10.0

## Project Structure

```
backend/
├── routes/
│   ├── __init__.py
│   └── api.py                    # API endpoints
├── services/
│   ├── __init__.py
│   ├── documentation_generator.py # Doc generation
│   ├── translator.py             # Translation service
│   ├── azure_service.py          # Sentiment analysis
│   ├── code_analyzer.py          # Code metrics
│   ├── github_service.py         # GitHub integration
│   └── export_services.py        # Export handlers
├── models/
│   ├── __init__.py
│   └── documentation.py          # Data models
├── utils/
│   ├── __init__.py
│   ├── validators.py             # Input validation
│   ├── middleware.py             # Middleware
│   ├── cache_manager.py          # Caching
│   └── complexity_analyzer.py    # Complexity analysis
├── tests/
│   ├── conftest.py              # Test configuration
│   ├── test_api.py              # API tests
│   ├── test_documentation_*.py  # Doc tests
│   └── test_*.py                # Various test files
├── config.py                     # Configuration
├── security.py                   # Security & auth
├── server.py                     # Main server
└── requirements.txt              # Python dependencies

vscode-extension/
├── src/
│   ├── extension.ts             # Main extension
│   ├── api.ts                   # API client
│   ├── webview.ts               # Preview webview
│   └── types.ts                 # Type definitions
├── .vscode/
│   ├── launch.json              # Debug config
│   └── tasks.json               # Build tasks
├── dist/                        # Compiled output
├── package.json                 # Extension manifest
└── tsconfig.json                # TypeScript config
```

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use TypeScript strict mode for extension code
- Write tests for new features
- Update documentation as needed
- Maintain code coverage above 75%

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

This project uses the following open-source libraries:

- TextBlob and NLTK for sentiment analysis
- deep-translator for multilingual translation
- Radon for code complexity metrics
- Pygments for syntax highlighting
- Flask ecosystem for web framework
- ReportLab and python-docx for document generation

## Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Check existing documentation
- Review closed issues for solutions

## Changelog

### Version 1.0.0 (Current)

**Features:**

- Complete documentation generation system
- Multilingual translation (11 languages)
- Code sentiment analysis
- VS Code extension with full integration
- Multiple export formats (Markdown, HTML, JSON, PDF, DOCX)
- GitHub OAuth integration
- Rate limiting and security features
- Comprehensive test suite

**Tech Stack:**

- Backend: Flask, Python 3.8+
- Extension: TypeScript, VS Code Extension API
- Services: Free/open-source libraries (no API keys required)
- Testing: pytest with 75%+ coverage

---

**Note**: This project previously used Azure Cognitive Services but has been migrated to free, open-source alternatives (TextBlob, NLTK, deep-translator) for accessibility and cost-effectiveness.
