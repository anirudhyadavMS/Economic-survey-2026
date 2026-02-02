"""
Bulk processor for all Economic Survey chapters and front matter
Processes: Preface, Acknowledgments, and all 17 chapters
"""

import json
import sys
from pathlib import Path
import fitz  # PyMuPDF
from ai_processor_enhanced import EconomicSurveyProcessor

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Chapter definitions
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

PDF_PATH = Path(__file__).parent / "data" / "economic-survey-2025-26.pdf"


def process_all_chapters():
    """Process all 17 chapters with enhanced AI"""

    print("="*70)
    print("BULK PROCESSING: All Chapters")
    print("="*70)

    # Load PDF
    print("\n[1/3] Loading PDF...")
    doc = fitz.open(str(PDF_PATH))
    print(f"[OK] PDF loaded: {doc.page_count} pages")

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    results = []

    # Process all 17 chapters
    print(f"\n[2/3] Processing {len(CHAPTERS)} chapters...")
    print("-"*70)

    for chapter_id in sorted(CHAPTERS.keys()):
        chapter_info = CHAPTERS[chapter_id]

        print(f"\nChapter {chapter_id}: {chapter_info['title']}...")

        # Extract raw text from PDF
        start_page, end_page = chapter_info["pages"]
        raw_text = []
        for page_num in range(start_page - 1, min(end_page, doc.page_count)):
            page = doc[page_num]
            text = page.get_text()
            raw_text.append(text)
        raw_content = "\n".join(raw_text)

        # Process with enhanced AI
        processor = EconomicSurveyProcessor(chapter_id)
        result = processor.process_chapter(
            raw_content=raw_content,
            chapter_title=chapter_info["title"],
            chapter_subtitle=chapter_info["subtitle"]
        )

        # Add metadata
        result["metadata"] = {
            "extraction_method": "mcp_raw + ai_intelligent_processing",
            "pages": {
                "start": chapter_info["pages"][0],
                "end": chapter_info["pages"][1]
            },
            "structure": {
                "sections_count": len(result["sections"]),
                "summary_paragraphs": len(result["summary"]),
                "references": len(result["references"])
            }
        }

        # Save
        filename = f"chapter_{chapter_id:02d}_{chapter_info['title'].lower().replace(' ', '_').replace('&', 'and')}.json"
        output_file = output_dir / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        results.append({
            "chapter_id": chapter_id,
            "title": chapter_info["title"],
            "sections": len(result["sections"]),
            "summary": len(result["summary"]),
            "file": str(output_file)
        })

        print(f"  [OK] Saved: {filename}")
        print(f"    Summary: {len(result['summary'])} paragraphs, Sections: {len(result['sections'])}")

    # Summary
    print("\n" + "="*70)
    print("[3/3] PROCESSING COMPLETE")
    print("="*70)

    print(f"\n[OK] Processed {len(results)} chapters")
    print(f"[OK] All files saved to: {output_dir}")

    # Statistics
    total_sections = sum(r["sections"] for r in results)
    total_summary = sum(r["summary"] for r in results)

    print(f"\nStatistics:")
    print(f"  Total sections: {total_sections}")
    print(f"  Total summary paragraphs: {total_summary}")
    print(f"  Average sections per chapter: {total_sections/len(results):.1f}")

    # Create summary file
    summary_file = output_dir / "_processing_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "processed_date": "2026-02-02",
            "total_chapters": len(results),
            "method": "mcp_raw + ai_intelligent_processing",
            "chapters": results,
            "statistics": {
                "total_sections": total_sections,
                "total_summary_paragraphs": total_summary,
                "avg_sections_per_chapter": round(total_sections/len(results), 1)
            }
        }, f, indent=2)

    print(f"\n[OK] Summary saved to: {summary_file}")

    doc.close()
    return results


def process_front_matter():
    """Process front matter sections (Preface, Acknowledgments)"""

    print("\n" + "="*70)
    print("PROCESSING FRONT MATTER")
    print("="*70)

    # Front matter page ranges
    front_matter = {
        "preface": {"title": "Preface", "pages": (8, 16)},
        "acknowledgments": {"title": "Acknowledgments", "pages": (18, 19)}
    }

    output_dir = Path(__file__).parent / "output"

    # Load PDF
    doc = fitz.open(str(PDF_PATH))

    for key, info in front_matter.items():
        print(f"\nProcessing {info['title']}...")

        # Extract raw text
        start_page, end_page = info["pages"]
        raw_text = []

        for page_num in range(start_page - 1, min(end_page, doc.page_count)):
            page = doc[page_num]
            text = page.get_text()
            raw_text.append(text)

        raw_content = "\n".join(raw_text)

        # Process (simplified - no section structure)
        lines = raw_content.split('\n')
        paragraphs = []
        current_para = ""

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Skip page numbers
            if line.isdigit():
                continue

            # Join sentences
            if current_para and not current_para.endswith(('.', '!', '?', ':')):
                current_para += " " + line
            else:
                if current_para:
                    paragraphs.append(current_para)
                current_para = line

        if current_para:
            paragraphs.append(current_para)

        # Save
        result = {
            "section": key,
            "title": info["title"],
            "pages": {
                "start": start_page,
                "end": end_page
            },
            "content": paragraphs,
            "metadata": {
                "extraction_method": "mcp_raw + ai_simple_processing",
                "paragraph_count": len(paragraphs)
            }
        }

        filename = f"front_matter_{key}.json"
        output_file = output_dir / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"  [OK] Saved: {filename}")
        print(f"    Paragraphs: {len(paragraphs)}")

    doc.close()

    print(f"\n[OK] Front matter processing complete")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ECONOMIC SURVEY 2025-26 - COMPLETE EXTRACTION")
    print("="*70)
    print("\nThis will process:")
    print("  • Preface")
    print("  • Acknowledgments")
    print("  • All 17 Chapters")
    print("\nEstimated time: ~2-3 minutes")
    print("="*70)

    input("\nPress ENTER to start processing...")

    try:
        # Process front matter
        process_front_matter()

        # Process all chapters
        results = process_all_chapters()

        print("\n" + "="*70)
        print("[OK][OK][OK] ALL PROCESSING COMPLETE [OK][OK][OK]")
        print("="*70)
        print(f"\nCheck the 'output' folder for all JSON files.")

    except Exception as e:
        print(f"\n[X] ERROR: {e}")
        import traceback
        traceback.print_exc()
