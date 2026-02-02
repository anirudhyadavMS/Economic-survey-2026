"""
Process chapter content using AI analysis in Claude Code console
Reads from MCP server output and creates cleaned, structured JSON
"""

import json
import re
import sys
from pathlib import Path

def load_mcp_response(response_file):
    """Load and extract content from MCP tool response"""
    with open(response_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract text from MCP response
    if isinstance(data, list) and len(data) > 0:
        for item in data:
            if item.get('type') == 'text':
                text = item.get('text', '')
                # Remove header and get content
                match = re.search(r'={60,}\n\n(.+)', text, re.DOTALL)
                if match:
                    return match.group(1)
                return text
    return str(data)


def clean_text_line(line):
    """Clean a single line of text"""
    # Remove line numbers at start
    line = re.sub(r'^\s*\d+→', '', line)
    return line.strip()


def is_table_or_chart(text):
    """Check if text is part of a table or chart"""
    indicators = [
        r'^(Chart|Table|Figure|Box)\s+[IVX]+\.\d+',  # Chart II.1, Table I.2
        r'^\s*\d+\s+\d+\s+\d+',  # Multiple numbers (table data)
        r'^(Source|Note):',  # Source/Note lines
        r'^\s*FY\d{2}\s+FY\d{2}',  # Fiscal year headers
        r'^\s*per cent of GDP\s*$',  # Column headers
        r'^\s*₹ Lakh Crore\s*$',  # Column headers
    ]

    for pattern in indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def extract_section_number(text):
    """Extract section number from text"""
    match = re.match(r'^(\d+\.\d+)\s+', text)
    if match:
        return match.group(1)
    return None


def process_chapter_content(content, chapter_num):
    """Process raw content into structured format"""

    lines = content.split('\n')

    # Initialize structure
    result = {
        "chapter_number": chapter_num,
        "chapter_title": "",
        "summary": [],
        "sections": [],
        "references": []
    }

    current_section = None
    current_paragraph = ""
    in_table_chart = False
    skip_lines = 0
    found_first_section = False

    for i, line in enumerate(lines):
        # Skip if we're in skip mode
        if skip_lines > 0:
            skip_lines -= 1
            continue

        line = clean_text_line(line)

        if not line or len(line) < 3:
            continue

        # Extract chapter title (large all-caps text at start)
        if not result["chapter_title"] and line.isupper() and len(line) > 10:
            if not re.match(r'^CHAPTER', line) and not re.match(r'^\d+$', line):
                result["chapter_title"] = line
                continue

        # Check for table/chart markers
        if is_table_or_chart(line):
            in_table_chart = True
            skip_lines = 10  # Skip next 10 lines
            continue

        # References
        if re.match(r'^(Source|Note):', line, re.IGNORECASE):
            result["references"].append(line)
            continue

        # Check for section markers
        section_num = extract_section_number(line)
        if section_num and section_num.startswith(f"{chapter_num}."):
            # Save previous section
            if current_section and current_paragraph:
                current_section["content"].append({
                    "type": "paragraph",
                    "text": current_paragraph.strip()
                })
                current_paragraph = ""
            if current_section:
                result["sections"].append(current_section)

            # Start new section
            found_first_section = True
            title = re.sub(r'^\d+\.\d+\s+', '', line).strip()
            current_section = {
                "section_id": section_num,
                "title": title[:100] + "..." if len(title) > 100 else title,
                "content": []
            }
            in_table_chart = False
            continue

        # Skip if in table/chart mode
        if in_table_chart:
            continue

        # Check if it's a heading (ALL CAPS or starts with capital and short)
        is_heading = (line.isupper() and 10 < len(line) < 100) or \
                     (line.startswith(('INTRODUCTION', 'CENTRAL', 'Trends', 'Box')))

        if is_heading:
            # Save previous paragraph
            if current_paragraph:
                if current_section:
                    current_section["content"].append({
                        "type": "paragraph",
                        "text": current_paragraph.strip()
                    })
                elif not found_first_section:
                    # Before first section = summary
                    result["summary"].append(current_paragraph.strip())
                current_paragraph = ""

            # Add heading
            if current_section:
                current_section["content"].append({
                    "type": "heading",
                    "text": line
                })
            continue

        # Regular paragraph text - accumulate
        if current_paragraph and not current_paragraph.endswith(('.', ':', '?', '!')):
            # Join broken sentences
            current_paragraph += " " + line
        else:
            # Start new paragraph or finish previous
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

    # Deduplicate references
    result["references"] = list(dict.fromkeys(result["references"]))

    return result


def main():
    """Main processing function"""

    # Path to MCP response file
    mcp_file = Path("C:/Users/anirudhyadav/.claude/projects/C--Users-anirudhyadav/4136eb76-3614-4a80-a572-fc927f9f269c/tool-results/mcp-economic-survey-get_chapter_content-1770008160120.txt")

    if not mcp_file.exists():
        print(f"Error: MCP response file not found: {mcp_file}")
        print("Please run the MCP tool first to get chapter content")
        return

    print("Loading chapter content from MCP response...")
    content = load_mcp_response(mcp_file)

    print(f"Processing {len(content):,} characters...")

    # Process chapter 2
    result = process_chapter_content(content, chapter_num=2)

    # Add metadata
    result["metadata"] = {
        "extraction_method": "ai_claude_code_console",
        "structure": {
            "sections_count": len(result["sections"]),
            "summary_paragraphs": len(result["summary"]),
            "references": len(result["references"])
        }
    }

    # Save result
    output_file = Path(__file__).parent / "output" / "chapter_02_cleaned_by_ai.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"\nChapter: {result['chapter_number']} - {result['chapter_title']}")
    print(f"Summary paragraphs: {len(result['summary'])}")
    print(f"Sections: {len(result['sections'])}")
    print(f"References: {len(result['references'])}")
    print(f"\nOutput saved to: {output_file}")

    # Show first 3 sections
    print(f"\nFirst 3 sections:")
    for i, section in enumerate(result['sections'][:3], 1):
        print(f"  {i}. {section['section_id']}: {section['title']}")
        print(f"     Content blocks: {len(section['content'])}")


if __name__ == "__main__":
    main()
