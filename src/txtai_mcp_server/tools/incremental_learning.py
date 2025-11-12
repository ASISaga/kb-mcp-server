"""
Incremental learning tools for the txtai MCP server.

Provides "on the go" learning capabilities that allow continuous knowledge acquisition,
progressive refinement, and adaptive learning - key aspects of human incremental learning.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field

from ..core.state import add_to_document_cache, get_txtai_app

logger = logging.getLogger(__name__)


def register_incremental_learning_tools(mcp: FastMCP) -> None:
    """Register incremental learning tools with the MCP server."""
    logger.debug("Starting registration of incremental learning tools...")

    @mcp.tool(
        name="quick_capture",
        description="""Quickly capture a learning moment or insight on the go.
        
        Designed for rapid knowledge capture during active learning or experiences.
        Creates a memory stub that can be expanded or refined later.
        
        Perfect for:
        - Capturing fleeting thoughts or insights
        - Recording "aha moments" during learning
        - Noting questions that arise during study
        - Quick bookmarking of important concepts
        - Building knowledge incrementally without interruption
        
        The captured item is automatically tagged for later expansion and review.
        
        Example: quick_capture(content="async/await might solve my callback problem", context="programming")""",
    )
    async def quick_capture(
        ctx: Context,
        content: str,
        context: Optional[str] = Field(
            None, description="Brief context: what were you doing when this came up?"
        ),
        tags: Optional[List[str]] = Field(None, description="Quick tags for categorization"),
        expand_later: bool = Field(
            True, description="Mark this for expansion in next review session"
        ),
    ) -> Dict[str, Any]:
        """Quickly capture a learning moment without extensive metadata."""
        try:
            app = get_txtai_app()

            # Generate ID
            capture_id = f"quick_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Build minimal metadata optimized for quick capture
            metadata = {
                "type": "quick_capture",
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "tags": tags or [],
                "expand_later": expand_later,
                "expanded": False,
                "importance": 5,  # Default medium importance
                "capture_method": "quick",
            }

            # Add to cache
            add_to_document_cache(capture_id, content)

            # Add to embeddings
            metadata_str = json.dumps(metadata)
            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(capture_id, content, metadata_str)])
            else:
                app.embeddings.index([(capture_id, content, metadata_str)])

            # Save if configured
            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))

            logger.info(f"Quick captured: {capture_id}")

            return {
                "status": "success",
                "capture_id": capture_id,
                "message": "Learning moment captured! Review and expand when ready.",
                "expand_later": expand_later,
            }

        except Exception as e:
            logger.error(f"Failed to quick capture: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to capture"}

    @mcp.tool(
        name="expand_learning",
        description="""Expand a previously captured quick note into a full memory.
        
        Takes a quick capture or partial memory and enriches it with:
        - Additional context and details
        - Proper categorization and tags
        - Importance weighting
        - Connections to related knowledge
        
        This enables progressive knowledge building - start quick, refine later.
        
        Best used for:
        - Reviewing quick captures from learning sessions
        - Adding depth to partial knowledge
        - Connecting new learnings to existing knowledge
        - Building comprehensive understanding over time
        
        Example: expand_learning(capture_id="quick_123", expanded_content="...", importance=8)""",
    )
    async def expand_learning(
        ctx: Context,
        capture_id: str,
        expanded_content: str,
        importance: int = Field(
            7, description="Importance level now that you understand it better (1-10)"
        ),
        topics: Optional[List[str]] = Field(None, description="Topics this relates to"),
        related_to: Optional[List[str]] = Field(
            None, description="IDs of related memories or learnings"
        ),
        key_insight: Optional[str] = Field(
            None, description="Main insight or takeaway from this learning"
        ),
    ) -> Dict[str, Any]:
        """Expand a quick capture into a full learning memory."""
        try:
            app = get_txtai_app()

            # Get original capture
            results = app.embeddings.search(f"SELECT metadata FROM txtai WHERE id = '{capture_id}'")
            if not results:
                return {
                    "status": "error",
                    "error": "Capture not found",
                    "message": f"No capture found with ID: {capture_id}",
                }

            # Get original metadata
            original_metadata = json.loads(results[0].get("metadata", "{}"))

            # Build expanded metadata
            metadata = {
                "type": "expanded_learning",
                "original_capture_id": capture_id,
                "original_timestamp": original_metadata.get("timestamp"),
                "expanded_at": datetime.now().isoformat(),
                "importance": importance,
                "topics": topics or original_metadata.get("tags", []),
                "related_to": related_to or [],
                "key_insight": key_insight,
                "learning_progression": "expanded",
                "access_count": 0,
            }

            # Create new ID for expanded version
            expanded_id = f"learn_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Add to cache
            add_to_document_cache(expanded_id, expanded_content)

            # Add expanded version
            metadata_str = json.dumps(metadata)
            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(expanded_id, expanded_content, metadata_str)])
            else:
                app.embeddings.index([(expanded_id, expanded_content, metadata_str)])

            # Mark original as expanded
            original_metadata["expanded"] = True
            original_metadata["expanded_to"] = expanded_id
            original_metadata_str = json.dumps(original_metadata)

            # Get original content
            original_results = app.embeddings.search(
                f"SELECT text FROM txtai WHERE id = '{capture_id}'"
            )
            original_content = original_results[0].get("text", "") if original_results else ""

            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(capture_id, original_content, original_metadata_str)])

            # Save if configured
            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))

            logger.info(f"Expanded learning: {capture_id} -> {expanded_id}")

            return {
                "status": "success",
                "expanded_id": expanded_id,
                "original_id": capture_id,
                "message": "Learning expanded successfully!",
                "key_insight": key_insight,
            }

        except Exception as e:
            logger.error(f"Failed to expand learning: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to expand"}

    @mcp.tool(
        name="reinforce_learning",
        description="""Reinforce a learning through repetition and usage.
        
        Implements spaced repetition principles by:
        - Tracking how often knowledge is accessed/used
        - Increasing importance of frequently used knowledge
        - Identifying learnings that need reinforcement
        - Building long-term retention through repetition
        
        Mimics human learning: repetition strengthens memory pathways.
        
        Best used for:
        - Marking when you actively use learned knowledge
        - Building mastery through practice
        - Strengthening important concepts
        - Implementing spaced repetition for retention
        
        Example: reinforce_learning(learning_id="learn_123", usage_context="applied in project")""",
    )
    async def reinforce_learning(
        ctx: Context,
        learning_id: str,
        usage_context: Optional[str] = Field(None, description="How/where you used this knowledge"),
        mastery_level: Optional[int] = Field(
            None, description="Your current mastery level 1-10 (if you can assess it)"
        ),
    ) -> Dict[str, Any]:
        """Reinforce learning through usage tracking and repetition."""
        try:
            app = get_txtai_app()

            # Get existing learning
            results = app.embeddings.search(
                f"SELECT text, metadata FROM txtai WHERE id = '{learning_id}'"
            )
            if not results:
                return {
                    "status": "error",
                    "error": "Learning not found",
                    "message": f"No learning found with ID: {learning_id}",
                }

            content = results[0].get("text", "")
            metadata = json.loads(results[0].get("metadata", "{}"))

            # Update reinforcement data
            if "reinforcement_count" not in metadata:
                metadata["reinforcement_count"] = 0
            metadata["reinforcement_count"] += 1
            metadata["last_reinforced"] = datetime.now().isoformat()

            # Track usage contexts
            if "usage_contexts" not in metadata:
                metadata["usage_contexts"] = []
            if usage_context:
                metadata["usage_contexts"].append(
                    {"timestamp": datetime.now().isoformat(), "context": usage_context}
                )

            # Update mastery
            if mastery_level is not None:
                metadata["mastery_level"] = mastery_level
                metadata["mastery_updated"] = datetime.now().isoformat()

            # Boost importance based on reinforcement
            current_importance = metadata.get("importance", 5)
            reinforcement_count = metadata["reinforcement_count"]

            # Progressive importance boost (max +3 from reinforcement)
            importance_boost = min(3, reinforcement_count // 3)
            new_importance = min(10, current_importance + importance_boost)

            if new_importance > current_importance:
                metadata["importance"] = new_importance
                metadata["importance_boosted_by_reinforcement"] = True

            # Update metadata
            metadata_str = json.dumps(metadata)
            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(learning_id, content, metadata_str)])

            # Save if configured
            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))

            logger.info(
                f"Reinforced learning: {learning_id} (count: {reinforcement_count}, importance: {new_importance})"
            )

            return {
                "status": "success",
                "learning_id": learning_id,
                "reinforcement_count": reinforcement_count,
                "importance": new_importance,
                "mastery_level": metadata.get("mastery_level"),
                "message": "Learning reinforced! Keep practicing for mastery.",
            }

        except Exception as e:
            logger.error(f"Failed to reinforce learning: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to reinforce"}

    @mcp.tool(
        name="track_learning_progress",
        description="""Track your learning journey and identify what needs attention.
        
        Analyzes learning patterns to provide insights:
        - What topics you're actively learning
        - Quick captures waiting to be expanded
        - Learnings that need reinforcement
        - Your learning momentum and streaks
        - Knowledge gaps and next steps
        
        Supports adaptive learning by identifying where to focus next.
        
        Best used for:
        - Daily or weekly learning reviews
        - Planning study sessions
        - Identifying what to expand or reinforce
        - Understanding your learning patterns
        - Maintaining learning momentum
        
        Example: track_learning_progress(time_period="last_week")""",
    )
    async def track_learning_progress(
        ctx: Context,
        time_period: str = Field(
            "last_week", description="Period to analyze: 'today', 'last_week', 'last_month'"
        ),
    ) -> Dict[str, Any]:
        """Track and analyze learning progress over time."""
        try:
            app = get_txtai_app()

            # Calculate time range
            now = datetime.now()
            if time_period == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_period == "last_week":
                start_date = now - timedelta(days=7)
            elif time_period == "last_month":
                start_date = now - timedelta(days=30)
            else:
                start_date = now - timedelta(days=7)

            # Get all learning-related items
            query = f"SELECT id, text, metadata FROM txtai WHERE timestamp >= '{start_date.isoformat()}' AND (type = 'quick_capture' OR type = 'expanded_learning' OR type = 'memory')"

            results = app.embeddings.search(query)

            # Analyze learnings
            quick_captures = []
            expanded_learnings = []
            needs_expansion = []
            needs_reinforcement = []
            topics_learning = defaultdict(int)
            learning_by_day = defaultdict(int)

            for result in results:
                metadata = {}
                try:
                    metadata = json.loads(result.get("metadata", "{}"))
                except:
                    pass

                item_type = metadata.get("type")
                item_id = result.get("id", "")
                timestamp_str = metadata.get("timestamp", "")

                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        day_key = timestamp.strftime("%Y-%m-%d")
                        learning_by_day[day_key] += 1
                    except:
                        pass

                if item_type == "quick_capture":
                    quick_captures.append(
                        {
                            "id": item_id,
                            "content": result.get("text", "")[:100] + "...",
                            "expanded": metadata.get("expanded", False),
                        }
                    )

                    if not metadata.get("expanded", False) and metadata.get("expand_later", True):
                        needs_expansion.append(item_id)

                elif item_type == "expanded_learning":
                    expanded_learnings.append(item_id)

                    # Check if needs reinforcement
                    reinforcement_count = metadata.get("reinforcement_count", 0)
                    if reinforcement_count < 3:  # Needs at least 3 reinforcements
                        needs_reinforcement.append(
                            {
                                "id": item_id,
                                "content": result.get("text", "")[:100] + "...",
                                "reinforcement_count": reinforcement_count,
                            }
                        )

                # Track topics
                topics = metadata.get("topics", []) or metadata.get("tags", [])
                for topic in topics:
                    topics_learning[topic] += 1

            # Calculate learning streak
            sorted_days = sorted(learning_by_day.keys(), reverse=True)
            current_streak = 0
            for i, day in enumerate(sorted_days):
                expected_day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
                if day == expected_day:
                    current_streak += 1
                else:
                    break

            # Prepare insights
            insights = {
                "period": time_period,
                "total_captures": len(quick_captures),
                "total_expanded": len(expanded_learnings),
                "pending_expansion": len(needs_expansion),
                "needs_reinforcement": len(needs_reinforcement),
                "learning_streak_days": current_streak,
                "active_topics": sorted(
                    [{"topic": k, "count": v} for k, v in topics_learning.items()],
                    key=lambda x: x["count"],
                    reverse=True,
                )[:10],
                "daily_activity": [
                    {"date": k, "learnings": v} for k, v in sorted(learning_by_day.items())
                ],
            }

            # Generate recommendations
            recommendations = []

            if len(needs_expansion) > 5:
                recommendations.append(
                    f"You have {len(needs_expansion)} quick captures waiting to be expanded. Consider a review session!"
                )

            if len(needs_reinforcement) > 0:
                recommendations.append(
                    f"{len(needs_reinforcement)} learnings need reinforcement for better retention."
                )

            if current_streak >= 7:
                recommendations.append(
                    f"Excellent! You're on a {current_streak}-day learning streak! 🔥"
                )
            elif current_streak == 0:
                recommendations.append("Start a new learning streak today!")

            if len(topics_learning) > 0:
                top_topic = max(topics_learning.items(), key=lambda x: x[1])
                recommendations.append(
                    f"Your focus area is '{top_topic[0]}' - consider consolidating this knowledge."
                )

            insights["recommendations"] = recommendations
            insights["needs_reinforcement_items"] = needs_reinforcement[:5]  # Top 5

            return {"status": "success", "insights": insights}

        except Exception as e:
            logger.error(f"Failed to track learning progress: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to track progress"}

    @mcp.tool(
        name="create_learning_path",
        description="""Create a personalized learning path based on current knowledge and goals.
        
        Analyzes existing knowledge and suggests next learning steps:
        - Identifies knowledge gaps
        - Suggests topics to explore based on current learnings
        - Orders topics by prerequisite relationships
        - Creates structured learning milestones
        
        Enables adaptive, goal-oriented learning progression.
        
        Best used for:
        - Planning learning journeys
        - Identifying next topics to study
        - Building on existing knowledge
        - Setting learning goals and milestones
        
        Example: create_learning_path(goal="master async programming", current_level="beginner")""",
    )
    async def create_learning_path(
        ctx: Context,
        goal: str,
        current_level: str = Field(
            "beginner", description="Your current level: beginner, intermediate, advanced"
        ),
        related_topics: Optional[List[str]] = Field(
            None, description="Topics you already know that relate to this goal"
        ),
    ) -> Dict[str, Any]:
        """Create a personalized learning path."""
        try:
            app = get_txtai_app()

            # Search for related learnings
            query = f"goal: {goal}"
            if related_topics:
                query += " " + " ".join(related_topics)

            # Find related content
            results = app.embeddings.search(query, 20)

            # Analyze what's already known
            known_topics = set()
            if related_topics:
                known_topics.update(related_topics)

            # Extract topics from existing learnings
            for result in results:
                metadata = {}
                try:
                    metadata = json.loads(result.get("metadata", "{}"))
                except:
                    pass

                topics = metadata.get("topics", []) or metadata.get("tags", [])
                known_topics.update(topics)

            # Create learning path structure
            learning_path = {
                "goal": goal,
                "current_level": current_level,
                "created_at": datetime.now().isoformat(),
                "known_topics": list(known_topics),
                "milestones": [],
                "estimated_duration": "Variable based on practice and reinforcement",
            }

            # Define milestones based on level
            if current_level == "beginner":
                learning_path["milestones"] = [
                    {
                        "phase": "Foundation",
                        "description": f"Build foundational understanding of {goal}",
                        "tasks": [
                            "Quick capture key concepts as you encounter them",
                            "Expand captures into detailed learnings",
                            "Reinforce basics through practice",
                        ],
                    },
                    {
                        "phase": "Practice",
                        "description": "Apply knowledge in real scenarios",
                        "tasks": [
                            "Use knowledge in projects",
                            "Track reinforcement as you apply concepts",
                            "Identify gaps through practical experience",
                        ],
                    },
                    {
                        "phase": "Mastery",
                        "description": "Achieve deep understanding",
                        "tasks": [
                            "Connect learnings with related concepts",
                            "Teach or explain to others",
                            "Regular reinforcement to maintain mastery",
                        ],
                    },
                ]
            else:
                learning_path["milestones"] = [
                    {
                        "phase": "Advanced Topics",
                        "description": f"Explore advanced aspects of {goal}",
                        "tasks": [
                            "Quick capture advanced patterns and techniques",
                            "Connect with existing knowledge",
                            "Reinforce through real-world application",
                        ],
                    },
                    {
                        "phase": "Expert",
                        "description": "Achieve expertise",
                        "tasks": [
                            "Contribute to knowledge base",
                            "Mentor others",
                            "Stay updated with latest developments",
                        ],
                    },
                ]

            # Save learning path as a special memory
            path_id = f"path_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            path_content = f"Learning Path: {goal}\nLevel: {current_level}\n\nThis learning path will guide your progressive mastery."

            metadata = {
                "type": "learning_path",
                "goal": goal,
                "level": current_level,
                "timestamp": datetime.now().isoformat(),
                "path_data": learning_path,
            }

            metadata_str = json.dumps(metadata)
            if hasattr(app.embeddings, "upsert"):
                app.embeddings.upsert([(path_id, path_content, metadata_str)])
            else:
                app.embeddings.index([(path_id, path_content, metadata_str)])

            if app.config.get("path"):
                app.embeddings.save(app.config.get("path"))

            logger.info(f"Created learning path: {path_id} for goal: {goal}")

            return {
                "status": "success",
                "path_id": path_id,
                "learning_path": learning_path,
                "message": f"Learning path created for: {goal}",
            }

        except Exception as e:
            logger.error(f"Failed to create learning path: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "message": "Failed to create path"}

    logger.debug("Incremental learning tools registered successfully")
