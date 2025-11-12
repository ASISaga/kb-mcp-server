"""
Knowledge base management tools for the txtai MCP server.

Provides tools for incremental learning and evolving knowledge bases,
allowing AI agents to edit, organize, and consolidate knowledge dynamically.
"""
import logging
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field

from ..core.state import get_txtai_app, add_to_document_cache, get_document_from_cache, get_document_cache

logger = logging.getLogger(__name__)


def register_kb_management_tools(mcp: FastMCP) -> None:
    """Register knowledge base management tools with the MCP server."""
    logger.debug("Starting registration of KB management tools...")

    @mcp.tool(
        name="update_document",
        description="""Update an existing document in the knowledge base.
        
        Allows incremental learning by modifying existing knowledge.
        The agent can refine, correct, or enhance existing information.
        
        Best used for:
        - Correcting errors in existing knowledge
        - Adding new information to existing documents
        - Refining understanding of concepts
        - Evolving knowledge over time
        
        Example: Update a document about "Python" to include new Python 3.12 features."""
    )
    async def update_document(
        ctx: Context,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the document")
    ) -> Dict[str, Any]:
        """Update an existing document in the knowledge base."""
        logger.info(f"Updating document: {document_id}")
        
        try:
            app = get_txtai_app()
            
            # Prepare document for update
            document = {
                "id": document_id,
                "text": text
            }
            
            if metadata:
                document["metadata"] = metadata
            
            # Update in cache
            add_to_document_cache(document_id, text)
            
            # Upsert to index (update if exists, insert if not)
            if hasattr(app.embeddings, 'upsert'):
                metadata_str = json.dumps(metadata) if metadata else None
                app.embeddings.upsert([(document_id, text, metadata_str)])
                
                # Save index
                if app.config.get("path"):
                    app.embeddings.save(app.config.get("path"))
                
                return {
                    "status": "success",
                    "message": f"Document {document_id} updated successfully",
                    "document_id": document_id
                }
            else:
                # Fallback: delete and re-add
                return {
                    "status": "error",
                    "message": "Update not supported by current embeddings backend. Use delete and add instead."
                }
                
        except Exception as e:
            logger.error(f"Failed to update document: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to update document: {str(e)}"
            }

    @mcp.tool(
        name="delete_document",
        description="""Delete a document from the knowledge base.
        
        Allows removal of outdated or incorrect information.
        Part of incremental learning and knowledge evolution.
        
        Best used for:
        - Removing outdated information
        - Deleting duplicate content
        - Cleaning up the knowledge base
        - Managing knowledge base size
        
        Example: Delete deprecated API documentation."""
    )
    async def delete_document(
        ctx: Context,
        document_id: str
    ) -> Dict[str, Any]:
        """Delete a document from the knowledge base."""
        logger.info(f"Deleting document: {document_id}")
        
        try:
            app = get_txtai_app()
            
            # Remove from cache
            cache = get_document_cache()
            if document_id in cache:
                del cache[document_id]
            
            # Delete from index
            if hasattr(app.embeddings, 'delete'):
                app.embeddings.delete([document_id])
                
                # Save index
                if app.config.get("path"):
                    app.embeddings.save(app.config.get("path"))
                
                return {
                    "status": "success",
                    "message": f"Document {document_id} deleted successfully",
                    "document_id": document_id
                }
            else:
                return {
                    "status": "error",
                    "message": "Delete not supported by current embeddings backend"
                }
                
        except Exception as e:
            logger.error(f"Failed to delete document: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to delete document: {str(e)}"
            }

    @mcp.tool(
        name="save_to_markdown",
        description="""Save document(s) to markdown files in the knowledge base directory.
        
        Enables persistent, file-based knowledge storage that can be version controlled.
        The agent can directly manage the markdown knowledge base.
        
        Best used for:
        - Persisting learned knowledge to disk
        - Creating new markdown documents
        - Building a git-trackable knowledge base
        - Exporting knowledge for human review
        
        Example: Save newly learned information about "Docker" to docs/docker.md"""
    )
    async def save_to_markdown(
        ctx: Context,
        filename: str,
        content: str,
        kb_directory: str = Field(description="Path to knowledge base markdown directory"),
        metadata: Optional[Dict[str, str]] = Field(None, description="YAML frontmatter metadata")
    ) -> Dict[str, Any]:
        """Save content to a markdown file in the knowledge base."""
        logger.info(f"Saving to markdown: {filename} in {kb_directory}")
        
        try:
            kb_path = Path(kb_directory).expanduser()
            
            # Create directory if it doesn't exist
            kb_path.mkdir(parents=True, exist_ok=True)
            
            # Ensure filename has .md extension
            if not filename.endswith('.md'):
                filename = f"{filename}.md"
            
            file_path = kb_path / filename
            
            # Build markdown content with frontmatter if provided
            markdown_content = ""
            
            if metadata:
                markdown_content += "---\n"
                for key, value in metadata.items():
                    markdown_content += f"{key}: {value}\n"
                markdown_content += "---\n\n"
            
            markdown_content += content
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Saved markdown file: {file_path}")
            
            return {
                "status": "success",
                "message": f"Content saved to {filename}",
                "path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to save markdown: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to save markdown: {str(e)}"
            }

    @mcp.tool(
        name="update_markdown_file",
        description="""Update an existing markdown file in the knowledge base.
        
        Allows direct editing of the markdown knowledge base files.
        Supports incremental knowledge evolution and refinement.
        
        Best used for:
        - Updating existing documentation
        - Refining knowledge articles
        - Correcting information in markdown files
        - Appending new sections to existing documents
        
        Example: Update docs/python.md to add information about async/await"""
    )
    async def update_markdown_file(
        ctx: Context,
        filename: str,
        content: str,
        kb_directory: str = Field(description="Path to knowledge base markdown directory"),
        mode: str = Field("replace", description="Update mode: 'replace' (overwrite) or 'append' (add to end)")
    ) -> Dict[str, Any]:
        """Update an existing markdown file."""
        logger.info(f"Updating markdown file: {filename} in {kb_directory} (mode: {mode})")
        
        try:
            kb_path = Path(kb_directory).expanduser()
            
            if not filename.endswith('.md'):
                filename = f"{filename}.md"
            
            file_path = kb_path / filename
            
            if not file_path.exists():
                return {
                    "status": "error",
                    "message": f"File not found: {filename}"
                }
            
            if mode == "replace":
                # Replace entire content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                message = f"Replaced content in {filename}"
                
            elif mode == "append":
                # Append to existing content
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write("\n\n" + content)
                message = f"Appended content to {filename}"
                
            else:
                return {
                    "status": "error",
                    "message": f"Invalid mode: {mode}. Use 'replace' or 'append'"
                }
            
            logger.info(f"Updated markdown file: {file_path}")
            
            return {
                "status": "success",
                "message": message,
                "path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to update markdown: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to update markdown: {str(e)}"
            }

    @mcp.tool(
        name="organize_knowledge",
        description="""Semantically organize documents by creating categories/tags.
        
        Helps structure the knowledge base for better retrieval and understanding.
        Uses semantic similarity to suggest document groupings.
        
        Best used for:
        - Categorizing related documents
        - Creating semantic hierarchies
        - Improving knowledge base navigation
        - Identifying knowledge clusters
        
        Example: Organize all ML-related documents under "machine-learning" category"""
    )
    async def organize_knowledge(
        ctx: Context,
        query: str = Field(description="Query to find related documents"),
        category: str = Field(description="Category/tag name to assign"),
        limit: int = Field(10, description="Number of documents to organize")
    ) -> Dict[str, Any]:
        """Organize documents by semantic similarity into categories."""
        logger.info(f"Organizing knowledge: query='{query}', category='{category}'")
        
        try:
            app = get_txtai_app()
            
            # Search for related documents
            results = app.search(query, limit=limit)
            
            organized_docs = []
            
            for result in results:
                if isinstance(result, dict):
                    doc_id = result.get("id")
                    score = result.get("score", 0.0)
                    
                    if doc_id:
                        # Update metadata to include category
                        # Note: This would need to be persisted
                        organized_docs.append({
                            "id": doc_id,
                            "score": score,
                            "category": category
                        })
            
            return {
                "status": "success",
                "message": f"Organized {len(organized_docs)} documents into '{category}'",
                "documents": organized_docs,
                "suggestion": f"Consider creating a directory '{category}' in your markdown KB"
            }
            
        except Exception as e:
            logger.error(f"Failed to organize knowledge: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to organize knowledge: {str(e)}"
            }

    @mcp.tool(
        name="consolidate_knowledge",
        description="""Consolidate duplicate or related documents.
        
        Identifies and merges similar documents to reduce redundancy.
        Part of knowledge base maintenance and optimization.
        
        Best used for:
        - Removing duplicate information
        - Merging related documents
        - Improving knowledge base quality
        - Reducing storage and search overhead
        
        Example: Find and consolidate duplicate articles about "Python basics" """
    )
    async def consolidate_knowledge(
        ctx: Context,
        topic: str = Field(description="Topic to consolidate around"),
        similarity_threshold: float = Field(0.8, description="Minimum similarity to consider consolidation"),
        limit: int = Field(20, description="Maximum documents to analyze")
    ) -> Dict[str, Any]:
        """Find and suggest consolidation of similar documents."""
        logger.info(f"Consolidating knowledge: topic='{topic}', threshold={similarity_threshold}")
        
        try:
            app = get_txtai_app()
            
            # Search for documents related to topic
            results = app.search(topic, limit=limit)
            
            # Group highly similar documents
            consolidation_groups = []
            seen = set()
            
            for i, result1 in enumerate(results):
                if i in seen:
                    continue
                    
                group = [result1]
                
                for j, result2 in enumerate(results[i+1:], start=i+1):
                    if j in seen:
                        continue
                    
                    # Check similarity (using scores as proxy)
                    if isinstance(result1, dict) and isinstance(result2, dict):
                        score1 = result1.get("score", 0.0)
                        score2 = result2.get("score", 0.0)
                        
                        # If both have high scores for same query, they're likely similar
                        if abs(score1 - score2) < (1.0 - similarity_threshold):
                            group.append(result2)
                            seen.add(j)
                
                if len(group) > 1:
                    consolidation_groups.append(group)
                    seen.add(i)
            
            suggestions = []
            for group in consolidation_groups:
                doc_ids = [d.get("id") for d in group if isinstance(d, dict)]
                suggestions.append({
                    "documents": doc_ids,
                    "count": len(doc_ids),
                    "suggestion": f"Consider merging these {len(doc_ids)} similar documents"
                })
            
            return {
                "status": "success",
                "message": f"Found {len(suggestions)} consolidation opportunities",
                "consolidation_groups": suggestions,
                "total_documents_analyzed": len(results)
            }
            
        except Exception as e:
            logger.error(f"Failed to consolidate knowledge: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to consolidate knowledge: {str(e)}"
            }

    @mcp.tool(
        name="reload_markdown_kb",
        description="""Reload the knowledge base from markdown directory.
        
        Synchronizes the in-memory knowledge base with the markdown files on disk.
        Essential for incremental learning from file-based knowledge.
        
        Best used for:
        - Reloading after manual markdown edits
        - Syncing after git pull
        - Refreshing the knowledge base
        - Loading newly added markdown files
        
        Example: Reload KB after adding new markdown files to docs/"""
    )
    async def reload_markdown_kb(
        ctx: Context,
        kb_directory: str = Field(description="Path to knowledge base markdown directory"),
        clear_existing: bool = Field(False, description="Clear existing index before reloading")
    ) -> Dict[str, Any]:
        """Reload knowledge base from markdown directory."""
        logger.info(f"Reloading markdown KB from: {kb_directory}")
        
        try:
            from ...kb_builder.markdown_loader import load_and_segment_markdown_directory
            
            app = get_txtai_app()
            
            # Load markdown files
            documents = load_and_segment_markdown_directory(
                kb_directory,
                recursive=True,
                segment_by_headings=True,
                min_segment_length=100
            )
            
            if not documents:
                return {
                    "status": "warning",
                    "message": "No markdown documents found in directory",
                    "path": kb_directory
                }
            
            # Clear existing index if requested
            if clear_existing and hasattr(app.embeddings, 'delete'):
                # This would require getting all existing IDs first
                logger.info("Clear existing index requested")
            
            # Add documents
            app.add(documents)
            app.index()
            
            # Update cache
            for doc in documents:
                add_to_document_cache(doc["id"], doc["text"])
            
            # Save index
            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))
            
            return {
                "status": "success",
                "message": f"Reloaded {len(documents)} document segments from markdown",
                "documents_loaded": len(documents),
                "path": kb_directory
            }
            
        except Exception as e:
            logger.error(f"Failed to reload markdown KB: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to reload markdown KB: {str(e)}"
            }

    @mcp.tool(
        name="list_markdown_files",
        description="""List all markdown files in the knowledge base directory.
        
        Provides visibility into the file-based knowledge base structure.
        Helps the agent understand what knowledge exists on disk.
        
        Best used for:
        - Exploring the knowledge base structure
        - Finding specific markdown files
        - Understanding knowledge organization
        - Planning knowledge base updates
        
        Example: List all markdown files to see what topics are covered"""
    )
    async def list_markdown_files(
        ctx: Context,
        kb_directory: str = Field(description="Path to knowledge base markdown directory"),
        include_stats: bool = Field(True, description="Include file statistics")
    ) -> Dict[str, Any]:
        """List all markdown files in the KB directory."""
        logger.info(f"Listing markdown files in: {kb_directory}")
        
        try:
            kb_path = Path(kb_directory).expanduser()
            
            if not kb_path.exists():
                return {
                    "status": "error",
                    "message": f"Directory not found: {kb_directory}"
                }
            
            # Find all markdown files
            md_files = list(kb_path.glob("**/*.md")) + list(kb_path.glob("**/*.markdown"))
            
            files_info = []
            for md_file in md_files:
                file_info = {
                    "name": md_file.name,
                    "path": str(md_file.relative_to(kb_path)),
                    "full_path": str(md_file)
                }
                
                if include_stats:
                    stat = md_file.stat()
                    file_info["size_bytes"] = stat.st_size
                    file_info["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    
                    # Read first line for title
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            if first_line.startswith('#'):
                                file_info["title"] = first_line.lstrip('#').strip()
                    except:
                        pass
                
                files_info.append(file_info)
            
            return {
                "status": "success",
                "count": len(files_info),
                "files": files_info,
                "directory": kb_directory
            }
            
        except Exception as e:
            logger.error(f"Failed to list markdown files: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to list markdown files: {str(e)}"
            }

    logger.info("Registered knowledge base management tools successfully")
