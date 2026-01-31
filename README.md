# Economic Survey 2025-26 MCP Server

A Model Context Protocol (MCP) server that provides AI-powered access to India's Economic Survey 2025-26. This server allows AI assistants like Claude to interact with the complete economic survey document through structured tools.

## 🎯 Features

The MCP server exposes 5 powerful tools:

### 1. **get_document_summary**
Get an executive summary of the entire Economic Survey including:
- Key highlights (7%+ GDP growth, credit upgrades, US tariffs)
- Three scenarios for 2026 with probabilities
- Central message and overall structure
- Total pages and chapter count

### 2. **get_key_highlights**
Get structured key highlights organized by categories:
- Economic Growth
- Fiscal Consolidation
- External Challenges
- Credit Ratings
- Monetary Policy
- Strategic Priorities

### 3. **list_chapters**
List all 17 chapters with:
- Chapter number and title
- Subtitle/theme
- Page ranges
- Quick reference guide

### 4. **get_chapter_summary**
Get a concise summary of any specific chapter (1-17):
- Chapter title and subtitle
- Page range
- Executive summary
- Content length

### 5. **get_chapter_content**
Get the complete text content of any chapter:
- Full chapter text extracted from PDF
- Configurable maximum length
- Original formatting preserved

## 📖 Document Coverage

**Economic Survey 2025-26** - Government of India
- **Total Pages**: 739
- **Total Chapters**: 17

### Chapter List:
1. State of the Economy - "Frontier"
2. Fiscal Policy - "Through Credible Consolidation"
3. Monetary & Financial Sector - "Refining the Regulatory Touch"
4. External Sector - "Playing the Long Game"
5. Prices & Inflation - "Tamed and Anchored"
6. Agriculture - "Productivity & Food Security"
7. Services Sector - "From Stability to New Frontiers"
8. Manufacturing - "And Global Integration"
9. Infrastructure - "Connectivity, Capacity, Competitiveness"
10. Climate & Environment - "Resilient, Competitive, Development-Driven"
11. Human Development - "Education & Health"
12. Employment & Skills - "Skilling Right"
13. Social Inclusion - "Participation to Partnership"
14. Artificial Intelligence - "Forward" (Special Essay)
15. Urban Development - "Cities for Its Citizens" (Special Essay)
16. Strategic Autonomy - "Strategic Indispensability" (Special Essay)
17. State Capacity - "State, Private Sector & Citizens" (Special Essay)

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/anirudhyadavMS/economic-survey-mcp-server.git
cd economic-survey-mcp-server
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add the PDF file**
Place the Economic Survey PDF in the `data` directory:
```bash
mkdir data
# Copy your PDF file to: data/economic-survey-2025-26.pdf
```

## 📦 Project Structure

```
economic-survey-mcp-server/
├── server.py              # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
└── data/                 # PDF data directory
    └── economic-survey-2025-26.pdf  # Place PDF here
```

## 🔧 Configuration

### Claude Desktop Integration

To use this MCP server with Claude Desktop, add it to your configuration:

**On Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**On macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "economic-survey": {
      "command": "python",
      "args": ["C:/Users/YOUR_USERNAME/economic-survey-mcp-server/server.py"],
      "env": {}
    }
  }
}
```

Replace `YOUR_USERNAME` with your actual Windows username.

### Environment Variables

You can configure the PDF path via environment variable:
```bash
export PDF_PATH=/path/to/your/economic-survey-2025-26.pdf
```

## 💻 Usage Examples

Once configured with Claude Desktop, you can use natural language:

### Get Document Overview
```
"Give me a summary of the Economic Survey 2025-26"
```

### Get Chapter Summary
```
"Summarize Chapter 1 of the Economic Survey"
"What does Chapter 8 on Manufacturing cover?"
```

### Get Full Chapter Content
```
"Show me the complete content of Chapter 4 on External Sector"
"What's the full text of the AI chapter?"
```

### Get Key Highlights
```
"What are the key highlights from the Economic Survey?"
"Show me the important points organized by category"
```

### List All Chapters
```
"List all chapters in the Economic Survey"
"What chapters are covered in the document?"
```

## 🛠️ Development

### Running Tests
```bash
# Test the server
python server.py
```

### Debugging
Enable detailed logging by setting log level:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Adding New Tools
To add new tools, update the `@app.list_tools()` and `@app.call_tool()` functions in `server.py`.

## 📊 Technical Details

- **Protocol**: Model Context Protocol (MCP)
- **Language**: Python 3.10+
- **PDF Parser**: PyMuPDF (fitz)
- **Server Framework**: MCP Python SDK
- **Communication**: Standard I/O (stdio)

## 🔒 Security & Privacy

- The server runs locally on your machine
- No data is sent to external servers
- PDF content is processed locally
- All communication happens via standard I/O

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Government of India, Ministry of Finance for publishing the Economic Survey
- Anthropic for the Model Context Protocol specification
- PyMuPDF team for the excellent PDF parsing library

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions

## 🔄 Updates

The server will be updated as:
- New chapters or sections are added
- Bug fixes are needed
- New features are requested

## ⚠️ Disclaimer

This is an unofficial tool for educational and research purposes. For official information, refer to the Economic Survey 2025-26 published by the Government of India.

---

**Built with ❤️ for policy researchers, economists, students, and professionals studying India's economy**
