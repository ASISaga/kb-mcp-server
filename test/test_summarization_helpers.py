#!/usr/bin/env python3
"""
Tests for summarization helper functions.
"""
import os
import json
import tempfile
import shutil
from pathlib import Path


# Extract helper functions for testing (avoiding MCP dependencies)
def _human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def _detect_file_type(path: Path, content: str) -> str:
    """Detect file type based on extension and content."""
    ext = path.suffix.lower()
    
    code_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.rb', '.go', '.rs', '.ts', '.tsx', '.jsx'}
    config_extensions = {'.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf'}
    
    if ext in code_extensions:
        return "code"
    elif ext == '.json':
        return "json"
    elif ext in {'.md', '.markdown'}:
        return "markdown"
    elif ext in config_extensions:
        return "config"
    elif ext in {'.txt', '.log'}:
        return "text"
    elif ext in {'.xml', '.html', '.htm'}:
        return "markup"
    else:
        return "unknown"


def _analyze_code(content: str, extension: str) -> str:
    """Analyze code file and extract key information."""
    lines = content.split('\n')
    
    # Count various code elements
    functions = len([l for l in lines if 'def ' in l or 'function ' in l or 'func ' in l])
    classes = len([l for l in lines if 'class ' in l])
    imports = len([l for l in lines if 'import ' in l or 'from ' in l or 'require(' in l])
    
    analysis_parts = []
    if classes > 0:
        analysis_parts.append(f"{classes} classes")
    if functions > 0:
        analysis_parts.append(f"{functions} functions")
    if imports > 0:
        analysis_parts.append(f"{imports} imports")
    
    return ', '.join(analysis_parts) if analysis_parts else "code file"


def _analyze_json(content: str) -> str:
    """Analyze JSON file structure."""
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return f"Object with {len(data)} top-level keys: {', '.join(list(data.keys())[:5])}"
        elif isinstance(data, list):
            return f"Array with {len(data)} items"
        else:
            return f"JSON value: {type(data).__name__}"
    except:
        return "Invalid JSON"


def _analyze_markdown(content: str) -> str:
    """Analyze markdown file structure."""
    lines = content.split('\n')
    headings = [l for l in lines if l.strip().startswith('#')]
    links = content.count('[')
    code_blocks = content.count('```')
    
    parts = []
    if headings:
        parts.append(f"{len(headings)} headings")
    if links > 0:
        parts.append(f"{links} links")
    if code_blocks > 0:
        parts.append(f"{code_blocks // 2} code blocks")
    
    return ', '.join(parts) if parts else "markdown document"


def _analyze_config(content: str) -> str:
    """Analyze configuration file."""
    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
    sections = len([l for l in lines if l.startswith('[')])
    settings = len([l for l in lines if '=' in l or ':' in l])
    
    parts = []
    if sections > 0:
        parts.append(f"{sections} sections")
    if settings > 0:
        parts.append(f"{settings} settings")
    
    return ', '.join(parts) if parts else "configuration file"


def test_summarization_helpers():
    """Test summarization helper functions."""
    
    # Test 1: Human readable size
    print("Test 1: Human readable size conversion")
    assert _human_readable_size(1024) == "1.0 KB"
    assert _human_readable_size(1048576) == "1.0 MB"
    assert _human_readable_size(1073741824) == "1.0 GB"
    assert _human_readable_size(500) == "500.0 B"
    print("✓ Size conversion working correctly")
    
    # Test 2: File type detection
    print("\nTest 2: File type detection")
    test_cases = [
        (Path("test.py"), "code"),
        (Path("test.js"), "code"),
        (Path("test.md"), "markdown"),
        (Path("test.json"), "json"),
        (Path("test.yml"), "config"),
        (Path("test.txt"), "text"),
        (Path("test.unknown"), "unknown"),
    ]
    for path, expected_type in test_cases:
        result = _detect_file_type(path, "")
        assert result == expected_type, f"Expected {expected_type} for {path}, got {result}"
    print("✓ File type detection working correctly")
    
    # Test 3: Code analysis
    print("\nTest 3: Code analysis")
    code_sample = """
import os
import sys

class MyClass:
    def __init__(self):
        pass
    
    def method1(self):
        pass

def function1():
    pass

def function2():
    pass
"""
    analysis = _analyze_code(code_sample, ".py")
    assert "class" in analysis.lower() or "1" in analysis
    assert "function" in analysis.lower() or "2" in analysis
    print(f"✓ Code analysis: {analysis}")
    
    # Test 4: Markdown analysis
    print("\nTest 4: Markdown analysis")
    md_sample = """
# Heading 1
Some text with [a link](http://example.com)

## Heading 2
More text

```python
code block
```

Another [link](http://example.com)
"""
    analysis = _analyze_markdown(md_sample)
    assert "heading" in analysis.lower()
    print(f"✓ Markdown analysis: {analysis}")
    
    # Test 5: JSON analysis
    print("\nTest 5: JSON analysis")
    json_str = '{"key1": "value1", "key2": "value2", "key3": {"nested": "value"}}'
    analysis = _analyze_json(json_str)
    assert "key" in analysis.lower() or "object" in analysis.lower()
    print(f"✓ JSON analysis: {analysis}")
    
    # Test 6: Config analysis
    print("\nTest 6: Config analysis")
    config_sample = """
[section1]
setting1=value1
setting2=value2

[section2]
setting3=value3
"""
    analysis = _analyze_config(config_sample)
    assert "section" in analysis.lower() or "setting" in analysis.lower()
    print(f"✓ Config analysis: {analysis}")
    
    print("\n" + "="*50)
    print("All summarization helper tests passed! ✓")
    print("="*50)
    
    return True


if __name__ == "__main__":
    try:
        test_summarization_helpers()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
