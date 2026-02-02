"""
Enhanced AI Processor for Economic Survey Chapters

This script contains ALL the intelligence for cleaning and structuring chapters.
It understands the Economic Survey document format and applies smart processing.

DOCUMENT STRUCTURE KNOWLEDGE:
1. Each chapter starts with:
   - Chapter number (e.g., "CHAPTER 2" or just "2")
   - Chapter title (ALL CAPS, e.g., "FISCAL DEVELOPMENTS:")
   - Subtitle (may be ALL CAPS)

2. Summary section:
   - Introductory paragraphs BEFORE first numbered section (X.1)
   - Usually 3-10 paragraphs of overview

3. Numbered sections:
   - Format: "X.Y" or "X.Y." where X = chapter number, Y = section number
   - Examples: "2.1", "2.2.", "2.10"
   - May have tab after number: "2.1\t" or "2.1. "

4. Content to REMOVE:
   - Tables: "Table II.1", "Table 2.3" with data rows
   - Charts: "Chart II.1", "Chart 2.2" with descriptions
   - Figures: "Figure 2.1"
   - Boxes: "Box II.1", "Box 2.1" (special topic boxes)
   - Source lines: "Source: ..."
   - Note lines: "Note: ..."
   - Headers/Footers: Page numbers, "Economic Survey 2025-26", "Fiscal Developments"

5. Content to KEEP:
   - All substantive paragraphs
   - Section headings (bold or ALL CAPS)
   - Footnote references (numbers like 1, 2, 3)

6. Text formatting issues to fix:
   - Sentences broken across lines (no space or with hyphen)
   - Multiple newlines
   - Line numbers from PDF (e.g., "123→")
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


class EconomicSurveyProcessor:
    """
    Intelligent processor for Economic Survey chapters
    Contains all document structure knowledge
    """

    def __init__(self, chapter_num: int):
        self.chapter_num = chapter_num
        self.in_table_chart_box = False
        self.skip_count = 0

    def clean_line(self, line: str) -> str:
        """Clean a single line of text"""
        # Remove line numbers (e.g., "123→")
        line = re.sub(r'^\s*\d+→', '', line)
        # Remove excessive whitespace
        line = ' '.join(line.split())
        return line.strip()

    def is_table_marker(self, text: str) -> bool:
        """Check if line marks start of a table"""
        patterns = [
            r'^Table\s+[IVX]+\.\d+',  # Table II.1
            r'^Table\s+\d+\.\d+',      # Table 2.1
            r'^\s*FY\d{2}\s+FY\d{2}',  # FY23 FY24 (table header)
            r'^\s*₹\s+lakh\s+crore',   # Currency column header
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def is_chart_marker(self, text: str) -> bool:
        """Check if line marks start of a chart"""
        patterns = [
            r'^Chart\s+[IVX]+\.\d+',  # Chart II.1
            r'^Chart\s+\d+\.\d+',      # Chart 2.1
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def is_figure_marker(self, text: str) -> bool:
        """Check if line marks start of a figure"""
        patterns = [
            r'^Figure\s+[IVX]+\.\d+',  # Figure II.1
            r'^Figure\s+\d+\.\d+',      # Figure 2.1
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def is_box_marker(self, text: str) -> bool:
        """Check if line marks start of a box"""
        patterns = [
            r'^Box\s+[IVX]+\.\d+',  # Box II.1
            r'^Box\s+\d+\.\d+',      # Box 2.1
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def is_source_note(self, text: str) -> bool:
        """Check if line is a source or note"""
        return re.match(r'^(Source|Note)[\s:]', text, re.IGNORECASE) is not None

    def is_table_data(self, text: str) -> bool:
        """Check if line is table data (lots of numbers)"""
        if len(text) < 10:
            return False
        # Count numeric characters vs total
        numbers = sum(c.isdigit() or c in '.,₹%' for c in text)
        letters = sum(c.isalpha() for c in text)
        if letters == 0:
            return True
        return numbers / len(text) > 0.6

    def is_header_footer(self, text: str) -> bool:
        """Check if line is header/footer"""
        patterns = [
            r'^Economic Survey 2025-26$',
            r'^Fiscal Developments$',
            r'^State of the Economy$',
            r'^\d+$',  # Just a page number
            r'^\s*\d{2}\s*$',  # Page number with spaces
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def extract_section_number(self, text: str) -> tuple:
        """
        Extract section number from text
        Returns: (section_id, remaining_text) or (None, text)
        """
        # Try patterns like "2.1", "2.1.", "2.1\t"
        match = re.match(rf'^({self.chapter_num}\.(\d+))\.?\s+(.+)', text)
        if match:
            return (match.group(1), match.group(3))
        return (None, text)

    def is_heading(self, text: str) -> bool:
        """Check if text is a heading"""
        # All caps text (not too short, not too long)
        if text.isupper() and 10 < len(text) < 120:
            return True
        # Starts with certain keywords
        heading_starts = ['INTRODUCTION', 'CENTRAL', 'Trends', 'Performance']
        return any(text.startswith(h) for h in heading_starts)

    def should_skip_line(self, text: str) -> bool:
        """Decide if a line should be skipped"""
        if not text or len(text) < 3:
            return True
        if self.is_header_footer(text):
            return True
        if self.is_source_note(text):
            return True
        if self.is_table_data(text):
            return True
        return False

    def join_broken_sentence(self, prev: str, curr: str) -> tuple:
        """
        Join broken sentences intelligently
        Returns: (should_join, separator)
        """
        if not prev:
            return (False, "")

        # Join if previous doesn't end with sentence boundary
        if not prev[-1] in '.!?:;':
            # Join if current starts lowercase
            if curr[0].islower():
                return (True, " ")
            # Join if previous ends with hyphen
            if prev.endswith('-'):
                return (True, "")
            # Join if short line (likely continuation)
            if len(prev) < 80:
                return (True, " ")

        return (False, "")

    def process_chapter(self, raw_content: str, chapter_title: str, chapter_subtitle: str) -> Dict[str, Any]:
        """
        Main processing function - applies all intelligence

        Args:
            raw_content: Raw text from MCP server
            chapter_title: Chapter title from metadata
            chapter_subtitle: Chapter subtitle from metadata

        Returns:
            Structured chapter data
        """

        lines = raw_content.split('\n')

        result = {
            "chapter_number": self.chapter_num,
            "chapter_title": f"{chapter_title}: {chapter_subtitle}",
            "summary": [],
            "sections": [],
            "references": []
        }

        current_section = None
        current_paragraph = ""
        found_first_section = False

        for i, raw_line in enumerate(lines):
            line = self.clean_line(raw_line)

            # Skip empty or invalid lines
            if self.should_skip_line(line):
                continue

            # Check for table/chart/box/figure markers
            if (self.is_table_marker(line) or
                self.is_chart_marker(line) or
                self.is_figure_marker(line) or
                self.is_box_marker(line)):
                self.in_table_chart_box = True
                self.skip_count = 20  # Skip next 20 lines
                continue

            # Skip if in table/chart/box mode
            if self.skip_count > 0:
                self.skip_count -= 1
                continue

            if self.in_table_chart_box:
                # Exit mode when we hit normal content again
                if len(line) > 50 and not self.is_table_data(line):
                    self.in_table_chart_box = False
                else:
                    continue

            # Extract section number
            section_id, remaining_text = self.extract_section_number(line)

            if section_id:
                # Save previous paragraph
                if current_paragraph:
                    if current_section:
                        current_section["content"].append({
                            "type": "paragraph",
                            "text": current_paragraph.strip()
                        })
                    elif not found_first_section:
                        result["summary"].append(current_paragraph.strip())
                    current_paragraph = ""

                # Save previous section
                if current_section:
                    result["sections"].append(current_section)

                # Start new section
                found_first_section = True
                current_section = {
                    "section_id": section_id,
                    "title": remaining_text[:100] + "..." if len(remaining_text) > 100 else remaining_text,
                    "content": []
                }
                continue

            # Check if it's a heading
            if self.is_heading(line):
                # Save previous paragraph
                if current_paragraph:
                    if current_section:
                        current_section["content"].append({
                            "type": "paragraph",
                            "text": current_paragraph.strip()
                        })
                    elif not found_first_section:
                        result["summary"].append(current_paragraph.strip())
                    current_paragraph = ""

                # Add heading
                if current_section:
                    current_section["content"].append({
                        "type": "heading",
                        "text": line
                    })
                continue

            # Regular text - accumulate intelligently
            should_join, separator = self.join_broken_sentence(current_paragraph, line)

            if should_join:
                current_paragraph += separator + line
            else:
                # Save previous paragraph
                if current_paragraph:
                    if current_section:
                        current_section["content"].append({
                            "type": "paragraph",
                            "text": current_paragraph.strip()
                        })
                    elif not found_first_section:
                        result["summary"].append(current_paragraph.strip())
                current_paragraph = line

        # Save last paragraph/section
        if current_paragraph:
            if current_section:
                current_section["content"].append({
                    "type": "paragraph",
                    "text": current_paragraph.strip()
                })
            elif not found_first_section:
                result["summary"].append(current_paragraph.strip())

        if current_section:
            result["sections"].append(current_section)

        return result


def process_chapter_from_mcp(mcp_response_file: Path, chapter_num: int, output_file: Path):
    """
    Process chapter from MCP response file

    Args:
        mcp_response_file: Path to MCP tool response
        chapter_num: Chapter number
        output_file: Where to save cleaned JSON
    """

    # Load MCP response
    with open(mcp_response_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract raw content from MCP response
    if isinstance(data, list) and len(data) > 0:
        text = data[0].get('text', '')

        # Parse the MCP response format
        # Format: "CHAPTER X: TITLE\nSubtitle: ...\nPages: ...\n===\n\n<content>"
        lines = text.split('\n')

        chapter_title = ""
        chapter_subtitle = ""
        raw_content = ""

        # Extract metadata and content
        content_start = False
        for line in lines:
            if line.startswith('CHAPTER'):
                chapter_title = line.split(':', 1)[1].strip() if ':' in line else ""
            elif line.startswith('Subtitle:'):
                chapter_subtitle = line.split(':', 1)[1].strip()
            elif '='*60 in line:
                content_start = True
            elif content_start:
                raw_content += line + '\n'

        # Process with intelligence
        processor = EconomicSurveyProcessor(chapter_num)
        result = processor.process_chapter(raw_content, chapter_title, chapter_subtitle)

        # Add metadata
        result["metadata"] = {
            "extraction_method": "mcp_raw + ai_intelligent_processing",
            "structure": {
                "sections_count": len(result["sections"]),
                "summary_paragraphs": len(result["summary"]),
                "references": len(result["references"])
            }
        }

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[OK] Processed Chapter {chapter_num}")
        print(f"   Title: {result['chapter_title']}")
        print(f"   Summary: {len(result['summary'])} paragraphs")
        print(f"   Sections: {len(result['sections'])}")
        print(f"   Saved to: {output_file}")

        return result

    return None


if __name__ == "__main__":
    # Example usage
    mcp_file = Path("C:/Users/anirudhyadav/.claude/projects/C--Users-anirudhyadav/4136eb76-3614-4a80-a572-fc927f9f269c/tool-results/mcp-economic-survey-get_chapter_content-1770008160120.txt")
    output_file = Path(__file__).parent / "output" / "chapter_02_enhanced_ai.json"

    if mcp_file.exists():
        process_chapter_from_mcp(mcp_file, chapter_num=2, output_file=output_file)
    else:
        print(f"MCP response file not found: {mcp_file}")
        print("Please run the MCP tool first to extract chapter content")
