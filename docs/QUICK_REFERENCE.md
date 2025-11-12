# Quick Reference: Human Memory Tools

## Memory Tools

### store_memory
Store information with rich context.

```python
await store_memory(
    content="Python async patterns for concurrent programming",
    importance=8,
    topics=["python", "async"],
    people=["Alice"],
    sentiment="positive"
)
```

### recall_by_time
Retrieve memories from specific time periods.

```python
# Last week's memories
await recall_by_time(period="last_week", min_importance=7)

# Yesterday
await recall_by_time(period="yesterday", topics=["python"])

# Date range
await recall_by_time(period="2024-11-01:2024-11-10")
```

### find_associations
Find memories by context.

```python
# By people
await find_associations(people=["Alice", "Bob"])

# By topics
await find_associations(topics=["project"], min_importance=6)

# Multiple filters
await find_associations(
    topics=["learning"],
    sentiment="positive",
    min_importance=7
)
```

### reflect_on_memories
Analyze memory patterns.

```python
# Topic patterns
await reflect_on_memories(aspect="topics", time_period="last_month")

# All aspects
await reflect_on_memories(aspect="all")
```

### update_memory_importance
Adjust memory priority.

```python
await update_memory_importance(
    memory_id="mem_123",
    new_importance=9,
    reason="Frequently referenced"
)
```

## Conversation Tools

### store_conversation_turn
Track conversations.

```python
await store_conversation_turn(
    user_message="How do I use async?",
    assistant_response="Use async def...",
    session_id="learning_session",
    topics=["python", "async"],
    importance=7
)
```

### recall_conversation_history
Get conversation history.

```python
# By session
await recall_conversation_history(session_id="learning_session")

# By topic
await recall_conversation_history(topics=["python"])

# Recent conversations
await recall_conversation_history(since="2024-11-10T00:00:00")
```

### summarize_conversation_session
Generate session summary.

```python
await summarize_conversation_session(
    session_id="learning_session",
    save_summary=True
)
```

### search_conversations
Semantic search.

```python
await search_conversations(
    query="async programming patterns",
    min_importance=6
)
```

## Graph Tools

### create_graph
Build knowledge graphs.

```python
await create_graph(
    nodes=[
        {"id": "python", "text": "Python Language"},
        {"id": "async", "text": "Async Programming"}
    ],
    relationships=[
        {"source": "python", "target": "async", "relationship": "supports"}
    ]
)
```

## Common Patterns

### Learning Session
```python
# Store learning
await store_memory(
    content="Learned about Python async",
    importance=8,
    topics=["python", "async"]
)

# Track conversation
await store_conversation_turn(
    user_message="Teach me async",
    assistant_response="...",
    session_id="async_learning"
)

# Review later
history = await recall_conversation_history(session_id="async_learning")
memories = await recall_by_time(period="today", topics=["async"])
```

### Weekly Review
```python
# Get week's insights
insights = await reflect_on_memories(
    aspect="all",
    time_period="last_week"
)

# Find important memories
important = await recall_by_time(
    period="last_week",
    min_importance=8
)

# Update priorities
for memory in important:
    await update_memory_importance(
        memory_id=memory["id"],
        new_importance=memory["importance"] + 1,
        reason="Weekly review boost"
    )
```

### Project Context
```python
# Store project decision
await store_memory(
    content="Decided to use Python for ML pipeline",
    importance=9,
    topics=["project", "decisions"],
    people=["Alice", "Bob"],
    places=["conference_room"]
)

# Find all project memories
project_memories = await find_associations(
    topics=["project"],
    min_importance=7
)

# Get conversations about project
project_convos = await recall_conversation_history(
    topics=["project"],
    limit=20
)
```
