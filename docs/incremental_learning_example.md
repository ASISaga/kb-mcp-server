# Incremental Learning Example

This example demonstrates how an AI agent can use the knowledge base management tools to build and evolve a persistent knowledge base.

## Setup

```bash
# Initialize a markdown knowledge base directory
mkdir -p ./my_knowledge_base

# Start the MCP server with the knowledge base
kb-mcp-server --embeddings ./my_knowledge_base
```

## Agent Learning Workflow

### 1. Creating Initial Knowledge

The agent learns something new and saves it to markdown:

```python
# Save new knowledge to markdown file
result = await save_to_markdown(
    filename="python_basics.md",
    content="""# Python Basics

Python is a high-level programming language known for its simplicity and readability.

## Key Features
- Dynamic typing
- Interpreted language
- Rich standard library
- Cross-platform support
""",
    kb_directory="./my_knowledge_base",
    metadata={
        "category": "programming",
        "language": "python",
        "level": "beginner"
    }
)
```

### 2. Adding to the Knowledge Base

The agent indexes the markdown file:

```python
# Reload knowledge base from markdown directory
result = await reload_markdown_kb(
    kb_directory="./my_knowledge_base"
)
# Returns: {"status": "success", "documents_loaded": 4, ...}
```

### 3. Refining Existing Knowledge

Later, the agent learns more and updates the document:

```python
# Update existing markdown file with new information
result = await update_markdown_file(
    filename="python_basics.md",
    content="""
## Advanced Features (Python 3.12+)
- Type hints with generics
- Pattern matching
- Structural pattern matching
- Improved error messages
""",
    kb_directory="./my_knowledge_base",
    mode="append"
)
```

### 4. Organizing Knowledge

The agent semantically organizes related documents:

```python
# Find and organize all Python-related documents
result = await organize_knowledge(
    query="python programming language",
    category="python-language",
    limit=20
)
```

### 5. Consolidating Duplicate Information

The agent finds and consolidates similar documents:

```python
# Find duplicate or very similar documents
result = await consolidate_knowledge(
    topic="python functions",
    similarity_threshold=0.85,
    limit=50
)
```

## Complete Learning Cycle

```python
# 1. Agent encounters new information
new_info = "Python asyncio enables concurrent programming..."

# 2. Agent saves to markdown
await save_to_markdown(
    filename="python_asyncio.md",
    content=f"# Python Asyncio\n\n{new_info}",
    kb_directory="./my_knowledge_base",
    metadata={"category": "python", "topic": "concurrency"}
)

# 3. Agent indexes new knowledge
await reload_markdown_kb(kb_directory="./my_knowledge_base")

# 4. Agent can now use this knowledge
results = await semantic_search(
    query="How does Python handle concurrent programming?",
    limit=3
)
```

## Benefits

1. **Persistent Memory**: Knowledge persists across agent sessions
2. **Incremental Learning**: Agent continuously improves its knowledge
3. **Human Review**: Humans can read and edit markdown files
4. **Version Control**: Full history of knowledge evolution via git
5. **Semantic Organization**: Automatic categorization and structure
6. **Self-Awareness**: Agent understands and manages its own knowledge
7. **Collaboration**: Agent and human can co-evolve the knowledge base
