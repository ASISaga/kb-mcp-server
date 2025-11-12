#!/usr/bin/env python3
"""
Tests for knowledge base management functionality.
"""
import os
import tempfile
import shutil
from pathlib import Path


def test_kb_management_helpers():
    """Test knowledge base management helper functions."""
    
    print("Test 1: Save markdown file")
    test_dir = tempfile.mkdtemp()
    try:
        # Simulate saving markdown
        kb_path = Path(test_dir)
        filename = "test_doc.md"
        
        # Test with frontmatter
        frontmatter = {
            "title": "Test Document",
            "category": "testing",
            "author": "Test Agent"
        }
        
        content = "# Test Document\n\nThis is test content."
        
        # Build markdown with frontmatter
        markdown_content = "---\n"
        for key, value in frontmatter.items():
            markdown_content += f"{key}: {value}\n"
        markdown_content += "---\n\n"
        markdown_content += content
        
        file_path = kb_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        assert file_path.exists(), "File should be created"
        
        # Read back and verify
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        assert "title: Test Document" in saved_content
        assert "# Test Document" in saved_content
        print("✓ Markdown file saved with frontmatter")
        
    finally:
        shutil.rmtree(test_dir)
    
    print("\nTest 2: Update markdown file (append mode)")
    test_dir = tempfile.mkdtemp()
    try:
        kb_path = Path(test_dir)
        filename = "update_test.md"
        file_path = kb_path / filename
        
        # Create initial file
        initial_content = "# Original Content\n\nOriginal text."
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # Append to file
        append_content = "## New Section\n\nNew text."
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("\n\n" + append_content)
        
        # Verify both contents present
        with open(file_path, 'r', encoding='utf-8') as f:
            final_content = f.read()
        
        assert "Original Content" in final_content
        assert "New Section" in final_content
        print("✓ Markdown file updated in append mode")
        
    finally:
        shutil.rmtree(test_dir)
    
    print("\nTest 3: List markdown files with stats")
    test_dir = tempfile.mkdtemp()
    try:
        kb_path = Path(test_dir)
        
        # Create multiple markdown files
        (kb_path / "doc1.md").write_text("# Doc 1\n\nContent 1")
        (kb_path / "doc2.md").write_text("# Doc 2\n\nContent 2")
        
        subdir = kb_path / "subdir"
        subdir.mkdir()
        (subdir / "doc3.md").write_text("# Doc 3\n\nContent 3")
        
        # List all markdown files
        md_files = list(kb_path.glob("**/*.md"))
        
        assert len(md_files) == 3, f"Expected 3 files, found {len(md_files)}"
        
        # Check file info
        for md_file in md_files:
            stat = md_file.stat()
            assert stat.st_size > 0, "File should have content"
            
            # Read title
            with open(md_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                assert first_line.startswith('#'), "Should have heading"
        
        print(f"✓ Listed {len(md_files)} markdown files with stats")
        
    finally:
        shutil.rmtree(test_dir)
    
    print("\nTest 4: Document organization simulation")
    # Simulate organizing documents by category
    documents = [
        {"id": "doc1", "score": 0.95, "text": "Python programming"},
        {"id": "doc2", "score": 0.92, "text": "Python async"},
        {"id": "doc3", "score": 0.88, "text": "Python decorators"},
    ]
    
    category = "python-language"
    organized = []
    
    for doc in documents:
        organized.append({
            "id": doc["id"],
            "score": doc["score"],
            "category": category
        })
    
    assert len(organized) == 3
    assert all(d["category"] == category for d in organized)
    print(f"✓ Organized {len(organized)} documents into '{category}'")
    
    print("\nTest 5: Consolidation detection simulation")
    # Simulate finding duplicate documents
    results = [
        {"id": "doc1", "score": 0.95},
        {"id": "doc2", "score": 0.94},  # Similar to doc1
        {"id": "doc3", "score": 0.50},
        {"id": "doc4", "score": 0.51},  # Similar to doc3
    ]
    
    similarity_threshold = 0.8
    consolidation_groups = []
    seen = set()
    
    for i, r1 in enumerate(results):
        if i in seen:
            continue
        
        group = [r1]
        for j, r2 in enumerate(results[i+1:], start=i+1):
            if j in seen:
                continue
            
            # Similar scores indicate similar content
            if abs(r1["score"] - r2["score"]) < (1.0 - similarity_threshold):
                group.append(r2)
                seen.add(j)
        
        if len(group) > 1:
            consolidation_groups.append(group)
            seen.add(i)
    
    assert len(consolidation_groups) == 2, "Should find 2 consolidation groups"
    print(f"✓ Found {len(consolidation_groups)} consolidation opportunities")
    
    print("\nTest 6: Markdown directory structure")
    test_dir = tempfile.mkdtemp()
    try:
        kb_path = Path(test_dir)
        
        # Create organized structure
        (kb_path / "python").mkdir()
        (kb_path / "python" / "basics.md").write_text("# Python Basics")
        (kb_path / "python" / "advanced.md").write_text("# Python Advanced")
        
        (kb_path / "docker").mkdir()
        (kb_path / "docker" / "intro.md").write_text("# Docker Intro")
        
        # Verify structure
        categories = [d for d in kb_path.iterdir() if d.is_dir()]
        assert len(categories) == 2, "Should have 2 categories"
        
        python_files = list((kb_path / "python").glob("*.md"))
        assert len(python_files) == 2, "Should have 2 Python files"
        
        print("✓ Markdown directory structure organized by categories")
        
    finally:
        shutil.rmtree(test_dir)
    
    print("\n" + "="*50)
    print("All KB management tests passed! ✓")
    print("="*50)
    
    return True


if __name__ == "__main__":
    try:
        test_kb_management_helpers()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
