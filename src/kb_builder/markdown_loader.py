#!/usr/bin/env python3
"""
Markdown directory loader for knowledge base.

Provides native support for loading markdown files from a directory
without requiring tar.gz archives.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def load_markdown_directory(
    directory_path: str,
    recursive: bool = True,
    metadata_from_frontmatter: bool = True
) -> List[Dict[str, Any]]:
    """
    Load markdown files from a directory into document format.
    
    Args:
        directory_path: Path to directory containing markdown files
        recursive: Whether to recursively search subdirectories
        metadata_from_frontmatter: Whether to extract metadata from YAML frontmatter
        
    Returns:
        List of document dictionaries ready for indexing
    """
    path = Path(directory_path).expanduser()
    
    if not path.exists():
        raise ValueError(f"Directory not found: {directory_path}")
    
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    
    logger.info(f"Loading markdown files from: {path}")
    
    # Find all markdown files
    if recursive:
        md_files = list(path.glob("**/*.md")) + list(path.glob("**/*.markdown"))
    else:
        md_files = list(path.glob("*.md")) + list(path.glob("*.markdown"))
    
    logger.info(f"Found {len(md_files)} markdown files")
    
    documents = []
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter if requested
            metadata = {}
            text = content
            
            if metadata_from_frontmatter and content.startswith('---'):
                # Simple YAML frontmatter extraction
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1].strip()
                    text = parts[2].strip()
                    
                    # Parse simple key: value pairs
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()
            
            # Add file metadata
            metadata['source'] = str(md_file)
            metadata['filename'] = md_file.name
            metadata['directory'] = str(md_file.parent)
            
            # Create document
            doc_id = md_file.stem
            documents.append({
                "id": doc_id,
                "text": text,
                "metadata": metadata
            })
            
            logger.debug(f"Loaded: {md_file.name}")
            
        except Exception as e:
            logger.error(f"Error loading {md_file}: {e}")
    
    logger.info(f"Successfully loaded {len(documents)} markdown documents")
    return documents


def segment_markdown_document(
    text: str,
    by_headings: bool = True,
    min_segment_length: int = 100
) -> List[str]:
    """
    Segment a markdown document into smaller chunks.
    
    Args:
        text: Markdown text content
        by_headings: Whether to segment by heading boundaries
        min_segment_length: Minimum length for a segment (in characters)
        
    Returns:
        List of text segments
    """
    if not by_headings:
        # Simple paragraph-based segmentation
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return [p for p in paragraphs if len(p) >= min_segment_length]
    
    # Segment by headings
    segments = []
    current_segment = []
    current_heading = None
    
    for line in text.split('\n'):
        # Check if line is a heading
        if line.strip().startswith('#'):
            # Save previous segment if it exists
            if current_segment:
                segment_text = '\n'.join(current_segment).strip()
                if len(segment_text) >= min_segment_length:
                    segments.append(segment_text)
            
            # Start new segment with heading
            current_heading = line
            current_segment = [line]
        else:
            current_segment.append(line)
    
    # Add final segment
    if current_segment:
        segment_text = '\n'.join(current_segment).strip()
        if len(segment_text) >= min_segment_length:
            segments.append(segment_text)
    
    return segments if segments else [text]


def load_and_segment_markdown_directory(
    directory_path: str,
    recursive: bool = True,
    segment_by_headings: bool = True,
    min_segment_length: int = 100
) -> List[Dict[str, Any]]:
    """
    Load and segment markdown files from a directory.
    
    This combines loading and segmentation for optimal chunking
    of markdown content.
    
    Args:
        directory_path: Path to directory containing markdown files
        recursive: Whether to recursively search subdirectories
        segment_by_headings: Whether to segment by heading boundaries
        min_segment_length: Minimum length for segments
        
    Returns:
        List of segmented documents ready for indexing
    """
    # Load documents
    documents = load_markdown_directory(directory_path, recursive)
    
    # Segment each document
    segmented_documents = []
    for doc in documents:
        segments = segment_markdown_document(
            doc['text'],
            by_headings=segment_by_headings,
            min_segment_length=min_segment_length
        )
        
        # Create separate documents for each segment
        for i, segment in enumerate(segments):
            seg_id = f"{doc['id']}_seg{i}"
            seg_doc = {
                "id": seg_id,
                "text": segment,
                "metadata": {
                    **doc['metadata'],
                    "segment_index": i,
                    "total_segments": len(segments)
                }
            }
            segmented_documents.append(seg_doc)
    
    logger.info(f"Segmented into {len(segmented_documents)} document chunks")
    return segmented_documents
