"""
Test script for AI-powered chapter extraction
Run this to test the AI extraction feature
"""

import os
import json
import sys
from pathlib import Path

# Set UTF-8 encoding for console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from server import load_pdf, get_chapter_content


def check_setup():
    """Check if API key is configured"""
    print("=" * 60)
    print("AI Extraction Setup Check")
    print("=" * 60)

    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("[X] ANTHROPIC_API_KEY not found")
        print()
        print("To set up:")
        print("1. Get key from: https://console.anthropic.com/settings/keys")
        print("2. Set environment variable:")
        print("   Windows: set ANTHROPIC_API_KEY=your-key-here")
        print("   Linux/Mac: export ANTHROPIC_API_KEY=your-key-here")
        print()
        print("Or create .env file:")
        print("   Copy .env.example to .env and add your key")
        print()
        return False

    print(f"[OK] API key found: {api_key[:8]}...{api_key[-4:]}")
    return True


def test_extraction(chapter_id=1):
    """Test AI extraction on a specific chapter"""
    print(f"\nTesting AI extraction on Chapter {chapter_id}...")
    print("-" * 60)

    # Load PDF
    print("Loading PDF...")
    if not load_pdf():
        print("[X] Failed to load PDF")
        return
    print("[OK] PDF loaded")

    # Extract chapter
    print(f"\nExtracting Chapter {chapter_id} with AI...")
    result = get_chapter_content(
        chapter_id=chapter_id,
        save_to_file=True,
        output_format='json'
    )

    if not result:
        print("[X] Extraction failed")
        return

    # Check if files were created
    json_file = [f for f in result.get('files', []) if f['format'] == 'json']
    if not json_file:
        print("[X] No JSON file created")
        return

    json_path = json_file[0]['path']
    print(f"[OK] JSON file created: {json_path}")

    # Load and analyze the result
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n" + "=" * 60)
    print("EXTRACTION RESULTS")
    print("=" * 60)

    metadata = data.get('metadata', {})
    structure = metadata.get('structure', {})

    print(f"\nExtraction Method: {metadata.get('extraction_method', 'unknown').upper()}")

    if metadata.get('extraction_method') == 'ai':
        print("[OK] AI extraction successful!")
    else:
        print("[!] Fell back to manual extraction")

    print("\nStructure Statistics:")
    print(f"  Sections: {structure.get('sections_count', 0)}")
    print(f"  Summary Paragraphs: {structure.get('summary_paragraphs', 0)}")
    print(f"  Total Content Blocks: {structure.get('total_content_blocks', 0)}")
    print(f"  Headings: {structure.get('headings', 0)}")
    print(f"  Paragraphs: {structure.get('paragraphs', 0)}")
    print(f"  References: {structure.get('references', 0)}")

    # Show sample content
    structured = data.get('content', {}).get('structured', {})

    if structured:
        print("\n" + "=" * 60)
        print("SAMPLE CONTENT")
        print("=" * 60)

        # Chapter info
        print(f"\nChapter: {structured.get('chapter_number', 'N/A')}")
        print(f"Title: {structured.get('chapter_title', 'N/A')}")

        # Summary
        summary = structured.get('summary', [])
        if summary:
            print(f"\nSummary ({len(summary)} paragraphs):")
            print(f"  {summary[0][:100]}..." if summary else "  (none)")

        # Sections
        sections = structured.get('sections', [])
        if sections:
            print(f"\nFirst 3 Sections:")
            for i, section in enumerate(sections[:3], 1):
                title = section.get('title', '')[:60]
                print(f"  {i}. {section.get('section_id')}: {title}...")

        # References
        references = structured.get('references', [])
        if references:
            print(f"\nReferences ({len(references)} total):")
            if isinstance(references[0], dict):
                ref_text = references[0].get('text', '')[:80]
            else:
                ref_text = str(references[0])[:80]
            print(f"  {ref_text}...")

    print("\n" + "=" * 60)
    print("Test complete! Check the output file for full content.")
    print("=" * 60)


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Economic Survey AI Extraction Test")
    print("=" * 60)

    # Check setup
    if not check_setup():
        print("\n[X] Please set up your API key first (see instructions above)")
        print("\n[!] Will proceed with manual extraction as fallback...")
        print()

    # Test extraction
    print("\n" + "=" * 60)
    print("Testing Extraction")
    print("=" * 60)

    try:
        # Test Chapter 2 as requested
        test_extraction(chapter_id=2)
    except Exception as e:
        print(f"\n[X] Error during extraction: {e}")
        import traceback
        traceback.print_exc()

    print("\n[OK] Test complete!")
    print("\nNext steps:")
    print("1. Review the output in: output/chapter_02_*.json")
    print("2. Try other chapters if needed")
    print("3. Set up API key for AI extraction (see ANTHROPIC_API_KEY)")


if __name__ == "__main__":
    main()
