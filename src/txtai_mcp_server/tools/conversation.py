"""
Conversation history and context tracking tools for the txtai MCP server.

Provides tools for managing conversation history, tracking context across sessions,
and maintaining conversational continuity - key aspects of agent memory.
"""

import json
import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from ..core.state import add_to_document_cache, get_txtai_app

logger = logging.getLogger(__name__)


def register_conversation_tools(mcp: FastMCP) -> None:
    """Register conversation tracking tools with the MCP server."""
    logger.debug("Starting registration of conversation tools...")

    @mcp.tool(
        name="store_conversation_turn",
        description="""Store a conversation turn (user message + assistant response) with context.
        
        Maintains conversation history as structured memory, enabling the agent to:
        - Remember past conversations
        - Track context across sessions
        - Learn from interactions
        - Provide continuity in multi-session conversations
        
        Best used for:
        - Recording each exchange in a conversation
        - Building conversation history
        - Tracking topics discussed
        - Learning user preferences over time
        
        Example: store_conversation_turn(user_message='What is Python?', assistant_response='Python is...', topics=['python', 'programming'])""",
    )
    async def store_conversation_turn(
        ctx: Context,
        user_message: str,
        assistant_response: str,
        session_id: Optional[str] = Field(
            None, description="Session identifier for grouping related conversations"
        ),
        topics: Optional[List[str]] = Field(None, description="Topics discussed in this turn"),
        importance: int = Field(5, description="Importance of this conversation turn (1-10)"),
        user_sentiment: Optional[str] = Field(
            None, description="Detected sentiment of user message"
        ),
        metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata"),
    ) -> Dict[str, Any]:
        """Store a conversation turn with rich context."""
        try:
            app = get_txtai_app()

            # Generate unique ID
            timestamp = datetime.now()
            turn_id = f"conv_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"

            # Build conversation content
            conversation_text = f"User: {user_message}\n\nAssistant: {assistant_response}"

            # Build metadata
            conv_metadata = {
                "type": "conversation",
                "timestamp": timestamp.isoformat(),
                "session_id": session_id or "default",
                "user_message": user_message,
                "assistant_response": assistant_response,
                "importance": importance,
                "topics": topics or [],
                "user_sentiment": user_sentiment,
                "turn_number": None,  # Will be set if session tracking is implemented
            }

            if metadata:
                conv_metadata.update(metadata)

            # Add to cache
            add_to_document_cache(turn_id, conversation_text)

            # Add to embeddings
            metadata_str = json.dumps(conv_metadata)
            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(turn_id, conversation_text, metadata_str)])
            else:
                app.embeddings.index([(turn_id, conversation_text, metadata_str)])

            # Save if configured
            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))

            logger.info(f"Stored conversation turn {turn_id}")

            return {
                "status": "success",
                "turn_id": turn_id,
                "session_id": session_id or "default",
                "timestamp": timestamp.isoformat(),
                "message": "Conversation turn stored successfully",
            }

        except Exception as e:
            logger.error(f"Failed to store conversation turn: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to store conversation"}

    @mcp.tool(
        name="recall_conversation_history",
        description="""Recall previous conversation history for context.
        
        Retrieve past conversations to:
        - Restore context from previous sessions
        - Review what was discussed about a topic
        - Track conversation evolution over time
        - Provide continuity across sessions
        
        Best used for:
        - Starting a new session with context
        - Reviewing past discussions
        - Finding when a topic was last discussed
        - Understanding conversation patterns
        
        Example: recall_conversation_history(session_id='project_planning', limit=10)""",
    )
    async def recall_conversation_history(
        ctx: Context,
        session_id: Optional[str] = Field(None, description="Session ID to filter by"),
        topics: Optional[List[str]] = Field(None, description="Filter by topics"),
        since: Optional[str] = Field(
            None, description="ISO timestamp - only return conversations after this time"
        ),
        limit: int = Field(20, description="Maximum number of turns to return"),
    ) -> Dict[str, Any]:
        """Recall conversation history with optional filters."""
        try:
            app = get_txtai_app()

            # Build filter query
            filters = ["type = 'conversation'"]

            if session_id:
                filters.append(f"session_id = '{session_id}'")

            if topics:
                topic_filters = [f"topics LIKE '%{topic}%'" for topic in topics]
                filters.append(f"({' OR '.join(topic_filters)})")

            if since:
                filters.append(f"timestamp >= '{since}'")

            sql_query = f"SELECT id, text, metadata FROM txtai WHERE {' AND '.join(filters)} ORDER BY timestamp DESC LIMIT {limit}"

            results = app.embeddings.search(sql_query)

            conversations = []
            for result in results:
                metadata = {}
                try:
                    metadata = json.loads(result.get("metadata", "{}"))
                except:
                    pass

                conversations.append(
                    {
                        "turn_id": result.get("id", ""),
                        "timestamp": metadata.get("timestamp"),
                        "session_id": metadata.get("session_id"),
                        "user_message": metadata.get("user_message", ""),
                        "assistant_response": metadata.get("assistant_response", ""),
                        "topics": metadata.get("topics", []),
                        "importance": metadata.get("importance"),
                        "user_sentiment": metadata.get("user_sentiment"),
                    }
                )

            # Sort by timestamp (oldest first for conversation flow)
            conversations.reverse()

            return {
                "status": "success",
                "count": len(conversations),
                "session_id": session_id,
                "conversations": conversations,
            }

        except Exception as e:
            logger.error(f"Failed to recall conversation history: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to recall conversations"}

    @mcp.tool(
        name="summarize_conversation_session",
        description="""Generate a summary of a conversation session.
        
        Create a condensed overview of a conversation session including:
        - Main topics discussed
        - Key decisions or conclusions
        - Action items mentioned
        - Overall sentiment
        
        This helps maintain high-level context without storing full conversation details.
        
        Best used for:
        - Creating session summaries at end of conversation
        - Reviewing long conversation threads
        - Building session context efficiently
        - Tracking conversation outcomes
        
        Example: summarize_conversation_session(session_id='project_planning')""",
    )
    async def summarize_conversation_session(
        ctx: Context,
        session_id: str,
        save_summary: bool = Field(True, description="Whether to save summary as a memory"),
    ) -> Dict[str, Any]:
        """Generate and optionally save a summary of a conversation session."""
        try:
            # Get conversation history
            history_result = await recall_conversation_history(
                ctx, session_id=session_id, limit=100
            )

            if history_result["status"] == "error":
                return history_result

            conversations = history_result["conversations"]

            if not conversations:
                return {
                    "status": "error",
                    "error": "No conversations found for this session",
                    "message": f"Session '{session_id}' has no recorded conversations",
                }

            # Analyze conversations
            all_topics = []
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            high_importance_turns = []

            for conv in conversations:
                all_topics.extend(conv.get("topics", []))

                sentiment = conv.get("user_sentiment")
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1

                if conv.get("importance", 0) >= 7:
                    high_importance_turns.append(
                        {
                            "user": conv["user_message"],
                            "assistant": conv["assistant_response"],
                            "importance": conv["importance"],
                        }
                    )

            # Count unique topics
            from collections import Counter

            topic_counts = Counter(all_topics)
            top_topics = [{"topic": k, "count": v} for k, v in topic_counts.most_common(10)]

            # Determine overall sentiment
            max_sentiment = max(sentiment_counts, key=sentiment_counts.get)

            # Create summary
            summary = {
                "session_id": session_id,
                "turn_count": len(conversations),
                "time_span": {
                    "start": conversations[0]["timestamp"],
                    "end": conversations[-1]["timestamp"],
                },
                "top_topics": top_topics,
                "overall_sentiment": max_sentiment,
                "sentiment_distribution": sentiment_counts,
                "high_importance_turns": high_importance_turns[:5],  # Top 5
                "generated_at": datetime.now().isoformat(),
            }

            # Optionally save as a memory
            if save_summary:
                app = get_txtai_app()

                summary_id = f"summary_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                summary_text = f"Session Summary: {session_id}\n\n"
                summary_text += f"Turns: {len(conversations)}\n"
                summary_text += f"Topics: {', '.join([t['topic'] for t in top_topics[:5]])}\n"
                summary_text += f"Sentiment: {max_sentiment}\n"

                metadata = {
                    "type": "conversation_summary",
                    "session_id": session_id,
                    "summary": summary,
                    "timestamp": datetime.now().isoformat(),
                }

                metadata_str = json.dumps(metadata)
                if hasattr(app.embeddings, "upsert"):
                    app.embeddings.upsert([(summary_id, summary_text, metadata_str)])
                else:
                    app.embeddings.index([(summary_id, summary_text, metadata_str)])

                if app.config.get("path"):
                    app.embeddings.save(app.config.get("path"))

                summary["saved_as"] = summary_id

            return {"status": "success", "summary": summary}

        except Exception as e:
            logger.error(f"Failed to summarize conversation: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to generate summary"}

    @mcp.tool(
        name="search_conversations",
        description="""Search through conversation history semantically.
        
        Find past conversations related to a query using semantic search.
        This enables finding relevant context even when exact words weren't used.
        
        Best used for:
        - "Did we discuss X before?"
        - Finding relevant past context
        - Discovering related conversations
        - Building on previous discussions
        
        Example: search_conversations(query='machine learning best practices', limit=5)""",
    )
    async def search_conversations(
        ctx: Context,
        query: str,
        session_id: Optional[str] = Field(None, description="Limit to specific session"),
        min_importance: Optional[int] = Field(None, description="Minimum importance level"),
        limit: int = Field(10, description="Maximum results"),
    ) -> Dict[str, Any]:
        """Search conversations semantically."""
        try:
            app = get_txtai_app()

            # Build search query with filters
            filters = ["type = 'conversation'"]

            if session_id:
                filters.append(f"session_id = '{session_id}'")

            if min_importance is not None:
                filters.append(f"importance >= {min_importance}")

            # Perform semantic search
            filter_clause = " AND ".join(filters)
            search_query = f"SELECT id, text, score FROM txtai WHERE {filter_clause} AND similar(text, '{query}') LIMIT {limit}"

            results = app.embeddings.search(query, limit)

            # Filter to only conversation types and enrich with metadata
            conversations = []
            for result in results:
                result_id = result.get("id", "")
                if not result_id.startswith("conv_"):
                    continue

                # Get metadata
                metadata_results = app.embeddings.search(
                    f"SELECT metadata FROM txtai WHERE id = '{result_id}'"
                )
                metadata = {}
                if metadata_results:
                    try:
                        metadata = json.loads(metadata_results[0].get("metadata", "{}"))
                    except:
                        pass

                conversations.append(
                    {
                        "turn_id": result_id,
                        "relevance_score": result.get("score", 0.0),
                        "timestamp": metadata.get("timestamp"),
                        "session_id": metadata.get("session_id"),
                        "user_message": metadata.get("user_message", ""),
                        "assistant_response": metadata.get("assistant_response", ""),
                        "topics": metadata.get("topics", []),
                    }
                )

            return {
                "status": "success",
                "query": query,
                "count": len(conversations),
                "conversations": conversations,
            }

        except Exception as e:
            logger.error(f"Failed to search conversations: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to search conversations"}

    logger.debug("Conversation tools registered successfully")
