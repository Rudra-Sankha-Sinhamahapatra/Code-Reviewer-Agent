#  AI Code Reviewer Agent

An intelligent code review agent built with LangGraph, LangChain, and Google Gemini that automatically analyzes code repositories for quality, security vulnerabilities, and best practices.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-v0.0.15-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

##  Features

- **🔍 Comprehensive Code Analysis** - Analyzes code quality, complexity, and documentation
- **🔒 Security Vulnerability Detection** - Identifies SQL injection, hardcoded secrets, and unsafe functions
- **📊 Pattern Recognition** - Detects anti-patterns and good coding practices
- **🌐 Multi-Language Support** - Works with Python, JavaScript, TypeScript, Rust, Java, and more
- **📈 Detailed Reporting** - Provides actionable feedback with severity levels
- **🔗 GitHub Integration** - Directly analyzes GitHub repositories
- **⚡ Interactive CLI** - Beautiful command-line interface with Rich

##  Tech Stack

- **🧠 AI Framework**: LangGraph + LangChain
- **🤖 LLM**: Google Gemini 2.0 Flash
- **🐍 Language**: Python 3.9+
- **🎨 UI**: Rich (Terminal UI)
- **🔗 Integration**: GitHub API via PyGithub
- **⚙️ Environment**: python-dotenv

##  Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Rudra-Sankha-Sinhamahapatra/Code-Reviewer-Agent.git
cd Code-Reviewer-Agent
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation (you should see (venv) in your terminal)
which python  # Should point to venv/bin/python
```

### 3. Install Dependencies

```bash
# Option 1: Install from requirements.txt (Recommended)
pip install -r requirements.txt

# Option 2: Install manually
pip install langgraph==0.0.15 langchain==0.1.0 langchain-google-genai==0.0.5 python-dotenv==1.0.0 rich==13.7.0 PyGithub==2.7.0
```

## 🔑 Environment Setup

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
touch .env
```

### 2. Get Google Gemini API Key

1. **Visit Google AI Studio**: Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. **Sign in** with your Google account
3. **Create API Key**: Click "Create API Key" button
4. **Copy the key**: Save it securely (it won't be shown again)
5. **Add to .env**:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

### 3. Get GitHub Personal Access Token

1. **Go to GitHub Settings**: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. **Click "Generate new token"** → **"Generate new token (classic)"**
3. **Configure Token**:
   - **Note**: `AI Code Reviewer Token`
   - **Expiration**: Choose your preference
   - **Select Scopes** (Required permissions):
     - ✅ `repo` - Full control of private repositories
     - ✅ `read:org` - Read org and team membership
     - ✅ `workflow` (optional) - Update GitHub Action workflows
4. **Generate Token** and copy it
5. **Add to .env**:
   ```bash
   GITHUB_TOKEN=your_github_token_here
   ```

### 4. Complete .env File

Your `.env` file should look like this:

```bash
# AI Code Reviewer Environment Variables
GOOGLE_API_KEY= gemini api key
GITHUB_TOKEN= github pat
```

## 🎮 Usage

### Run the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or activate script for your OS

# Run the AI Code Reviewer
python main.py
```

### Available Options

```
================================================================================
AI Code Reviewer
================================================================================

Choose an option:
1. Review a GitHub repository
2. Review sample code
3. Exit
```

#### Option 1: GitHub Repository Review
- Enter repository name (e.g., `username/repo-name`)
- Enter branch name (default: `main`)
- Get comprehensive analysis of your repository

#### Option 2: Sample Code Review
- Reviews predefined code samples with various issues
- Perfect for testing and understanding the tool's capabilities

## 📊 Sample Output

```
🔍 ANALYSIS RESULTS:
• Total Issues: 13
• Critical: 2 | High: 2 | Medium: 4 | Low: 5

📂 BY CATEGORY:
• Security Issues: 3
• Best Practice Issues: 4
• Code Smells: 3
• Other Issues: 3

🎯 GOOD PATTERNS FOUND: 8

🚨 TOP PRIORITY ISSUES:
1. 🔴 example.py:17 - SQL injection vulnerability detected
2. 🔴 example.py:18 - Use parameterized queries
3. 🟠 example.py:13 - Missing function definition
4. 🟠 main.py:36 - Unsafe code execution detected
5. 🟡 example.py:7 - Global variables detected
```

## 🔄 Workflow Architecture

Our AI Code Reviewer follows this workflow:

```
┌─────────────────┐
│  Code Changes   │
│   (GitHub)      │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ analyze_changes │  ← AI analyzes code quality, complexity, docs
└─────────┬───────┘
          ▼
┌─────────────────┐
│detect_patterns  │  ← Finds anti-patterns and good practices
└─────────┬───────┘
          ▼
┌─────────────────┐
│security_check   │  ← Scans for vulnerabilities and secrets
└─────────┬───────┘
          ▼
┌─────────────────┐
│generate_feedback│  ← Creates comprehensive report
└─────────┬───────┘
          ▼
┌─────────────────┐
│   Final Report  │
│  (Categorized)  │
└─────────────────┘
```

### Workflow Components

1. **📥 Code Analysis**: AI-powered analysis using Google Gemini
2. **🔍 Pattern Detection**: Multi-language pattern recognition
3. **🔒 Security Scanning**: Vulnerability and secret detection
4. **📋 Report Generation**: Comprehensive feedback with priorities

## 🧪 Example Analysis

The tool analyzes various aspects of your code:

### Security Issues
- SQL injection vulnerabilities
- Hardcoded API keys and secrets
- Unsafe code execution functions
- Path traversal vulnerabilities

### Code Quality
- Code complexity and organization
- Naming conventions
- Documentation quality
- Error handling patterns

### Best Practices
- Resource management
- API design patterns
- Testability improvements
- Performance considerations

## 🛠️ Project Structure

```
ai-code-reviewer/
├── main.py              # Main application entry point
├── nodes.py             # LangGraph workflow nodes
├── utils.py             # Data models and utility functions
├── example.py           # Sample code for testing
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔧 Configuration

### Supported File Types
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`)
- And more...

### Analysis Limits
- **Max files per review**: 5 files
- **Max file size**: 2000 characters per file
- **Timeout**: 30 seconds per AI request

## 🐛 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError"**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**2. "API Key Error"**
```bash
# Check .env file exists and has correct format
cat .env
# Verify API key is valid at Google AI Studio
```

**3. "GitHub Token Error"**
```bash
# Verify token has correct permissions
# Check repository name format: username/repo-name
```

**4. "JSON Parsing Failed"**
- This is usually temporary - try again
- The tool has fallback mechanisms to handle this

### Debug Mode

For detailed debugging, check the terminal output for:
- Raw AI response length
- JSON parsing status
- Security scan results
- Pattern detection findings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph**: For the workflow orchestration framework
- **Google Gemini**: For the powerful AI analysis capabilities
- **Rich**: For the beautiful terminal interface
- **PyGithub**: For seamless GitHub integration

## 📧 Contact

- **Author**: Rudra Sankha Sinhamahapatra
- **GitHub**: [@Rudra-Sankha-Sinhamahapatra](https://github.com/Rudra-Sankha-Sinhamahapatra)
- **Repository**: [Code-Reviewer-Agent](https://github.com/Rudra-Sankha-Sinhamahapatra/Code-Reviewer-Agent)

---

**⭐ Star this repository if it helped you improve your code quality!**
