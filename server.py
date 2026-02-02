"""
Economic Survey 2025-26 MCP Server (Simplified)

A simple MCP server that extracts RAW text from the Economic Survey PDF.
All cleaning and structuring is handled by the AI processing script.
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
    "loaded": False
}

# PDF file path
PDF_PATH = Path(__file__).parent / "data" / "economic-survey-2025-26.pdf"

# Chapter definitions (Page numbers from the PDF)
CHAPTERS = {
    1: {"title": "State of the Economy", "subtitle": "Frontier", "pages": (52, 87)},
    2: {"title": "Fiscal Policy", "subtitle": "Through Credible Consolidation", "pages": (88, 128)},
    3: {"title": "Monetary & Financial Sector", "subtitle": "Refining the Regulatory Touch", "pages": (129, 194)},
    4: {"title": "External Sector", "subtitle": "Playing the Long Game", "pages": (195, 253)},
    5: {"title": "Prices & Inflation", "subtitle": "Tamed and Anchored", "pages": (254, 275)},
    6: {"title": "Agriculture", "subtitle": "Productivity & Food Security", "pages": (276, 308)},
    7: {"title": "Services Sector", "subtitle": "From Stability to New Frontiers", "pages": (309, 342)},
    8: {"title": "Manufacturing", "subtitle": "And Global Integration", "pages": (343, 391)},
    9: {"title": "Infrastructure", "subtitle": "Connectivity, Capacity, Competitiveness", "pages": (392, 426)},
    10: {"title": "Climate & Environment", "subtitle": "Resilient, Competitive, Development-Driven", "pages": (427, 468)},
    11: {"title": "Human Development", "subtitle": "Education & Health", "pages": (469, 516)},
    12: {"title": "Employment & Skills", "subtitle": "Skilling Right", "pages": (517, 562)},
    13: {"title": "Social Inclusion", "subtitle": "Participation to Partnership", "pages": (563, 598)},
    14: {"title": "Artificial Intelligence", "subtitle": "Forward (Special Essay)", "pages": (599, 637)},
    15: {"title": "Urban Development", "subtitle": "Cities for Its Citizens (Special Essay)", "pages": (638, 685)},
    16: {"title": "Strategic Autonomy", "subtitle": "Strategic Indispensability (Special Essay)", "pages": (686, 702)},
    17: {"title": "State Capacity", "subtitle": "State, Private Sector & Citizens (Special Essay)", "pages": (703, 730)}
}


def load_pdf():
    """Load PDF and extract RAW text from each chapter"""
    global pdf_data

    if not PDF_PATH.exists():
        logger.error(f"PDF file not found at {PDF_PATH}")
        return False

    try:
        logger.info(f"Loading PDF from {PDF_PATH}")
        doc = fitz.open(str(PDF_PATH))

        pdf_data["metadata"] = {
            "title": "Economic Survey 2025-26",
            "pages": doc.page_count,
            "chapters": len(CHAPTERS)
        }

        # Extract RAW text from each chapter (NO CLEANING)
        for chapter_id, chapter_info in CHAPTERS.items():
            start_page, end_page = chapter_info["pages"]
            raw_text = []

            for page_num in range(start_page - 1, min(end_page, doc.page_count)):
                page = doc[page_num]
                text = page.get_text()  # Just raw text extraction
                raw_text.append(text)

            pdf_data["chapters"][chapter_id] = {
                "id": chapter_id,
                "title": chapter_info["title"],
                "subtitle": chapter_info["subtitle"],
                "pages": chapter_info["pages"],
                "raw_content": "\n".join(raw_text)  # Store as raw text
            }

        pdf_data["loaded"] = True
        doc.close()

        logger.info(f"PDF loaded successfully: {doc.page_count} pages, {len(CHAPTERS)} chapters")
        return True

    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        return False


def get_chapter_content_raw(chapter_id: int) -> Optional[dict]:
    """Get RAW content of a specific chapter (no cleaning)"""
    if not pdf_data["loaded"]:
        load_pdf()

    if chapter_id not in pdf_data["chapters"]:
        return None

    chapter = pdf_data["chapters"][chapter_id]

    return {
        "chapter_id": chapter_id,
        "title": chapter["title"],
        "subtitle": chapter["subtitle"],
        "pages": {
            "start": chapter['pages'][0],
            "end": chapter['pages'][1]
        },
        "raw_content": chapter["raw_content"],
        "content_length": len(chapter["raw_content"])
    }


# MCP Tool Handlers

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_chapter_content",
            description="Get raw content from a specific chapter (1-17). Returns unprocessed text for AI cleaning.",
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
            name="list_chapters",
            description="List all 17 chapters with titles and page ranges",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    if name == "get_chapter_content":
        chapter_id = arguments.get("chapter_id")

        if not pdf_data["loaded"]:
            load_pdf()

        result = get_chapter_content_raw(chapter_id)

        if not result:
            return [TextContent(
                type="text",
                text=f"Error: Chapter {chapter_id} not found"
            )]

        # Return raw content in a structured format
        output = f"""CHAPTER {result['chapter_id']}: {result['title'].upper()}
Subtitle: {result['subtitle']}
Pages: {result['pages']['start']}-{result['pages']['end']}
Content Length: {result['content_length']:,} characters
{'='*60}

{result['raw_content']}"""

        return [TextContent(type="text", text=output)]

    elif name == "list_chapters":
        if not pdf_data["loaded"]:
            load_pdf()

        output = "Economic Survey 2025-26 - All Chapters\n"
        output += "="*60 + "\n\n"

        for chapter_id, info in CHAPTERS.items():
            output += f"Chapter {chapter_id}: {info['title']}\n"
            output += f"  Subtitle: {info['subtitle']}\n"
            output += f"  Pages: {info['pages'][0]}-{info['pages'][1]}\n\n"

        return [TextContent(type="text", text=output)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
