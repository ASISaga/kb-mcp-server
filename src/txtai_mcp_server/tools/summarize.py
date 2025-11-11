"""
Summarization tools for the txtai MCP server.

Provides concise summarization of various content types to help AI agents
manage context size and focus on critical information.
"""
import logging
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field

from ..core.state import get_txtai_app

logger = logging.getLogger(__name__)


def register_summarize_tools(mcp: FastMCP) -> None:
    """Register summarization tools with the MCP server."""
    logger.debug("Starting registration of summarization tools...")

    @mcp.tool(
        name="summarize_text",
        description="""Summarize text content to a concise form.
        
        Best used for:
        - Condensing long command outputs to focus on key information
        - Creating brief overviews of lengthy documents
        - Extracting main points from verbose text
        - Preventing context overflow in AI agents
        
        The summarization uses AI to understand the content and extract the most
        important information while maintaining meaning.
        
        Example: Summarize a 1000-line log file to highlight errors and warnings."""
    )
    async def summarize_text(
        ctx: Context,
        text: str,
        max_length: Optional[int] = Field(500, description="Maximum length of summary in words"),
        focus: Optional[str] = Field(None, description="Optional focus area (e.g., 'errors', 'warnings', 'key findings')")
    ) -> str:
        """Summarize text content using AI-powered summarization."""
        logger.info(f"Summarize text request - length: {len(text)}, max_length: {max_length}, focus: {focus}")
        
        try:
            app = get_txtai_app()
            
            # Build a prompt for summarization
            prompt = f"Summarize the following text concisely"
            if focus:
                prompt += f", focusing on {focus}"
            prompt += f" in approximately {max_length} words or less:\n\n{text}"
            
            # Check if the app has a summary pipeline configured
            if hasattr(app, 'pipelines') and 'summary' in app.pipelines:
                # Use txtai's summary pipeline if available
                summary = app.pipelines['summary'](text, maxlength=max_length)
                return summary
            
            # Fallback: Use extractor (Q&A) to generate summary
            if hasattr(app, 'pipelines') and 'extractor' in app.pipelines:
                question = f"What are the main points of this text?"
                if focus:
                    question = f"What are the main points related to {focus} in this text?"
                answers = app.pipelines['extractor']([question], [text])
                if answers and len(answers) > 0:
                    return f"Summary: {answers[0][1]}"
            
            # If no pipelines available, return truncated version with metadata
            words = text.split()
            if len(words) <= max_length:
                return f"Text (already concise, {len(words)} words):\n{text}"
            
            # Simple truncation with ellipsis
            truncated = ' '.join(words[:max_length])
            return f"Summary ({max_length} of {len(words)} words):\n{truncated}..."
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}", exc_info=True)
            return f"Error summarizing text: {str(e)}"

    @mcp.tool(
        name="summarize_file",
        description="""Analyze and summarize the contents of a file.
        
        Best used for:
        - Getting quick overviews of code files
        - Understanding configuration files
        - Analyzing log files for key information
        - Previewing document contents
        
        Supports various file types including text, code, markdown, JSON, and more.
        Provides technical analysis highlighting the file's purpose and key elements.
        
        Example: Summarize a Python file to understand its main functions and classes."""
    )
    async def summarize_file(
        ctx: Context,
        file_path: str,
        max_length: Optional[int] = Field(300, description="Maximum length of summary in words"),
        include_metadata: Optional[bool] = Field(True, description="Include file metadata (size, type, etc.)")
    ) -> str:
        """Analyze and summarize file contents with technical insights."""
        logger.info(f"Summarize file request - path: {file_path}, max_length: {max_length}")
        
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                return f"Error: File not found: {file_path}"
            
            if not path.is_file():
                return f"Error: Path is not a file: {file_path}"
            
            # Collect metadata
            metadata = {}
            if include_metadata:
                stat = path.stat()
                metadata = {
                    "file": str(path),
                    "size_bytes": stat.st_size,
                    "size_human": _human_readable_size(stat.st_size),
                    "extension": path.suffix,
                    "name": path.name
                }
            
            # Read file content
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Binary file
                return json.dumps({
                    "type": "binary_file",
                    "metadata": metadata,
                    "summary": f"Binary file: {path.suffix or 'unknown'} format"
                }, indent=2)
            
            # Analyze based on file type
            file_type = _detect_file_type(path, content)
            
            # Generate summary
            summary_parts = []
            
            if include_metadata:
                summary_parts.append(f"File: {metadata['name']} ({metadata['size_human']})")
                summary_parts.append(f"Type: {file_type}")
            
            # Add content-specific analysis
            if file_type == "code":
                analysis = _analyze_code(content, path.suffix)
                summary_parts.append(f"Analysis: {analysis}")
            elif file_type == "json":
                analysis = _analyze_json(content)
                summary_parts.append(f"Structure: {analysis}")
            elif file_type == "markdown":
                analysis = _analyze_markdown(content)
                summary_parts.append(f"Content: {analysis}")
            elif file_type == "config":
                analysis = _analyze_config(content)
                summary_parts.append(f"Configuration: {analysis}")
            
            # Add content preview/summary
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Extract key lines (non-empty, non-comment)
            key_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
            
            if total_lines <= 50:
                summary_parts.append(f"Content ({total_lines} lines):")
                summary_parts.append(content[:500] + ("..." if len(content) > 500 else ""))
            else:
                # For larger files, show statistics and sample
                summary_parts.append(f"Statistics: {total_lines} total lines, {len(key_lines)} content lines")
                summary_parts.append(f"Preview (first 10 lines):")
                summary_parts.append('\n'.join(lines[:10]))
            
            return '\n'.join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error summarizing file: {e}", exc_info=True)
            return f"Error summarizing file: {str(e)}"

    @mcp.tool(
        name="summarize_directory",
        description="""Provide an overview of a directory structure.
        
        Best used for:
        - Understanding project organization
        - Getting quick overview of codebases
        - Analyzing folder hierarchies
        - Identifying key files and directories
        
        Shows directory tree with file counts, sizes, and key file identification.
        Optimized output prevents context overflow for large directory structures.
        
        Example: Summarize a project directory to understand its structure."""
    )
    async def summarize_directory(
        ctx: Context,
        directory_path: str,
        max_depth: Optional[int] = Field(3, description="Maximum depth to traverse"),
        include_hidden: Optional[bool] = Field(False, description="Include hidden files and directories"),
        file_extensions: Optional[str] = Field(None, description="Comma-separated list of extensions to focus on (e.g., '.py,.js')")
    ) -> str:
        """Analyze and summarize directory structure."""
        logger.info(f"Summarize directory request - path: {directory_path}, max_depth: {max_depth}")
        
        try:
            path = Path(directory_path).expanduser()
            
            if not path.exists():
                return f"Error: Directory not found: {directory_path}"
            
            if not path.is_dir():
                return f"Error: Path is not a directory: {directory_path}"
            
            # Parse extensions filter
            extensions_filter = None
            if file_extensions:
                extensions_filter = set(ext.strip() for ext in file_extensions.split(','))
            
            # Analyze directory
            stats = _analyze_directory(path, max_depth, include_hidden, extensions_filter)
            
            # Build summary
            summary = []
            summary.append(f"Directory: {path}")
            summary.append(f"Total Size: {_human_readable_size(stats['total_size'])}")
            summary.append(f"Files: {stats['file_count']}, Directories: {stats['dir_count']}")
            
            # File type breakdown
            if stats['file_types']:
                summary.append("\nFile Types:")
                sorted_types = sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)
                for ext, count in sorted_types[:10]:  # Top 10 types
                    summary.append(f"  {ext or 'no extension'}: {count} files")
            
            # Largest files
            if stats['largest_files']:
                summary.append("\nLargest Files:")
                for file_path, size in stats['largest_files'][:5]:  # Top 5
                    rel_path = file_path.relative_to(path)
                    summary.append(f"  {rel_path} ({_human_readable_size(size)})")
            
            # Directory tree (limited depth)
            summary.append("\nDirectory Structure:")
            tree = _build_tree(path, max_depth, include_hidden, extensions_filter, current_depth=0)
            summary.append(tree)
            
            return '\n'.join(summary)
            
        except Exception as e:
            logger.error(f"Error summarizing directory: {e}", exc_info=True)
            return f"Error summarizing directory: {str(e)}"

    @mcp.tool(
        name="summarize_search_results",
        description="""Summarize search results from the knowledge base.
        
        Best used for:
        - Creating concise overviews from multiple search results
        - Extracting common themes across documents
        - Generating executive summaries from search findings
        - Consolidating information from diverse sources
        
        Takes search results and creates a coherent summary highlighting key insights.
        
        Example: Summarize 20 search results about 'machine learning' into key concepts."""
    )
    async def summarize_search_results(
        ctx: Context,
        query: str,
        limit: Optional[int] = Field(10, description="Number of search results to retrieve and summarize"),
        max_summary_length: Optional[int] = Field(400, description="Maximum length of final summary in words")
    ) -> str:
        """Search knowledge base and create summary of results."""
        logger.info(f"Summarize search results request - query: {query}, limit: {limit}")
        
        try:
            app = get_txtai_app()
            
            # Perform search
            results = app.search(query, limit=limit)
            
            if not results:
                return f"No search results found for query: {query}"
            
            # Extract text from results
            texts = []
            for result in results:
                if isinstance(result, dict) and 'text' in result:
                    texts.append(result['text'])
            
            if not texts:
                return f"No text content found in search results for query: {query}"
            
            # Combine texts
            combined_text = "\n\n".join(texts)
            
            # Generate summary using the app's capabilities
            summary_prompt = f"Based on these search results for '{query}', provide a comprehensive summary of the key information:\n\n{combined_text}"
            
            # Use extractor if available
            if hasattr(app, 'pipelines') and 'extractor' in app.pipelines:
                question = f"What are the main points about {query} from these search results?"
                answers = app.pipelines['extractor']([question], [combined_text])
                if answers and len(answers) > 0:
                    return f"Summary of {len(texts)} search results for '{query}':\n\n{answers[0][1]}"
            
            # Fallback: Return truncated combined results
            words = combined_text.split()
            if len(words) <= max_summary_length:
                return f"Search Results Summary for '{query}' ({len(texts)} documents):\n\n{combined_text}"
            
            truncated = ' '.join(words[:max_summary_length])
            return f"Search Results Summary for '{query}' ({len(texts)} documents, showing {max_summary_length} of {len(words)} words):\n\n{truncated}..."
            
        except Exception as e:
            logger.error(f"Error summarizing search results: {e}", exc_info=True)
            return f"Error summarizing search results: {str(e)}"

    logger.info("Registered summarization tools successfully")


# Helper functions

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
    comments = len([l for l in lines if l.strip().startswith('#') or l.strip().startswith('//') or l.strip().startswith('/*')])
    
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


def _analyze_directory(path: Path, max_depth: int, include_hidden: bool, extensions_filter: Optional[set], current_depth: int = 0) -> Dict[str, Any]:
    """Recursively analyze directory structure."""
    stats = {
        'total_size': 0,
        'file_count': 0,
        'dir_count': 0,
        'file_types': {},
        'largest_files': []
    }
    
    try:
        for item in path.iterdir():
            # Skip hidden files if not included
            if not include_hidden and item.name.startswith('.'):
                continue
            
            if item.is_file():
                # Apply extension filter
                if extensions_filter and item.suffix not in extensions_filter:
                    continue
                
                stats['file_count'] += 1
                size = item.stat().st_size
                stats['total_size'] += size
                
                # Track file types
                ext = item.suffix or 'no extension'
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
                # Track largest files
                stats['largest_files'].append((item, size))
                
            elif item.is_dir() and current_depth < max_depth:
                stats['dir_count'] += 1
                # Recurse into subdirectory
                sub_stats = _analyze_directory(item, max_depth, include_hidden, extensions_filter, current_depth + 1)
                stats['total_size'] += sub_stats['total_size']
                stats['file_count'] += sub_stats['file_count']
                stats['dir_count'] += sub_stats['dir_count']
                
                # Merge file types
                for ext, count in sub_stats['file_types'].items():
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + count
                
                # Merge largest files
                stats['largest_files'].extend(sub_stats['largest_files'])
    
    except PermissionError:
        pass
    
    # Keep only top largest files
    stats['largest_files'] = sorted(stats['largest_files'], key=lambda x: x[1], reverse=True)[:10]
    
    return stats


def _build_tree(path: Path, max_depth: int, include_hidden: bool, extensions_filter: Optional[set], current_depth: int, prefix: str = "") -> str:
    """Build ASCII tree representation of directory."""
    if current_depth >= max_depth:
        return ""
    
    lines = []
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        
        # Filter items
        filtered_items = []
        for item in items:
            if not include_hidden and item.name.startswith('.'):
                continue
            if extensions_filter and item.is_file() and item.suffix not in extensions_filter:
                continue
            filtered_items.append(item)
        
        for i, item in enumerate(filtered_items):
            is_last = i == len(filtered_items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "
            
            if item.is_dir():
                lines.append(f"{prefix}{current_prefix}{item.name}/")
                # Recurse
                subtree = _build_tree(item, max_depth, include_hidden, extensions_filter, current_depth + 1, prefix + next_prefix)
                if subtree:
                    lines.append(subtree)
            else:
                size = _human_readable_size(item.stat().st_size)
                lines.append(f"{prefix}{current_prefix}{item.name} ({size})")
    
    except PermissionError:
        lines.append(f"{prefix}[Permission Denied]")
    
    return '\n'.join(lines)
