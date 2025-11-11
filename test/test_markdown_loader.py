#!/usr/bin/env python3
"""
Tests for markdown loader functionality.
"""
import os
import tempfile
import shutil
from pathlib import Path

# Simple test without external dependencies
def test_markdown_loader():
    """Test markdown directory loading."""
    # Create temporary directory with test markdown files
    test_dir = tempfile.mkdtemp()
    
    try:
        # Create test markdown files
        md1 = Path(test_dir) / "test1.md"
        md1.write_text("""# Test Document 1

This is a test document with multiple sections.

## Section 1

Content for section 1.

## Section 2

Content for section 2.""")
        
        md2 = Path(test_dir) / "test2.md"
        md2.write_text("""---
title: Test Document 2
author: Test Author
---

# Test Document 2

This document has frontmatter.

## Introduction

Some introductory text.""")
        
        # Import the loader
        import sys
        import importlib.util
        
        # Load the module directly from file path
        loader_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'kb_builder', 'markdown_loader.py')
        spec = importlib.util.spec_from_file_location("markdown_loader", loader_path)
        markdown_loader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(markdown_loader)
        
        load_markdown_directory = markdown_loader.load_markdown_directory
        segment_markdown_document = markdown_loader.segment_markdown_document
        load_and_segment_markdown_directory = markdown_loader.load_and_segment_markdown_directory
        
        # Test basic loading
        print("Test 1: Basic markdown loading")
        docs = load_markdown_directory(test_dir, recursive=False)
        assert len(docs) == 2, f"Expected 2 documents, got {len(docs)}"
        assert all('id' in doc and 'text' in doc and 'metadata' in doc for doc in docs)
        print(f"✓ Loaded {len(docs)} documents")
        
        # Test frontmatter extraction
        print("\nTest 2: Frontmatter extraction")
        doc_with_frontmatter = [d for d in docs if d['id'] == 'test2'][0]
        assert 'title' in doc_with_frontmatter['metadata'] or 'title' not in doc_with_frontmatter['text']
        print("✓ Frontmatter handled correctly")
        
        # Test segmentation
        print("\nTest 3: Document segmentation")
        text = md1.read_text()
        segments = segment_markdown_document(text, by_headings=True, min_segment_length=10)
        assert len(segments) > 1, f"Expected multiple segments, got {len(segments)}"
        print(f"✓ Segmented into {len(segments)} chunks")
        
        # Test combined load and segment
        print("\nTest 4: Combined load and segment")
        seg_docs = load_and_segment_markdown_directory(test_dir, recursive=False)
        assert len(seg_docs) >= len(docs), "Segmented documents should be >= original documents"
        print(f"✓ Created {len(seg_docs)} segmented documents from {len(docs)} original documents")
        
        # Test metadata preservation
        print("\nTest 5: Metadata preservation")
        for doc in seg_docs:
            assert 'source' in doc['metadata'], "Source metadata missing"
            assert 'filename' in doc['metadata'], "Filename metadata missing"
        print("✓ Metadata preserved in segmented documents")
        
        print("\n" + "="*50)
        print("All markdown loader tests passed! ✓")
        print("="*50)
        
        return True
        
    finally:
        # Clean up
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    try:
        test_markdown_loader()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
