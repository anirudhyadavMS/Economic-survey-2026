"""
AI-powered chapter cleaning using Claude Code console
Extracts content from MCP server, then uses AI to clean and structure it
"""

import json
import re
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def extract_raw_text_from_mcp_response(response_file):
    """Extract raw text content from MCP tool response file"""
    with open(response_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # MCP response is a JSON array with content
    if isinstance(data, list) and len(data) > 0:
        # Find the text content
        for item in data:
            if item.get('type') == 'text':
                text = item.get('text', '')
                # Extract content after "Content Length:" line
                match = re.search(r'Content Length:.*?\n={60,}\n\n(.+)', text, re.DOTALL)
                if match:
                    return match.group(1)
                return text

    return str(data)


def split_into_chunks(text, chunk_size=40000):
    """Split text into chunks for processing"""
    # Try to split on section boundaries (numbered sections like 2.1, 2.2)
    sections = re.split(r'(\n\d+\.\d+\s+)', text)

    chunks = []
    current_chunk = ""

    for i, part in enumerate(sections):
        if len(current_chunk) + len(part) < chunk_size:
            current_chunk += part
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = part

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def create_cleaning_prompt(text, chapter_num, is_first_chunk=False):
    """Create prompt for AI to clean and structure the content"""

    base_instructions = f"""You are cleaning and structuring Chapter {chapter_num} from India's Economic Survey 2025-26.

TASK: Clean and structure this content following these rules:

1. **REMOVE completely**:
   - All tables (remove table headers, data rows, everything)
   - All charts (Chart I.1, Chart 2.3, etc. - remove titles and descriptions)
   - All figures (Figure 2.1, etc.)
   - All boxes (Box 2.1, etc.)
   - Headers and footers (page numbers, running headers)
   - Source/Note lines that reference charts/tables

2. **CLEAN text**:
   - Join broken sentences across lines
   - Remove excessive whitespace and newlines
   - Fix formatting artifacts
   - Keep only substantive paragraphs

3. **STRUCTURE**:
   - Identify numbered sections ({chapter_num}.1, {chapter_num}.2, etc.)
   - For each section: extract section number and title (first sentence)
   - Organize content into paragraphs
   - Identify headings (ALL CAPS or bold text indicators)

4. **OUTPUT** as JSON:
```json
{{
  "sections": [
    {{
      "section_id": "{chapter_num}.1",
      "title": "Brief section title from first line",
      "content": [
        {{
          "type": "heading|paragraph",
          "text": "Clean, complete text"
        }}
      ]
    }}
  ],
  "references": ["Source: ...", "Note: ..."]
}}
```

IMPORTANT:
- Return ONLY valid JSON
- No markdown code fences
- No explanatory text
- Just the JSON object

"""

    if is_first_chunk:
        extra = f"""
SPECIAL for first chunk:
- Extract the chapter title and summary
- Summary = intro paragraphs BEFORE first numbered section ({chapter_num}.1)
- Include these in output:
```json
{{
  "chapter_title": "Full chapter title",
  "summary": ["Paragraph 1", "Paragraph 2", ...],
  "sections": [...],
  "references": [...]
}}
```
"""
        base_instructions += extra

    base_instructions += f"\n\nCONTENT TO PROCESS:\n\n{text}"

    return base_instructions


def clean_chapter_with_ai(chapter_id):
    """
    Clean a chapter using AI from Claude Code console

    This function guides the user to:
    1. Get raw content from MCP server
    2. Process it in chunks
    3. Use AI (in Claude Code console) to clean each chunk
    4. Assemble the final result
    """

    print("=" * 70)
    print(f"AI CHAPTER CLEANING - Chapter {chapter_id}")
    print("=" * 70)
    print()
    print("This script helps you clean chapter content using AI in Claude Code.")
    print()
    print("STEPS:")
    print("1. Extract raw content from MCP server")
    print("2. Split into manageable chunks")
    print("3. Generate cleaning prompts for Claude Code")
    print("4. Process each chunk")
    print("5. Assemble final structured output")
    print()

    # Check if we have the MCP response file
    tool_results_dir = Path.home() / ".claude" / "projects"
    print(f"Looking for MCP response files in: {tool_results_dir}")
    print()

    # For now, create a template for manual processing
    output_dir = Path(__file__).parent / "output"
    prompt_file = output_dir / f"chapter_{chapter_id:02d}_cleaning_prompts.txt"

    print(f"Generated prompts will be saved to: {prompt_file}")
    print()
    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. In Claude Code console, run:")
    print(f"   mcp__economic-survey__get_chapter_content(chapter_id={chapter_id})")
    print()
    print("2. Copy the content text (not the JSON wrapper)")
    print()
    print("3. Save it to: chapter_2_raw.txt")
    print()
    print("4. Run this script again with the raw file")
    print()


if __name__ == "__main__":
    chapter_id = 2
    if len(sys.argv) > 1:
        chapter_id = int(sys.argv[1])

    clean_chapter_with_ai(chapter_id)
