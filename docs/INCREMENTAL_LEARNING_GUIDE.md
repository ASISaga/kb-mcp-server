# Incremental Learning Tools - Quick Reference

## Overview

Incremental learning tools enable "on the go" continuous knowledge acquisition and progressive refinement. These tools mirror how humans learn in real-world scenarios - capturing quick insights, refining understanding over time, and reinforcing through practice.

## Tools

### 1. quick_capture

**Purpose**: Rapidly capture learning moments without interrupting your flow

```python
await quick_capture(
    content="Event loop manages async tasks without blocking",
    context="reading async docs",
    tags=["python", "async"],
    expand_later=True
)
```

**Best for**:
- Capturing fleeting thoughts during study
- Recording "aha moments" in real-time
- Noting questions as they arise
- Building knowledge without interruption

**Returns**: `capture_id` for later expansion

---

### 2. expand_learning

**Purpose**: Transform quick captures into comprehensive knowledge

```python
await expand_learning(
    capture_id="quick_20241112_103000",
    expanded_content="Detailed explanation of event loop mechanics...",
    importance=8,
    topics=["python", "async", "event-loop"],
    related_to=["learn_20241110_120000"],
    key_insight="Event loop enables concurrent I/O without threading"
)
```

**Best for**:
- Reviewing and deepening quick captures
- Adding context and connections
- Extracting key insights
- Progressive knowledge building

**Returns**: `expanded_id` and marks original as expanded

---

### 3. reinforce_learning

**Purpose**: Strengthen knowledge through spaced repetition

```python
await reinforce_learning(
    learning_id="learn_20241112_140000",
    usage_context="Applied in async web scraper project",
    mastery_level=7
)
```

**Best for**:
- Tracking when you use learned knowledge
- Implementing spaced repetition
- Building long-term retention
- Measuring mastery progression

**Returns**: Reinforcement count, updated importance, mastery level

**Features**:
- Auto-boosts importance based on usage
- Tracks usage contexts and patterns
- Supports mastery level tracking (1-10)

---

### 4. track_learning_progress

**Purpose**: Monitor learning journey and get recommendations

```python
progress = await track_learning_progress(
    time_period="last_week"
)
```

**Returns**:
```python
{
    "total_captures": 15,
    "total_expanded": 8,
    "pending_expansion": 7,
    "needs_reinforcement": 3,
    "learning_streak_days": 5,
    "active_topics": [
        {"topic": "python", "count": 10},
        {"topic": "async", "count": 8}
    ],
    "recommendations": [
        "You have 7 quick captures waiting to be expanded",
        "3 learnings need reinforcement for better retention",
        "Excellent! You're on a 5-day learning streak! 🔥"
    ]
}
```

**Best for**:
- Daily/weekly learning reviews
- Planning study sessions
- Identifying what needs attention
- Maintaining learning momentum

---

### 5. create_learning_path

**Purpose**: Build personalized learning roadmaps

```python
path = await create_learning_path(
    goal="master async programming in Python",
    current_level="intermediate",
    related_topics=["event-loop", "coroutines", "asyncio"]
)
```

**Returns**:
```python
{
    "path_id": "path_20241112_150000",
    "learning_path": {
        "goal": "master async programming in Python",
        "current_level": "intermediate",
        "milestones": [
            {
                "phase": "Advanced Topics",
                "description": "Explore advanced async patterns",
                "tasks": [
                    "Quick capture advanced patterns",
                    "Connect with existing knowledge",
                    "Reinforce through practice"
                ]
            },
            {
                "phase": "Expert",
                "description": "Achieve mastery",
                "tasks": [
                    "Contribute to knowledge base",
                    "Mentor others",
                    "Stay updated"
                ]
            }
        ]
    }
}
```

**Best for**:
- Planning learning journeys
- Identifying next steps
- Setting learning goals
- Structured progression

---

## Complete Workflow Examples

### Example 1: Daily Learning Session

```python
# Morning: Quick captures while reading
await quick_capture(
    content="asyncio.gather() runs tasks concurrently",
    context="async tutorial",
    tags=["python", "async", "asyncio"]
)

await quick_capture(
    content="await pauses function until task completes",
    context="async tutorial",
    tags=["python", "async", "await"]
)

# Evening: Expand and reinforce
# Get today's captures
progress = await track_learning_progress(period="today")

# Expand important captures
for capture in progress["quick_captures"]:
    if not capture["expanded"]:
        await expand_learning(
            capture_id=capture["id"],
            expanded_content="Detailed understanding...",
            importance=7
        )

# Reinforce what you practiced
await reinforce_learning(
    learning_id="learn_xyz",
    usage_context="Built concurrent API client",
    mastery_level=6
)
```

### Example 2: Weekly Review

```python
# Review week's progress
progress = await track_learning_progress(period="last_week")

print(f"Learning streak: {progress['learning_streak_days']} days")
print(f"Captures to expand: {progress['pending_expansion']}")
print(f"Topics studied: {progress['active_topics']}")

# Expand pending captures
for rec in progress["recommendations"]:
    print(rec)

# Create next week's learning path
if "python" in progress["active_topics"]:
    path = await create_learning_path(
        goal="deepen Python async knowledge",
        current_level="intermediate"
    )
```

### Example 3: Project-Based Learning

```python
# Start of project
path = await create_learning_path(
    goal="build async web scraper",
    current_level="beginner",
    related_topics=["http", "async"]
)

# During development - capture learnings
await quick_capture(
    content="aiohttp better than requests for async",
    context="web scraping project",
    tags=["python", "async", "http", "project"]
)

# Encounter challenge - capture solution
capture = await quick_capture(
    content="Rate limiting solved with semaphore",
    context="web scraper bug fix",
    tags=["async", "rate-limiting", "solution"]
)

# Later - expand the solution
await expand_learning(
    capture_id=capture["capture_id"],
    expanded_content="asyncio.Semaphore(n) limits concurrent tasks...",
    importance=9,
    key_insight="Semaphores prevent overwhelming APIs with requests"
)

# Applied in next project - reinforce
await reinforce_learning(
    learning_id=...,
    usage_context="Applied to API client project",
    mastery_level=8
)
```

## Integration with Other Tools

### With Memory Tools

```python
# Capture -> Expand -> Store as Memory
capture = await quick_capture(content="...", tags=["important"])

expanded = await expand_learning(
    capture_id=capture["capture_id"],
    expanded_content="...",
    importance=9
)

# Important learnings can be stored as memories
await store_memory(
    content=expanded_content,
    importance=9,
    topics=["key-concept"],
    source="incremental-learning"
)
```

### With Conversation Tools

```python
# Conversation triggers learning
await store_conversation_turn(
    user_message="How does async/await work?",
    assistant_response="...",
    topics=["python", "async"]
)

# Capture key insight from conversation
await quick_capture(
    content="await releases control back to event loop",
    context="conversation about async",
    tags=["python", "async", "key-insight"]
)
```

## Best Practices

1. **Capture Immediately**: Don't wait - capture insights as they occur
2. **Review Regularly**: Set aside time daily/weekly to expand captures
3. **Reinforce Through Use**: Mark when you actually apply knowledge
4. **Track Progress**: Use progress tracking to stay motivated
5. **Build Paths**: Create learning paths for structured goals
6. **Measure Mastery**: Update mastery levels as you progress
7. **Connect Knowledge**: Link related learnings when expanding
8. **Celebrate Streaks**: Maintain learning momentum with daily practice

## Quick Commands

```bash
# Capture on the go
quick_capture("Brief insight", context="what you were doing", tags=[...])

# End of day
track_learning_progress(period="today")

# Weekly review
track_learning_progress(period="last_week")

# Plan learning
create_learning_path(goal="...", current_level="...")

# Expand capture
expand_learning(capture_id="...", expanded_content="...", importance=8)

# Mark usage
reinforce_learning(learning_id="...", usage_context="...")
```

## Mastery Levels

- **1-3**: Aware (heard of it, basic understanding)
- **4-6**: Practicing (can use with documentation)
- **7-8**: Proficient (can use without help)
- **9-10**: Expert (can teach, innovate)

Track your progression and celebrate growth!
