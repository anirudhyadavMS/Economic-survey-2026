"""
Economic Survey 2025-26 MCP Server

An MCP server that provides AI-powered access to India's Economic Survey 2025-26.
Offers tools to get summaries, key highlights, and chapter content.
"""

import asyncio
import json
import logging
import tempfile
import os
import re
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
import anthropic
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Load environment variables from .env file
load_dotenv()

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

# Output directory for markdown files
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Front matter sections (before Chapter 1)
# Pages 1-51 contain: Title, Contents, Preface, Acknowledgments, Abbreviations,
# List of Tables, List of Charts, List of Boxes
FRONT_MATTER = {
    "title_page": {"title": "Title Page", "pages": (1, 2)},
    "contents": {"title": "Contents", "pages": (4, 7)},
    "preface": {"title": "Preface", "pages": (8, 16)},
    "acknowledgments": {"title": "Acknowledgments", "pages": (18, 19)},
    "abbreviations": {"title": "Abbreviations", "pages": (20, 37)},
    "list_of_tables": {"title": "List of Tables", "pages": (38, 39)},
    "list_of_charts": {"title": "List of Charts", "pages": (40, 47)},
    "list_of_boxes": {"title": "List of Boxes", "pages": (48, 51)}
}

# Chapter definitions (Chapter 1 starts at page 52, after all front matter)
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

            # Extract plain text
            for page_num in range(start_page - 1, min(end_page, doc.page_count)):
                page = doc[page_num]
                text = page.get_text()
                chapter_text.append(text)

            # Extract structured content with chapter number
            structured = extract_structured_content(doc, start_page, end_page, chapter_id)

            pdf_data["chapters"][chapter_id] = {
                "id": chapter_id,
                "title": chapter_info["title"],
                "subtitle": chapter_info["subtitle"],
                "pages": chapter_info["pages"],
                "content": "\n".join(chapter_text),
                "structured_content": structured
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

DOCUMENT STRUCTURE:
• Front Matter (pages 1-51): Title, Contents, Preface, Acknowledgments, Abbreviations, List of Tables, List of Charts, List of Boxes
• Main Content: 17 chapters (pages 52-730)

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


def extract_structured_content(doc, start_page, end_page, chapter_num):
    """Extract structured content from Economic Survey chapter

    Structure:
    - Chapter title
    - Summary section (before first numbered section)
    - Numbered sections (e.g., 1.1, 1.2)
    - Headings and paragraphs within sections
    - References (consolidated at end)

    Ignores: Tables, Figures, Boxes, Headers, Footers
    """
    import re

    structured_content = {
        "title": "",
        "summary": [],
        "sections": [],
        "references": []
    }

    current_section = None
    references_temp = []
    in_table_figure_box = False
    collecting_section_title = False
    pending_section_data = None

    for page_num in range(start_page - 1, min(end_page, doc.page_count)):
        page = doc[page_num]
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])

        page_height = page.rect.height

        for block in blocks:
            if block.get("type") != 0:  # Not a text block
                continue

            lines = block.get("lines", [])
            block_y = block.get("bbox", [0, 0, 0, 0])[1]  # Y position

            # Skip headers (top 10% of page) and footers (bottom 5% of page)
            if block_y < page_height * 0.1 or block_y > page_height * 0.95:
                continue

            for line in lines:
                spans = line.get("spans", [])
                if not spans:
                    continue

                # Combine text from spans
                line_text = ""
                size_sum = 0
                is_bold = False

                for span in spans:
                    line_text += span.get("text", "")
                    size_sum += span.get("size", 0)
                    font_name = span.get("font", "")
                    if "bold" in font_name.lower():
                        is_bold = True

                avg_size = size_sum / len(spans) if spans else 0
                line_text = line_text.strip()

                if not line_text or len(line_text) <= 2:
                    continue

                # Check for table/figure/box markers
                if re.match(r'^(Table|Figure|Chart|Box)\s+[IVXivx0-9]+\.\d+', line_text, re.IGNORECASE):
                    in_table_figure_box = True
                    continue

                # Skip if we're inside a table/figure/box (until we hit next section or large text gap)
                if in_table_figure_box:
                    # Exit table/figure/box mode when we hit a numbered section or normal paragraph
                    if re.match(r'^\d+\.\d+', line_text) or (avg_size >= 11 and not line_text[0].isdigit()):
                        in_table_figure_box = False
                    else:
                        continue

                # Capture references (lines starting with Source:, Note:, or reference numbers)
                if re.match(r'^(Source|Note)[\s:]', line_text, re.IGNORECASE):
                    references_temp.append({
                        "text": line_text,
                        "page": page_num + 1
                    })
                    continue

                # Extract chapter title (first large bold text)
                if not structured_content["title"] and avg_size >= 14 and is_bold:
                    if not re.match(r'^\d+$', line_text):  # Skip page numbers
                        structured_content["title"] = line_text
                        continue

                # Check for numbered sections (e.g., "1.1.", "1.2." or "2.1\t", "2.2\t")
                # Format: "1.1.\t Title text" or "1.1 Title text" or "2.1\t Title"
                section_match = re.match(rf'^{chapter_num}\.(\d+)\.?\s+(.+)', line_text)
                if section_match:
                    # Save previous section
                    if current_section:
                        structured_content["sections"].append(current_section)
                    if pending_section_data:
                        structured_content["sections"].append(pending_section_data)

                    # Start new section
                    section_id = f"{chapter_num}.{section_match.group(1)}"
                    section_title = section_match.group(2).strip()

                    # Use first 100 chars as title (don't collect multiple lines)
                    if len(section_title) > 100:
                        section_title = section_title[:97] + "..."

                    current_section = {
                        "section_id": section_id,
                        "title": section_title,
                        "content": [],
                        "page_start": page_num + 1
                    }
                    collecting_section_title = False
                    pending_section_data = None

                    continue

                # Determine block type
                block_type = "paragraph"
                level = 0

                # Subsection numbering (e.g., "1.1.1.", "1.1.2." or "2.1.1\t")
                subsection_match = re.match(rf'^{chapter_num}\.\d+\.\d+\.?\s+(.+)', line_text)
                if subsection_match:
                    block_type = "subheading"
                    level = 3
                # Bold text or all caps = heading
                elif (is_bold and avg_size >= 11) or (line_text.isupper() and 3 < len(line_text) < 100):
                    block_type = "heading"
                    level = 2

                # Create content block
                content_block = {
                    "type": block_type,
                    "text": line_text,
                    "page": page_num + 1,
                    "font_size": round(avg_size, 1),
                    "is_bold": is_bold
                }

                if block_type in ["heading", "subheading"]:
                    content_block["level"] = level

                # Add to appropriate section
                if current_section:
                    current_section["content"].append(content_block)
                else:
                    # Before first section = summary
                    if structured_content["title"]:  # Only add to summary after title is found
                        structured_content["summary"].append(content_block)

    # Add last section
    if current_section:
        structured_content["sections"].append(current_section)

    # Consolidate and deduplicate references
    seen_refs = set()
    for ref in references_temp:
        ref_text = ref["text"]
        if ref_text not in seen_refs:
            seen_refs.add(ref_text)
            structured_content["references"].append(ref)

    return structured_content

    # Post-process to merge paragraph lines and clean up
    merged_content = []
    current_paragraph = None

    for block in structured_content:
        if block["type"] == "heading":
            # Save any pending paragraph
            if current_paragraph:
                merged_content.append(current_paragraph)
                current_paragraph = None
            merged_content.append(block)
        else:  # paragraph
            # Merge consecutive paragraph lines
            if current_paragraph is None:
                current_paragraph = block.copy()
            else:
                # Check if this should be merged with previous paragraph
                # Merge if text doesn't end with period or if next starts lowercase
                prev_text = current_paragraph["text"]
                curr_text = block["text"]

                if (not prev_text.endswith('.') and not prev_text.endswith(':') and
                    not curr_text[0].isupper() if curr_text else False) or \
                   len(prev_text) < 100:  # Short lines likely continue
                    current_paragraph["text"] += " " + curr_text
                else:
                    merged_content.append(current_paragraph)
                    current_paragraph = block.copy()

    # Add last paragraph
    if current_paragraph:
        merged_content.append(current_paragraph)

    return merged_content


def clean_and_structure_with_ai(raw_text: str, chapter_num: int, chapter_title: str) -> dict:
    """
    Use Claude AI to clean and structure chapter content

    Returns structured content with:
    - Chapter number and title
    - Summary section
    - Numbered sections with content
    - References

    Removes: Tables, Charts, Figures, Boxes, Headers, Footers
    """
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set, falling back to basic extraction")
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Split into chunks if too large (max ~100k chars per request)
        max_chunk_size = 90000
        chunks = []

        if len(raw_text) > max_chunk_size:
            # Split by pages or sections
            pages = raw_text.split('\n\n')
            current_chunk = ""

            for page in pages:
                if len(current_chunk) + len(page) < max_chunk_size:
                    current_chunk += page + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = page + "\n\n"

            if current_chunk:
                chunks.append(current_chunk)
        else:
            chunks = [raw_text]

        logger.info(f"Processing chapter {chapter_num} in {len(chunks)} chunk(s)")

        # Process first chunk to get structure
        first_chunk_prompt = f"""You are analyzing Chapter {chapter_num} of India's Economic Survey 2025-26: "{chapter_title}".

TASK: Extract and structure the content following this exact format:

1. **Chapter Info**: Extract chapter number and full title
2. **Summary**: The introductory paragraphs before the first numbered section (e.g., before {chapter_num}.1)
3. **Sections**: All numbered sections (format: {chapter_num}.1, {chapter_num}.2, etc.) with their content
4. **References**: Consolidate all "Source:", "Note:", and citation lines at the end

IMPORTANT RULES:
- IGNORE and REMOVE all Tables, Charts, Figures, and Boxes completely
- IGNORE headers and footers (page numbers, chapter titles at top/bottom of pages)
- Clean up newline characters - join broken sentences
- Keep only the substantive text content (paragraphs and headings)
- For each section, capture the section number and a brief title (first line)

Return ONLY valid JSON in this exact format:
{{
  "chapter_number": {chapter_num},
  "chapter_title": "Full chapter title",
  "summary": [
    "Paragraph 1 of summary...",
    "Paragraph 2 of summary..."
  ],
  "sections": [
    {{
      "section_id": "{chapter_num}.1",
      "title": "Brief section title",
      "content": [
        {{
          "type": "heading",
          "text": "Heading text"
        }},
        {{
          "type": "paragraph",
          "text": "Paragraph text..."
        }}
      ]
    }}
  ],
  "references": [
    "Source: ...",
    "Note: ..."
  ]
}}

Here's the chapter content to process:

{chunks[0]}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=16000,
            temperature=0,
            messages=[{"role": "user", "content": first_chunk_prompt}]
        )

        # Extract JSON from response
        response_text = message.content[0].text

        # Try to find JSON in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            structured_data = json.loads(json_match.group())
        else:
            structured_data = json.loads(response_text)

        # Process remaining chunks if any and append sections
        if len(chunks) > 1:
            for i, chunk in enumerate(chunks[1:], start=2):
                logger.info(f"Processing chunk {i}/{len(chunks)}")

                continuation_prompt = f"""Continue extracting sections from Chapter {chapter_num}.
This is continuation chunk {i} of {len(chunks)}.

Extract any additional numbered sections ({chapter_num}.X format) and references.
Return ONLY JSON:
{{
  "sections": [...],
  "references": [...]
}}

Content:
{chunk}"""

                chunk_message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=16000,
                    temperature=0,
                    messages=[{"role": "user", "content": continuation_prompt}]
                )

                chunk_text = chunk_message.content[0].text
                json_match = re.search(r'\{.*\}', chunk_text, re.DOTALL)
                if json_match:
                    chunk_data = json.loads(json_match.group())

                    # Append sections and references
                    if "sections" in chunk_data:
                        structured_data["sections"].extend(chunk_data["sections"])
                    if "references" in chunk_data:
                        structured_data["references"].extend(chunk_data["references"])

        # Deduplicate references
        structured_data["references"] = list(dict.fromkeys(structured_data.get("references", [])))

        logger.info(f"AI extraction complete: {len(structured_data.get('sections', []))} sections, "
                   f"{len(structured_data.get('references', []))} references")

        return structured_data

    except Exception as e:
        logger.error(f"AI extraction failed: {e}")
        return None


def clean_content(text: str) -> str:
    """Remove charts, tables, and their captions from the content

    This is a conservative filter that removes obvious chart/table blocks
    while preserving narrative text with embedded statistics.
    """
    import re

    lines = text.split('\n')
    cleaned_lines = []
    in_table_block = False
    table_block_lines = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Keep empty lines
        if not stripped:
            if not in_table_block:
                cleaned_lines.append(line)
            i += 1
            continue

        # === CHART/TABLE CAPTION DETECTION ===
        # Match: "Chart I.1:", "Table I.2a:", etc.
        caption_match = re.match(r'^(Chart|Table|Figure|Box)\s+[IVXivx]+\.\d+[a-z]?[\s:]+(.+)', stripped, re.IGNORECASE)
        if caption_match:
            # Skip caption line
            i += 1
            # Skip the next few lines that are part of the caption/title (usually short lines)
            while i < len(lines) and len(lines[i].strip()) < 80 and lines[i].strip():
                i += 1
            continue

        # === TABLE BLOCK DETECTION ===
        # A table block has multiple consecutive lines with structured data
        # Look ahead to detect table blocks
        if not in_table_block:
            # Check if this starts a table block (look at next 3-5 lines)
            lookahead_lines = lines[i:min(i+5, len(lines))]
            table_indicators = 0

            for look_line in lookahead_lines:
                look_stripped = look_line.strip()
                if not look_stripped:
                    break

                # Count indicators of table structure:
                # 1. Multiple tabs
                if look_line.count('\t') >= 2:
                    table_indicators += 1

                # 2. Lines with pattern: word/phrase followed by numbers
                # Example: "Agriculture, Livestock    2.7    3.6    4.6"
                if re.search(r'^[A-Za-z][A-Za-z\s,&-]+\s+[\d\.\-\s]+$', look_stripped):
                    table_indicators += 1

                # 3. Lines that are mostly numbers separated by spaces
                # Example: "2.7    3.6    4.6    3.1"
                words = look_stripped.split()
                if len(words) >= 3:
                    num_words = sum(1 for w in words if re.match(r'^[\d\.\-\(\)]+$', w))
                    if num_words >= 3:
                        table_indicators += 1

            # If we found 2+ table indicators, this is a table block
            if table_indicators >= 2:
                in_table_block = True
                table_block_lines = 0

        # If in table block, skip lines
        if in_table_block:
            table_block_lines += 1
            i += 1

            # Exit table block after empty line or after many lines
            if not stripped or table_block_lines > 20:
                in_table_block = False
                table_block_lines = 0
            continue

        # === FILTER INDIVIDUAL LINES ===

        # Skip "Source:" and "Note:" lines
        if re.match(r'^(Source|Note)[\s:]', stripped, re.IGNORECASE):
            i += 1
            continue

        # Skip lines that are purely tabular (lots of tabs/numbers, minimal text)
        if line.count('\t') >= 3:
            i += 1
            continue

        # Skip lines where 80%+ is numbers and separators (but keep if part of prose)
        if len(stripped) > 20:
            non_alpha = sum(1 for c in stripped if not c.isalpha() and c != ' ')
            if non_alpha / len(stripped.replace(' ', '')) > 0.8:
                i += 1
                continue

        # === KEEP THIS LINE ===
        cleaned_lines.append(line)
        i += 1

    # Join and clean up whitespace
    cleaned_text = '\n'.join(cleaned_lines)
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)

    return cleaned_text


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


def clean_structured_content(structured_content):
    """Clean structured content by removing artifacts and validating blocks

    The new structure is:
    {
        "title": str,
        "summary": [blocks],
        "sections": [{section_id, title, content: [blocks]}],
        "references": [refs]
    }
    """
    import re

    if not isinstance(structured_content, dict):
        return structured_content

    def clean_blocks(blocks):
        """Clean a list of content blocks"""
        cleaned = []
        for block in blocks:
            text = block.get("text", "")

            # Skip very short or likely artifacts
            if len(text) < 3:
                continue

            # Skip blocks that are mostly numbers (table data remnants)
            if len(text) > 20:
                alpha_chars = sum(c.isalpha() for c in text)
                total_chars = len(text.replace(' ', ''))
                if total_chars > 0 and alpha_chars / total_chars < 0.3:
                    continue

            cleaned.append(block)
        return cleaned

    # Clean each part of the structure
    cleaned_structure = {
        "title": structured_content.get("title", ""),
        "summary": clean_blocks(structured_content.get("summary", [])),
        "sections": [],
        "references": structured_content.get("references", [])
    }

    # Clean each section's content
    for section in structured_content.get("sections", []):
        cleaned_section = {
            "section_id": section.get("section_id", ""),
            "title": section.get("title", ""),
            "content": clean_blocks(section.get("content", [])),
            "page_start": section.get("page_start", 0)
        }
        if cleaned_section["content"]:  # Only include sections with content
            cleaned_structure["sections"].append(cleaned_section)

    return cleaned_structure


def get_chapter_content(chapter_id: int, save_to_file: bool = True, output_format: str = "md") -> Optional[dict]:
    """Get full content of a specific chapter and optionally save to file

    Args:
        chapter_id: Chapter number (1-17)
        save_to_file: Whether to save to file
        output_format: Output format - "md" (markdown), "json", or "both"
    """
    if not pdf_data["loaded"]:
        return None

    if chapter_id not in pdf_data["chapters"]:
        return None

    chapter = pdf_data["chapters"][chapter_id]
    content = chapter["content"]

    result = {
        "chapter_id": chapter_id,
        "title": chapter["title"],
        "subtitle": chapter["subtitle"],
        "pages": f"{chapter['pages'][0]}-{chapter['pages'][1]}",
        "full_length": len(content)
    }

    if save_to_file:
        # Clean content to remove charts and tables
        cleaned_content = clean_content(content)

        result["original_length"] = len(content)
        result["cleaned_length"] = len(cleaned_content)

        base_filename = f"chapter_{chapter_id:02d}_{chapter['title'].lower().replace(' ', '_').replace('&', 'and')}"

        files_created = []

        # Save as Markdown
        if output_format in ["md", "both"]:
            md_filename = f"{base_filename}.md"
            md_filepath = OUTPUT_DIR / md_filename

            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Chapter {chapter_id}: {chapter['title']}\n\n")
                f.write(f"**{chapter['subtitle']}**\n\n")
                f.write(f"*Pages: {chapter['pages'][0]}-{chapter['pages'][1]}*\n\n")
                f.write("---\n\n")
                f.write(cleaned_content)

            files_created.append({
                "format": "markdown",
                "path": str(md_filepath),
                "size": md_filepath.stat().st_size
            })

        # Save as JSON
        if output_format in ["json", "both"]:
            json_filename = f"{base_filename}.json"
            json_filepath = OUTPUT_DIR / json_filename

            # Try AI-based extraction first
            ai_structured = clean_and_structure_with_ai(content, chapter_id, chapter["title"])

            if ai_structured:
                # Use AI-extracted structure
                cleaned_structured = ai_structured
                extraction_method = "ai"
                logger.info(f"Using AI-extracted structure for chapter {chapter_id}")

                # Calculate statistics for AI structure
                total_blocks = len(cleaned_structured.get("summary", []))
                headings = 0
                paragraphs = 0

                for section in cleaned_structured.get("sections", []):
                    for block in section.get("content", []):
                        total_blocks += 1
                        if block.get("type") == "heading":
                            headings += 1
                        elif block.get("type") == "paragraph":
                            paragraphs += 1

            else:
                # Fall back to manual extraction
                structured = chapter.get("structured_content", {})
                cleaned_structured = clean_structured_content(structured)
                extraction_method = "manual"
                logger.info(f"Using manual extraction for chapter {chapter_id}")

                # Calculate statistics for manual structure
                total_blocks = len(cleaned_structured.get("summary", []))
                headings = 0
                paragraphs = 0

                for section in cleaned_structured.get("sections", []):
                    for block in section.get("content", []):
                        total_blocks += 1
                        if block.get("type") in ["heading", "subheading"]:
                            headings += 1
                        elif block.get("type") == "paragraph":
                            paragraphs += 1

            json_data = {
                "chapter_id": chapter_id,
                "title": chapter["title"],
                "subtitle": chapter["subtitle"],
                "pages": {
                    "start": chapter['pages'][0],
                    "end": chapter['pages'][1]
                },
                "content": {
                    "structured": cleaned_structured
                },
                "metadata": {
                    "extraction_method": extraction_method,
                    "original_length": len(content),
                    "structure": {
                        "sections_count": len(cleaned_structured.get("sections", [])),
                        "summary_paragraphs": len(cleaned_structured.get("summary", [])),
                        "total_content_blocks": total_blocks,
                        "headings": headings,
                        "paragraphs": paragraphs,
                        "references": len(cleaned_structured.get("references", []))
                    }
                }
            }

            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            files_created.append({
                "format": "json",
                "path": str(json_filepath),
                "size": json_filepath.stat().st_size
            })

        result["files"] = files_created

        # Include preview (first 2000 chars of cleaned content)
        result["preview"] = cleaned_content[:2000] + "\n\n[... Full content saved to file ...]" if len(cleaned_content) > 2000 else cleaned_content
    else:
        result["content"] = content

    return result


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
            description="List all 17 chapters of the Economic Survey with their titles, subtitles, and page ranges. Note: Front matter (Contents, Preface, Acknowledgments, lists, etc.) is on pages 1-51. Chapter 1 starts at page 52.",
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
            description="Get the complete content of a specific chapter by its number (1-17). Saves full content to file(s) and returns the file path(s) along with a preview. Supports markdown and JSON output formats.",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "integer",
                        "description": "Chapter number (1-17)",
                        "minimum": 1,
                        "maximum": 17
                    },
                    "save_to_file": {
                        "type": "boolean",
                        "description": "Save complete content to file (default: true)",
                        "default": True
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format: 'md' for markdown, 'json' for JSON, or 'both' for both formats (default: 'md')",
                        "enum": ["md", "json", "both"],
                        "default": "md"
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
            save_to_file = arguments.get("save_to_file", True)
            output_format = arguments.get("output_format", "md")
            content = get_chapter_content(chapter_id, save_to_file, output_format)

            if not content:
                return [TextContent(
                    type="text",
                    text=f"Error: Chapter {chapter_id} not found. Please use chapter number between 1-17."
                )]

            formatted = f"CHAPTER {content['chapter_id']}: {content['title'].upper()}\n"
            formatted += f"Subtitle: {content['subtitle']}\n"
            formatted += f"Pages: {content['pages']}\n"
            formatted += f"Content Length: {content['full_length']:,} characters\n"
            formatted += "=" * 60 + "\n\n"

            if save_to_file and 'files' in content:
                formatted += f"[OK] Content saved successfully:\n\n"

                for file_info in content['files']:
                    formatted += f"  {file_info['format'].upper()} File:\n"
                    formatted += f"    Path: {file_info['path']}\n"
                    formatted += f"    Size: {file_info['size']:,} bytes\n\n"

                if 'cleaned_length' in content and 'original_length' in content:
                    chars_removed = content['original_length'] - content['cleaned_length']
                    pct_removed = (chars_removed / content['original_length'] * 100) if content['original_length'] > 0 else 0
                    formatted += f"Content Processing:\n"
                    formatted += f"  Original length: {content['original_length']:,} characters\n"
                    formatted += f"  Cleaned length: {content['cleaned_length']:,} characters\n"
                    formatted += f"  Removed: {chars_removed:,} characters ({pct_removed:.1f}%) - charts/tables filtered\n"

                formatted += "\nCONTENT PREVIEW:\n"
                formatted += "-" * 60 + "\n"
                formatted += content['preview']
            else:
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
