"""
Memory-focused tools for the txtai MCP server.

Provides tools for temporal memory, contextual associations, importance tracking,
and reflection - enhancing the server's ability to function as human memory.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from ..core.state import add_to_document_cache, get_document_cache, get_txtai_app

logger = logging.getLogger(__name__)


def register_memory_tools(mcp: FastMCP) -> None:
    """Register memory-focused tools with the MCP server."""
    logger.debug("Starting registration of memory tools...")

    @mcp.tool(
        name="store_memory",
        description="""Store a memory with rich metadata for later retrieval.
        
        This is the primary way to save information as human-like memory. Each memory can include:
        - Temporal context (when did this happen/when was this learned?)
        - Importance/priority level (how significant is this?)
        - Emotional context or sentiment
        - Associated people, places, topics, or tags
        - Source of the memory
        
        Best used for:
        - Recording experiences or events
        - Saving learned information with context
        - Building a personal knowledge base
        - Creating time-aware memories
        
        Example: Store a memory about learning Python with importance=8, topics=['programming', 'learning']""",
    )
    async def store_memory(
        ctx: Context,
        content: str,
        importance: int = Field(5, description="Importance level 1-10, where 10 is most important"),
        timestamp: Optional[str] = Field(
            None, description="ISO timestamp when memory was created/occurred. Defaults to now."
        ),
        topics: Optional[List[str]] = Field(None, description="Associated topics or tags"),
        people: Optional[List[str]] = Field(None, description="People associated with this memory"),
        places: Optional[List[str]] = Field(None, description="Places associated with this memory"),
        sentiment: Optional[str] = Field(
            None, description="Emotional context: 'positive', 'negative', 'neutral', etc."
        ),
        source: Optional[str] = Field(
            None,
            description="Source of this memory (e.g., 'conversation', 'reading', 'experience')",
        ),
        related_to: Optional[List[str]] = Field(None, description="IDs of related memories"),
    ) -> Dict[str, Any]:
        """Store a memory with rich contextual metadata."""
        try:
            app = get_txtai_app()

            # Generate unique ID
            memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Set timestamp
            if timestamp is None:
                timestamp = datetime.now().isoformat()

            # Build comprehensive metadata
            metadata = {
                "type": "memory",
                "importance": importance,
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "access_count": 0,
                "last_accessed": None,
            }

            if topics:
                metadata["topics"] = topics
            if people:
                metadata["people"] = people
            if places:
                metadata["places"] = places
            if sentiment:
                metadata["sentiment"] = sentiment
            if source:
                metadata["source"] = source
            if related_to:
                metadata["related_to"] = related_to

            # Add to cache
            add_to_document_cache(memory_id, content)

            # Add to embeddings index
            metadata_str = json.dumps(metadata)
            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(memory_id, content, metadata_str)])
            else:
                app.embeddings.index([(memory_id, content, metadata_str)])

            # Save if path is configured
            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))

            logger.info(f"Stored memory {memory_id} with importance={importance}")

            return {
                "status": "success",
                "memory_id": memory_id,
                "timestamp": timestamp,
                "importance": importance,
                "message": "Memory stored successfully",
            }

        except Exception as e:
            logger.error(f"Failed to store memory: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to store memory"}

    @mcp.tool(
        name="recall_by_time",
        description="""Recall memories from a specific time period.
        
        Retrieve memories based on temporal context - when they occurred or were created.
        This enables time-based memory recall similar to human memory.
        
        Best used for:
        - "What did I learn last week?"
        - "What happened in January?"
        - "Recent conversations about X"
        - Building temporal context
        
        Example: recall_by_time(period='last_week', topics=['python'])""",
    )
    async def recall_by_time(
        ctx: Context,
        period: str = Field(
            ...,
            description="Time period: 'today', 'yesterday', 'last_week', 'last_month', 'last_year', or ISO date range 'YYYY-MM-DD:YYYY-MM-DD'",
        ),
        topics: Optional[List[str]] = Field(None, description="Filter by topics"),
        min_importance: Optional[int] = Field(None, description="Minimum importance level (1-10)"),
        limit: int = Field(20, description="Maximum number of memories to recall"),
    ) -> Dict[str, Any]:
        """Recall memories from a specific time period."""
        try:
            app = get_txtai_app()

            # Parse time period
            now = datetime.now()
            if period == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now
            elif period == "yesterday":
                start_date = (now - timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "last_week":
                start_date = now - timedelta(days=7)
                end_date = now
            elif period == "last_month":
                start_date = now - timedelta(days=30)
                end_date = now
            elif period == "last_year":
                start_date = now - timedelta(days=365)
                end_date = now
            elif ":" in period:
                # Date range format
                start_str, end_str = period.split(":")
                start_date = datetime.fromisoformat(start_str)
                end_date = datetime.fromisoformat(end_str)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown time period: {period}",
                    "message": "Use 'today', 'yesterday', 'last_week', 'last_month', 'last_year', or 'YYYY-MM-DD:YYYY-MM-DD'",
                }

            # Build SQL filter for temporal search
            sql_parts = [
                f"timestamp >= '{start_date.isoformat()}'",
                f"timestamp <= '{end_date.isoformat()}'",
            ]

            if topics:
                # Search for any of the topics
                topic_filters = [f"topics LIKE '%{topic}%'" for topic in topics]
                sql_parts.append(f"({' OR '.join(topic_filters)})")

            if min_importance is not None:
                sql_parts.append(f"importance >= {min_importance}")

            sql_filter = " AND ".join(sql_parts)

            # Search with temporal filter
            results = app.embeddings.search(
                "SELECT id, text, score FROM txtai WHERE "
                + sql_filter
                + f" ORDER BY timestamp DESC LIMIT {limit}"
            )

            memories = []
            for result in results:
                memory_id = result.get("id", "")
                text = result.get("text", "")

                # Try to get metadata
                metadata = {}
                if hasattr(app.embeddings, "search"):
                    try:
                        meta_results = app.embeddings.search(
                            f"SELECT metadata FROM txtai WHERE id = '{memory_id}'"
                        )
                        if meta_results:
                            metadata = json.loads(meta_results[0].get("metadata", "{}"))
                    except:
                        pass

                memories.append(
                    {
                        "id": memory_id,
                        "content": text,
                        "timestamp": metadata.get("timestamp"),
                        "importance": metadata.get("importance"),
                        "topics": metadata.get("topics", []),
                        "sentiment": metadata.get("sentiment"),
                    }
                )

            return {
                "status": "success",
                "period": period,
                "count": len(memories),
                "memories": memories,
                "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            }

        except Exception as e:
            logger.error(f"Failed to recall by time: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to recall memories by time",
            }

    @mcp.tool(
        name="find_associations",
        description="""Find memories associated with specific contexts, people, places, or topics.
        
        Discover related memories through contextual associations - similar to how human
        memory works through connections and associations.
        
        Best used for:
        - Finding all memories about a person
        - Recalling memories from a specific place
        - Discovering topic-related memories
        - Building contextual understanding
        
        Example: find_associations(people=['Alice'], topics=['project'])""",
    )
    async def find_associations(
        ctx: Context,
        topics: Optional[List[str]] = Field(None, description="Topics to find"),
        people: Optional[List[str]] = Field(None, description="People to find"),
        places: Optional[List[str]] = Field(None, description="Places to find"),
        sentiment: Optional[str] = Field(None, description="Sentiment filter"),
        min_importance: Optional[int] = Field(None, description="Minimum importance"),
        limit: int = Field(20, description="Maximum results"),
    ) -> Dict[str, Any]:
        """Find memories by contextual associations."""
        try:
            app = get_txtai_app()

            # Build filters
            filters = []

            if topics:
                for topic in topics:
                    filters.append(f"topics LIKE '%{topic}%'")

            if people:
                for person in people:
                    filters.append(f"people LIKE '%{person}%'")

            if places:
                for place in places:
                    filters.append(f"places LIKE '%{place}%'")

            if sentiment:
                filters.append(f"sentiment = '{sentiment}'")

            if min_importance is not None:
                filters.append(f"importance >= {min_importance}")

            if not filters:
                return {
                    "status": "error",
                    "error": "At least one filter criteria required",
                    "message": "Specify topics, people, places, sentiment, or min_importance",
                }

            sql_query = f"SELECT id, text FROM txtai WHERE {' OR '.join(filters)} LIMIT {limit}"

            results = app.embeddings.search(sql_query)

            memories = []
            for result in results:
                memories.append(
                    {
                        "id": result.get("id", ""),
                        "content": result.get("text", ""),
                        "score": result.get("score", 0.0),
                    }
                )

            return {
                "status": "success",
                "count": len(memories),
                "filters": {
                    "topics": topics,
                    "people": people,
                    "places": places,
                    "sentiment": sentiment,
                    "min_importance": min_importance,
                },
                "memories": memories,
            }

        except Exception as e:
            logger.error(f"Failed to find associations: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to find associations"}

    @mcp.tool(
        name="reflect_on_memories",
        description="""Analyze patterns and generate insights from stored memories.
        
        Perform meta-analysis on memories to identify:
        - Common themes and patterns
        - Temporal trends (what's been important recently?)
        - Frequently accessed memories
        - Knowledge gaps
        - Sentiment patterns over time
        
        This enables higher-order reflection similar to human introspection.
        
        Best used for:
        - Understanding learning patterns
        - Identifying focus areas
        - Discovering knowledge gaps
        - Tracking emotional patterns
        - Building self-awareness
        
        Example: reflect_on_memories(aspect='topics', time_period='last_month')""",
    )
    async def reflect_on_memories(
        ctx: Context,
        aspect: str = Field(
            ...,
            description="What to reflect on: 'topics', 'importance', 'sentiment', 'frequency', 'timeline', or 'all'",
        ),
        time_period: Optional[str] = Field(
            None, description="Time period to analyze (same format as recall_by_time)"
        ),
        limit: int = Field(100, description="Number of memories to analyze"),
    ) -> Dict[str, Any]:
        """Generate insights and patterns from memories."""
        try:
            app = get_txtai_app()

            # Get memories for analysis
            if time_period:
                # Use recall_by_time logic
                recall_result = await recall_by_time(ctx, period=time_period, limit=limit)
                if recall_result["status"] == "error":
                    return recall_result
                memories = recall_result["memories"]
            else:
                # Get all memories
                results = app.embeddings.search(
                    f"SELECT id, text, metadata FROM txtai WHERE type = 'memory' LIMIT {limit}"
                )
                memories = []
                for result in results:
                    metadata = {}
                    try:
                        metadata = json.loads(result.get("metadata", "{}"))
                    except:
                        pass

                    memories.append(
                        {
                            "id": result.get("id", ""),
                            "content": result.get("text", ""),
                            "importance": metadata.get("importance"),
                            "timestamp": metadata.get("timestamp"),
                            "topics": metadata.get("topics", []),
                            "sentiment": metadata.get("sentiment"),
                            "access_count": metadata.get("access_count", 0),
                        }
                    )

            insights = {
                "total_memories": len(memories),
                "analysis_period": time_period or "all_time",
            }

            # Analyze based on aspect
            if aspect in ["topics", "all"]:
                # Topic distribution
                topic_counts = defaultdict(int)
                for mem in memories:
                    for topic in mem.get("topics", []):
                        topic_counts[topic] += 1

                insights["top_topics"] = sorted(
                    [{"topic": k, "count": v} for k, v in topic_counts.items()],
                    key=lambda x: x["count"],
                    reverse=True,
                )[:10]

            if aspect in ["importance", "all"]:
                # Importance distribution
                importance_scores = [
                    m.get("importance", 0) for m in memories if m.get("importance")
                ]
                if importance_scores:
                    insights["importance_stats"] = {
                        "average": sum(importance_scores) / len(importance_scores),
                        "max": max(importance_scores),
                        "min": min(importance_scores),
                        "high_importance_count": sum(1 for s in importance_scores if s >= 8),
                    }

            if aspect in ["sentiment", "all"]:
                # Sentiment distribution
                sentiment_counts = defaultdict(int)
                for mem in memories:
                    sent = mem.get("sentiment")
                    if sent:
                        sentiment_counts[sent] += 1

                insights["sentiment_distribution"] = dict(sentiment_counts)

            if aspect in ["frequency", "all"]:
                # Access frequency
                access_counts = [m.get("access_count", 0) for m in memories]
                if access_counts:
                    insights["access_patterns"] = {
                        "average_accesses": sum(access_counts) / len(access_counts),
                        "most_accessed_count": max(access_counts),
                        "rarely_accessed_count": sum(1 for c in access_counts if c <= 1),
                    }

            if aspect in ["timeline", "all"]:
                # Temporal patterns
                timestamps = [m.get("timestamp") for m in memories if m.get("timestamp")]
                if timestamps:
                    dates = [datetime.fromisoformat(ts) for ts in timestamps if ts]
                    if dates:
                        insights["temporal_patterns"] = {
                            "earliest": min(dates).isoformat(),
                            "latest": max(dates).isoformat(),
                            "span_days": (max(dates) - min(dates)).days,
                        }

            # Generate recommendations
            recommendations = []

            if insights.get("top_topics"):
                top_topic = insights["top_topics"][0]["topic"]
                recommendations.append(
                    f"Your most frequent topic is '{top_topic}' - consider consolidating related memories"
                )

            if insights.get("importance_stats", {}).get("high_importance_count", 0) > 5:
                recommendations.append(
                    "You have many high-importance memories - consider reviewing and organizing them"
                )

            if insights.get("access_patterns", {}).get("rarely_accessed_count", 0) > 10:
                recommendations.append(
                    "Many memories are rarely accessed - consider reviewing their relevance"
                )

            insights["recommendations"] = recommendations

            return {"status": "success", "aspect": aspect, "insights": insights}

        except Exception as e:
            logger.error(f"Failed to reflect on memories: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to generate reflections"}

    @mcp.tool(
        name="update_memory_importance",
        description="""Update the importance level of a memory based on new context or reflection.
        
        As memories are accessed and reflected upon, their importance may change.
        This allows dynamic adjustment of memory priority.
        
        Best used for:
        - Adjusting importance after reflection
        - Boosting priority of frequently accessed memories
        - Demoting less relevant memories
        - Implementing spaced repetition patterns
        
        Example: update_memory_importance(memory_id='mem_123', new_importance=9, reason='Critical for project')""",
    )
    async def update_memory_importance(
        ctx: Context,
        memory_id: str,
        new_importance: int = Field(..., description="New importance level (1-10)"),
        reason: Optional[str] = Field(None, description="Reason for importance change"),
    ) -> Dict[str, Any]:
        """Update the importance level of an existing memory."""
        try:
            app = get_txtai_app()

            # Get existing memory
            results = app.embeddings.search(
                f"SELECT text, metadata FROM txtai WHERE id = '{memory_id}'"
            )
            if not results:
                return {
                    "status": "error",
                    "error": f"Memory {memory_id} not found",
                    "message": "Memory does not exist",
                }

            text = results[0].get("text", "")
            metadata = json.loads(results[0].get("metadata", "{}"))

            old_importance = metadata.get("importance", 5)
            metadata["importance"] = new_importance
            metadata["importance_updated_at"] = datetime.now().isoformat()

            if reason:
                if "importance_history" not in metadata:
                    metadata["importance_history"] = []
                metadata["importance_history"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "old_value": old_importance,
                        "new_value": new_importance,
                        "reason": reason,
                    }
                )

            # Update memory
            metadata_str = json.dumps(metadata)
            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(memory_id, text, metadata_str)])

            # Save if configured
            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))

            return {
                "status": "success",
                "memory_id": memory_id,
                "old_importance": old_importance,
                "new_importance": new_importance,
                "message": f"Importance updated from {old_importance} to {new_importance}",
            }

        except Exception as e:
            logger.error(f"Failed to update memory importance: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to update importance"}

    logger.debug("Memory tools registered successfully")
