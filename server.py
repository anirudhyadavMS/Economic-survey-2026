"""
Economic Survey 2025-26 MCP Server

An MCP server that provides AI-powered access to India's Economic Survey 2025-26.
Offers tools to get summaries, key highlights, and chapter content.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("economic-survey-mcp")

# Server instance
app = Server("economic-survey-mcp")

# Global storage for parsed PDF content
pdf_data = {
    "metadata": {},
    "chapters": {},
    "full_text": [],
    "loaded": False
}

# PDF file path - configure this
PDF_PATH = Path(__file__).parent / "data" / "economic-survey-2025-26.pdf"

# Chapter definitions
CHAPTERS = {
    1: {"title": "State of the Economy", "subtitle": "Frontier", "pages": (2, 37)},
    2: {"title": "Fiscal Policy", "subtitle": "Through Credible Consolidation", "pages": (38, 78)},
    3: {"title": "Monetary & Financial Sector", "subtitle": "Refining the Regulatory Touch", "pages": (79, 144)},
    4: {"title": "External Sector", "subtitle": "Playing the Long Game", "pages": (145, 203)},
    5: {"title": "Prices & Inflation", "subtitle": "Tamed and Anchored", "pages": (204, 225)},
    6: {"title": "Agriculture", "subtitle": "Productivity & Food Security", "pages": (226, 258)},
    7: {"title": "Services Sector", "subtitle": "From Stability to New Frontiers", "pages": (259, 292)},
    8: {"title": "Manufacturing", "subtitle": "And Global Integration", "pages": (293, 341)},
    9: {"title": "Infrastructure", "subtitle": "Connectivity, Capacity, Competitiveness", "pages": (342, 376)},
    10: {"title": "Climate & Environment", "subtitle": "Resilient, Competitive, Development-Driven", "pages": (377, 418)},
    11: {"title": "Human Development", "subtitle": "Education & Health", "pages": (419, 466)},
    12: {"title": "Employment & Skills", "subtitle": "Skilling Right", "pages": (467, 512)},
    13: {"title": "Social Inclusion", "subtitle": "Participation to Partnership", "pages": (513, 548)},
    14: {"title": "Artificial Intelligence", "subtitle": "Forward (Special Essay)", "pages": (549, 587)},
    15: {"title": "Urban Development", "subtitle": "Cities for Its Citizens (Special Essay)", "pages": (588, 635)},
    16: {"title": "Strategic Autonomy", "subtitle": "Strategic Indispensability (Special Essay)", "pages": (636, 652)},
    17: {"title": "State Capacity", "subtitle": "State, Private Sector & Citizens (Special Essay)", "pages": (653, 680)}
}


def load_pdf():
    """Load and parse the PDF file"""
    global pdf_data

    if not PDF_PATH.exists():
        logger.error(f"PDF file not found at {PDF_PATH}")
        return False

    try:
        logger.info(f"Loading PDF from {PDF_PATH}")
        doc = fitz.open(str(PDF_PATH))

        # Extract metadata
        pdf_data["metadata"] = {
            "title": doc.metadata.get("title", "Economic Survey 2025-26"),
            "pages": doc.page_count,
            "author": doc.metadata.get("author", "Government of India")
        }

        # Extract content by chapters
        for chapter_id, chapter_info in CHAPTERS.items():
            start_page, end_page = chapter_info["pages"]
            chapter_text = []

            for page_num in range(start_page - 1, min(end_page, doc.page_count)):
                page = doc[page_num]
                text = page.get_text()
                chapter_text.append(text)

            pdf_data["chapters"][chapter_id] = {
                "id": chapter_id,
                "title": chapter_info["title"],
                "subtitle": chapter_info["subtitle"],
                "pages": chapter_info["pages"],
                "content": "\n".join(chapter_text)
            }

        doc.close()
        pdf_data["loaded"] = True
        logger.info(f"PDF loaded successfully: {pdf_data['metadata']['pages']} pages, {len(pdf_data['chapters'])} chapters")
        return True

    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        return False


def get_document_summary() -> str:
    """Get overall document summary"""
    summary = """
Economic Survey 2025-26 - Government of India

KEY HIGHLIGHTS:
• India achieved 7%+ GDP growth in 2025, the strongest macroeconomic performance in decades
• Credit rating upgrades from DBRS, S&P (BBB- to BBB - first upgrade in 20 years), and R&I
• US imposed 50% total tariffs (25% reciprocal + 25% penal) on Indian goods
• Fiscal deficit: 4.8% in FY25 (target 4.9%), FY26 target: 4.4%
• Rupee underperformed despite strong fundamentals due to geopolitical factors
• Power Gap Index: -4.0 (lowest in Asia - India operating below strategic potential)

THREE SCENARIOS FOR 2026:
1. Managed Disorder (40-45% probability): Minor shocks escalate, requires active intervention
2. Multipolar Breakdown (40-45% probability): Trade becomes coercive, supply chains realign
3. Systemic Shock Cascade (10-20% probability): Financial/tech/geopolitical stresses amplify

CENTRAL MESSAGE:
"India must run a marathon and sprint simultaneously" - balancing domestic growth maximization
with shock absorption capacity, focusing on strategic autonomy and resilience.

STRUCTURE:
17 chapters covering macroeconomy, fiscal policy, monetary policy, external sector, inflation,
agriculture, services, manufacturing, infrastructure, climate, human development, employment,
social inclusion, plus special essays on AI, urban development, strategic autonomy, and state capacity.
"""
    return summary


def get_key_highlights() -> list:
    """Get key highlights from the survey"""
    highlights = [
        {
            "category": "Economic Growth",
            "points": [
                "GDP grew over 7% in 2025, strongest in decades",
                "Growth accelerated through the year despite global headwinds",
                "Policy reforms and dynamism reinforced growth trajectory"
            ]
        },
        {
            "category": "Fiscal Consolidation",
            "points": [
                "Fiscal deficit: 4.8% in FY25 vs target of 4.9%",
                "FY26 target: 4.4% of GDP",
                "More than halved from 9.2% in FY21",
                "Concerns over state finances: revenue deficits rising"
            ]
        },
        {
            "category": "External Challenges",
            "points": [
                "US tariffs: 50% total (25% reciprocal + 25% penal)",
                "Rupee depreciated despite strong fundamentals",
                "India depends on capital flows for balance of payments",
                "Gold price rose from $2,607 to $5,101+ reflecting uncertainty"
            ]
        },
        {
            "category": "Credit Ratings",
            "points": [
                "S&P upgraded India from BBB- to BBB (first in 20 years)",
                "Additional upgrades from DBRS and R&I",
                "Reflects strong macroeconomic fundamentals"
            ]
        },
        {
            "category": "Monetary Policy",
            "points": [
                "RBI cut interest rates aggressively",
                "Liquidity conditions eased significantly",
                "Banking sector remains healthy with strong capital buffers"
            ]
        },
        {
            "category": "Strategic Priorities",
            "points": [
                "Power Gap: -4.0 (operating below potential)",
                "Focus on strategic autonomy and self-reliance",
                "Emphasis on state capacity and governance",
                "AI and urban development as future priorities"
            ]
        }
    ]
    return highlights


def get_chapter_summary(chapter_id: int) -> Optional[dict]:
    """Get summary of a specific chapter"""
    if not pdf_data["loaded"]:
        return None

    if chapter_id not in pdf_data["chapters"]:
        return None

    chapter = pdf_data["chapters"][chapter_id]

    # Predefined summaries for better quality
    summaries = {
        1: "Reviews India's macroeconomic performance in 2025 and outlook for 2026. Covers 7%+ growth achievement, credit upgrades, US tariffs (50%), and three global scenarios. Emphasizes that India must 'run marathon and sprint simultaneously.'",
        2: "Examines fiscal consolidation. Central government achieved 4.8% deficit (target 4.9%) in FY25, targets 4.4% for FY26. Increasing focus on state finances due to fiscal populism concerns.",
        3: "Covers monetary policy and financial sector. RBI cut rates aggressively, eased liquidity. Banking sector healthy with strong capital buffers. Macroprudential measures relaxed.",
        4: "Analyzes external sector including trade and balance of payments. Despite US tariffs, focus on diversification. Trade deficit in goods offset by services surplus and remittances. Rupee stability challenged.",
        5: "Reviews inflation trends. Successfully tamed and anchored within target. Global commodity prices favorable. Regional dynamics vary across states.",
        6: "Covers agricultural performance and productivity improvements. Focus on food security, farmer income support, and institutional interventions.",
        7: "Examines services sector evolution. India's strength in IT/BPM, financial services. Sector moving to new frontiers with digital services gaining prominence.",
        8: "Reviews manufacturing sector and PLI schemes. Focus on MSMEs, core industries, and global integration. Structural transformation underway.",
        9: "Assesses infrastructure development. Massive push in transport, energy transition, and digital infrastructure. Nuclear power opened to private sector.",
        10: "Addresses climate action. Balances adaptation and mitigation. Focus on green finance and streamlined environmental governance.",
        11: "Examines education and health. NEP 2020 implementation, quality improvements. Healthcare expanding with focus on preventive care.",
        12: "Analyzes employment and skill development. Job creation strategies, youth skilling programs, aligning education with industry needs.",
        13: "Reviews poverty reduction and social inclusion. Rural economy transformation, direct benefit transfers, financial inclusion progress.",
        14: "Special essay on AI. Development-oriented approach, human capital requirements, governance architecture, phased roadmap for AI future.",
        15: "Special essay on urban development. Cities need economic agency, better planning. Focus on land, housing, mobility, and citizen-centric governance.",
        16: "Special essay on strategic indigenization. Tiered framework for self-reliance, input cost reduction, moving from Swadeshi to strategic indispensability.",
        17: "Special essay on state capacity. Governance as binding constraint. Focus on regulatory state, private sector role, and deregulation."
    }

    return {
        "chapter_id": chapter_id,
        "title": chapter["title"],
        "subtitle": chapter["subtitle"],
        "pages": f"{chapter['pages'][0]}-{chapter['pages'][1]}",
        "summary": summaries.get(chapter_id, "Summary not available"),
        "content_length": len(chapter["content"])
    }


def get_chapter_content(chapter_id: int, max_length: int = 50000) -> Optional[dict]:
    """Get full content of a specific chapter"""
    if not pdf_data["loaded"]:
        return None

    if chapter_id not in pdf_data["chapters"]:
        return None

    chapter = pdf_data["chapters"][chapter_id]
    content = chapter["content"]

    # Truncate if too long
    if len(content) > max_length:
        content = content[:max_length] + f"\n\n[Content truncated. Total length: {len(chapter['content'])} characters]"

    return {
        "chapter_id": chapter_id,
        "title": chapter["title"],
        "subtitle": chapter["subtitle"],
        "pages": f"{chapter['pages'][0]}-{chapter['pages'][1]}",
        "content": content,
        "full_length": len(chapter["content"])
    }


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="get_document_summary",
            description="Get an executive summary of the entire Economic Survey 2025-26 document, including key highlights, scenarios for 2026, and overall structure",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_key_highlights",
            description="Get structured key highlights from the Economic Survey organized by categories (Economic Growth, Fiscal Policy, External Challenges, etc.)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_chapters",
            description="List all 17 chapters of the Economic Survey with their titles, subtitles, and page ranges",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_chapter_summary",
            description="Get a concise summary of a specific chapter by its number (1-17)",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "integer",
                        "description": "Chapter number (1-17)",
                        "minimum": 1,
                        "maximum": 17
                    }
                },
                "required": ["chapter_id"]
            }
        ),
        Tool(
            name="get_chapter_content",
            description="Get the complete content of a specific chapter by its number (1-17). Returns full text extracted from the PDF.",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "integer",
                        "description": "Chapter number (1-17)",
                        "minimum": 1,
                        "maximum": 17
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum content length in characters (default: 50000)",
                        "default": 50000
                    }
                },
                "required": ["chapter_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    # Ensure PDF is loaded
    if not pdf_data["loaded"]:
        if not load_pdf():
            return [TextContent(
                type="text",
                text="Error: Could not load PDF file. Please ensure the PDF is placed in the data/ directory."
            )]

    try:
        if name == "get_document_summary":
            summary = get_document_summary()
            return [TextContent(type="text", text=summary)]

        elif name == "get_key_highlights":
            highlights = get_key_highlights()
            formatted = "KEY HIGHLIGHTS FROM ECONOMIC SURVEY 2025-26\n" + "=" * 60 + "\n\n"
            for item in highlights:
                formatted += f"\n{item['category'].upper()}\n" + "-" * 40 + "\n"
                for point in item['points']:
                    formatted += f"• {point}\n"
            return [TextContent(type="text", text=formatted)]

        elif name == "list_chapters":
            chapters_list = "ECONOMIC SURVEY 2025-26 - ALL CHAPTERS\n" + "=" * 60 + "\n\n"
            for ch_id, ch_info in CHAPTERS.items():
                chapters_list += f"Chapter {ch_id}: {ch_info['title']}\n"
                chapters_list += f"  Subtitle: {ch_info['subtitle']}\n"
                chapters_list += f"  Pages: {ch_info['pages'][0]}-{ch_info['pages'][1]}\n\n"
            return [TextContent(type="text", text=chapters_list)]

        elif name == "get_chapter_summary":
            chapter_id = arguments.get("chapter_id")
            summary = get_chapter_summary(chapter_id)

            if not summary:
                return [TextContent(
                    type="text",
                    text=f"Error: Chapter {chapter_id} not found. Please use chapter number between 1-17."
                )]

            formatted = f"CHAPTER {summary['chapter_id']}: {summary['title'].upper()}\n"
            formatted += f"Subtitle: {summary['subtitle']}\n"
            formatted += f"Pages: {summary['pages']}\n"
            formatted += "=" * 60 + "\n\n"
            formatted += f"SUMMARY:\n{summary['summary']}\n\n"
            formatted += f"Content Length: {summary['content_length']:,} characters"

            return [TextContent(type="text", text=formatted)]

        elif name == "get_chapter_content":
            chapter_id = arguments.get("chapter_id")
            max_length = arguments.get("max_length", 50000)
            content = get_chapter_content(chapter_id, max_length)

            if not content:
                return [TextContent(
                    type="text",
                    text=f"Error: Chapter {chapter_id} not found. Please use chapter number between 1-17."
                )]

            formatted = f"CHAPTER {content['chapter_id']}: {content['title'].upper()}\n"
            formatted += f"Subtitle: {content['subtitle']}\n"
            formatted += f"Pages: {content['pages']}\n"
            formatted += "=" * 60 + "\n\n"
            formatted += content['content']

            return [TextContent(type="text", text=formatted)]

        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error executing tool: {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Economic Survey MCP Server...")

    # Load PDF on startup
    load_pdf()

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
