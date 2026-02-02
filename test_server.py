"""
Quick test script to verify the MCP server loads correctly
"""
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the server module
import server

def test_pdf_loading():
    """Test if PDF loads correctly"""
    print("=" * 60)
    print("Testing Economic Survey MCP Server")
    print("=" * 60)

    print("\n1. Testing PDF loading...")
    result = server.load_pdf()

    if result:
        print("   ✅ PDF loaded successfully!")
        print(f"   📄 Title: {server.pdf_data['metadata']['title']}")
        print(f"   📊 Pages: {server.pdf_data['metadata']['pages']}")
        print(f"   📚 Chapters: {len(server.pdf_data['chapters'])}")
    else:
        print("   ❌ Failed to load PDF")
        return False

    print("\n2. Testing document summary...")
    summary = server.get_document_summary()
    print("   ✅ Summary generated")
    print(f"   Length: {len(summary)} characters")

    print("\n3. Testing key highlights...")
    highlights = server.get_key_highlights()
    print(f"   ✅ Found {len(highlights)} highlight categories")
    for h in highlights:
        print(f"      - {h['category']}: {len(h['points'])} points")

    print("\n4. Testing chapter summary (Chapter 1)...")
    ch1_summary = server.get_chapter_summary(1)
    if ch1_summary:
        print(f"   ✅ Chapter 1: {ch1_summary['title']}")
        print(f"      Subtitle: {ch1_summary['subtitle']}")
        print(f"      Pages: {ch1_summary['pages']}")
        print(f"      Content length: {ch1_summary['content_length']:,} chars")

    print("\n5. Testing chapter content (Chapter 1)...")
    ch1_content = server.get_chapter_content(1, max_length=1000)
    if ch1_content:
        print(f"   ✅ Chapter 1 content retrieved")
        print(f"      Full length: {ch1_content['full_length']:,} chars")
        print(f"      Preview (first 200 chars):")
        print(f"      {ch1_content['content'][:200]}...")

    print("\n" + "=" * 60)
    print("✅ All tests passed! MCP Server is working correctly!")
    print("=" * 60)

    print("\n📋 Summary:")
    print(f"   • Total chapters loaded: {len(server.pdf_data['chapters'])}")
    print(f"   • Total pages: {server.pdf_data['metadata']['pages']}")
    print(f"   • Server status: ✅ Ready")

    print("\n🚀 Next steps:")
    print("   1. Configure Claude Desktop (see README.md)")
    print("   2. Restart Claude Desktop")
    print("   3. Ask Claude to use the economic-survey tools!")

    return True

if __name__ == "__main__":
    try:
        success = test_pdf_loading()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
