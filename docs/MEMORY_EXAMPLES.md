# Memory Enhancement Examples

This document demonstrates the new human-like memory capabilities added to the kb-mcp-server.

## Overview

The enhanced MCP server now functions as sophisticated human memory, providing:
- **Temporal awareness** - memories with timestamps
- **Importance weighting** - priority-based memory management
- **Contextual associations** - linking through people, places, topics
- **Reflection capabilities** - pattern analysis and insights
- **Conversation continuity** - session-based dialogue tracking

## Memory Tools Examples

### 1. Storing Memories with Rich Context

```python
# Store a learning experience
await store_memory(
    content="Learned about vector embeddings for semantic search. Key insight: embeddings capture meaning, not just keywords.",
    importance=8,
    timestamp="2024-11-12T10:30:00",
    topics=["machine-learning", "embeddings", "semantic-search"],
    source="reading",
    sentiment="positive"
)

# Store a meeting memory
await store_memory(
    content="Team meeting: Decided to use Python for the ML pipeline. Bob suggested using txtai for embeddings.",
    importance=7,
    topics=["project", "meetings", "decisions"],
    people=["Bob", "Alice", "Charlie"],
    places=["conference_room_a"],
    sentiment="neutral"
)

# Store a personal experience
await store_memory(
    content="Had a great discussion about async programming patterns. Finally understood how event loops work!",
    importance=9,
    topics=["python", "async", "learning"],
    people=["mentor_alice"],
    sentiment="positive",
    related_to=["mem_20241112_093000"]
)
```

### 2. Time-Based Memory Recall

```python
# Recall recent memories
recent = await recall_by_time(
    period="last_week",
    min_importance=7
)

# Recall memories from yesterday
yesterday = await recall_by_time(
    period="yesterday",
    topics=["python"]
)

# Recall from specific date range
range_memories = await recall_by_time(
    period="2024-11-01:2024-11-10",
    topics=["project"],
    min_importance=6
)

# Recall today's important learnings
today_important = await recall_by_time(
    period="today",
    min_importance=8
)
```

### 3. Finding Contextual Associations

```python
# Find all memories about a person
bob_memories = await find_associations(
    people=["Bob"],
    limit=20
)

# Find memories from a specific place
office_memories = await find_associations(
    places=["conference_room_a", "office"],
    min_importance=5
)

# Find positive memories about a topic
positive_learning = await find_associations(
    topics=["learning", "python"],
    sentiment="positive"
)

# Complex association search
project_team_memories = await find_associations(
    topics=["project_alpha"],
    people=["Alice", "Bob"],
    min_importance=6,
    sentiment="positive"
)
```

### 4. Memory Reflection and Insights

```python
# Reflect on recent topic patterns
topic_insights = await reflect_on_memories(
    aspect="topics",
    time_period="last_month"
)
# Returns: Top topics, frequency counts, recommendations

# Analyze importance patterns
importance_analysis = await reflect_on_memories(
    aspect="importance",
    time_period="last_week"
)
# Returns: Average importance, high-importance count, distribution

# Comprehensive reflection
full_insights = await reflect_on_memories(
    aspect="all",
    time_period="last_month"
)
# Returns: Topics, importance, sentiment, frequency, timeline analysis
```

### 5. Dynamic Importance Updates

```python
# Increase importance after reflection
await update_memory_importance(
    memory_id="mem_20241112_100000",
    new_importance=9,
    reason="Referenced multiple times in project discussions"
)

# Decrease importance of outdated info
await update_memory_importance(
    memory_id="mem_20241001_120000",
    new_importance=3,
    reason="Information superseded by newer approach"
)
```

## Conversation Tools Examples

### 1. Tracking Conversations

```python
# Store a conversation turn
await store_conversation_turn(
    user_message="How do I implement async/await in Python?",
    assistant_response="To implement async/await in Python, you need to define async functions using 'async def'...",
    session_id="learning_async",
    topics=["python", "async", "programming"],
    importance=7,
    user_sentiment="curious"
)

# Continue the conversation
await store_conversation_turn(
    user_message="Can you show me an example with asyncio.gather()?",
    assistant_response="Here's an example using asyncio.gather() to run multiple async functions concurrently...",
    session_id="learning_async",
    topics=["python", "async", "asyncio"],
    importance=8,
    user_sentiment="engaged"
)
```

### 2. Recalling Conversation History

```python
# Get conversation history for a session
history = await recall_conversation_history(
    session_id="learning_async",
    limit=10
)

# Filter by topic
python_convos = await recall_conversation_history(
    topics=["python"],
    limit=20
)

# Get recent conversations
recent_convos = await recall_conversation_history(
    since="2024-11-10T00:00:00",
    limit=15
)
```

### 3. Session Summaries

```python
# Generate and save session summary
summary = await summarize_conversation_session(
    session_id="learning_async",
    save_summary=True
)
# Returns: Topics discussed, sentiment, high-importance turns, recommendations
```

### 4. Semantic Conversation Search

```python
# Find relevant past conversations
relevant = await search_conversations(
    query="async programming patterns",
    min_importance=6,
    limit=5
)

# Search within a specific session
session_search = await search_conversations(
    query="error handling",
    session_id="learning_async",
    limit=10
)
```

## Combined Workflow Example

Here's a realistic workflow combining multiple tools:

```python
# Day 1: Learning session
# Store what you learned
await store_memory(
    content="Studied Python async patterns. Key concepts: event loop, coroutines, tasks",
    importance=8,
    topics=["python", "async", "learning"],
    source="study",
    sentiment="positive"
)

# Store the conversation
await store_conversation_turn(
    user_message="I'm learning about async. What are the key concepts?",
    assistant_response="The key concepts are: event loop, coroutines, and tasks...",
    session_id="async_learning_day1",
    topics=["python", "async"],
    importance=7
)

# Day 2: Review and continue
# Recall what you learned yesterday
yesterday_learning = await recall_by_time(
    period="yesterday",
    topics=["async"],
    min_importance=7
)

# Continue learning
await store_memory(
    content="Practiced async/await with real examples. Built a concurrent web scraper!",
    importance=9,
    topics=["python", "async", "project"],
    sentiment="excited",
    related_to=[yesterday_learning[0]["id"]]
)

# Week later: Reflection
# What have I been focusing on?
weekly_insights = await reflect_on_memories(
    aspect="all",
    time_period="last_week"
)
# Recommendations: "Your most frequent topic is 'async' - consider consolidating related memories"

# Find all async-related memories
async_memories = await find_associations(
    topics=["async"],
    min_importance=6
)

# Boost importance of frequently referenced memory
await update_memory_importance(
    memory_id=async_memories[0]["id"],
    new_importance=9,
    reason="Core concept referenced in multiple projects"
)

# Review conversation history
all_async_convos = await recall_conversation_history(
    topics=["async"]
)

# Generate learning summary
session_summary = await summarize_conversation_session(
    session_id="async_learning_day1",
    save_summary=True
)
```

## Graph Tools Examples

The server also now includes graph tools for relationship mapping:

```python
# Create a knowledge graph
await create_graph(
    nodes=[
        {"id": "python", "text": "Python Programming Language", "type": "language"},
        {"id": "async", "text": "Asynchronous Programming", "type": "concept"},
        {"id": "asyncio", "text": "asyncio Library", "type": "library"}
    ],
    relationships=[
        {"source": "python", "target": "async", "relationship": "supports"},
        {"source": "asyncio", "target": "async", "relationship": "implements"},
        {"source": "python", "target": "asyncio", "relationship": "includes"}
    ]
)

# Analyze the graph for insights
await analyze_graph()
```

## Benefits of Memory-Enhanced MCP Server

1. **Temporal Context**: Track when information was learned or discussed
2. **Priority Management**: Focus on what's important while retaining details
3. **Associative Recall**: Find information through multiple pathways
4. **Self-Awareness**: Understand your own learning and interaction patterns
5. **Continuous Learning**: Build knowledge that evolves over time
6. **Session Continuity**: Resume conversations with full context
7. **Insight Generation**: Discover patterns you might have missed
8. **Adaptive Importance**: Memory priority adjusts based on relevance

## Use Cases

### Personal Learning Assistant
- Track learning progress over time
- Identify knowledge gaps
- Review and consolidate learnings
- Maintain conversation context across study sessions

### Project Memory System
- Remember team discussions and decisions
- Track who said what and when
- Associate information with project phases
- Generate project timeline insights

### Personal Knowledge Base
- Build a searchable memory of experiences
- Track relationships with people and places
- Identify life patterns and trends
- Maintain rich context for personal growth

### AI Agent Memory
- Provide agents with human-like memory capabilities
- Enable temporal awareness in AI interactions
- Support multi-session conversational continuity
- Allow agents to reflect on their own knowledge
