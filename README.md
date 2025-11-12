[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/geeksfino-kb-mcp-server-badge.png)](https://mseep.ai/app/geeksfino-kb-mcp-server)

# Embedding MCP Server

A Model Context Protocol (MCP) server implementation powered by txtai, providing semantic search, knowledge graph capabilities, AI-driven text processing, and **intelligent summarization** through a standardized interface.

## The Power of txtai: All-in-one Embeddings Database

This project leverages [txtai](https://github.com/neuml/txtai), an all-in-one embeddings database for RAG leveraging semantic search, knowledge graph construction, and language model workflows. txtai offers several key advantages:

- **Unified Vector Database**: Combines vector indexes, graph networks, and relational databases in a single platform
- **Semantic Search**: Find information based on meaning, not just keywords
- **Knowledge Graph Integration**: Automatically build and query knowledge graphs from your data
- **Portable Knowledge Bases**: Save entire knowledge bases as compressed archives (.tar.gz) that can be easily shared and loaded
- **Native Markdown Support**: Load knowledge bases directly from markdown file directories without requiring tar.gz archives
- **Extensible Pipeline System**: Process text, documents, audio, images, and video through a unified API
- **Local-first Architecture**: Run everything locally without sending data to external services

## How It Works

The project contains a knowledge base builder tool and a MCP server. The knowledge base builder tool is a command-line interface for creating and managing knowledge bases. The MCP server provides a standardized interface to access the knowledge base. 

It is not required to use the knowledge base builder tool to build a knowledge base. You can always build a knowledge base using txtai's programming interface by writing a Python script or even using a jupyter notebook. As long as the knowledge base is built using txtai, it can be loaded by the MCP server. Better yet, the knowledge base can be a folder on the file system or an exported .tar.gz file. Just give it to the MCP server and it will load it.

### 1. Build a Knowledge Base with kb_builder

The `kb_builder` module provides a command-line interface for creating and managing knowledge bases:

- Process documents from various sources (files, directories, JSON)
- Extract text and create embeddings
- Build knowledge graphs automatically
- Export portable knowledge bases

Note it is possibly limited in functionality and currently only provided for convenience.

### 2. Start the MCP Server

The MCP server provides a standardized interface to access the knowledge base:

- Semantic search capabilities
- Knowledge graph querying and visualization
- Text processing pipelines (summarization, extraction, etc.)
- Full compliance with the Model Context Protocol

## Installation

### Recommended: Using uv with Python 3.10+

We recommend using [uv](https://github.com/astral-sh/uv) with Python 3.10 or newer for the best experience. This provides better dependency management and ensures consistent behavior.

```bash
# Install uv if you don't have it already
pip install -U uv

# Create a virtual environment with Python 3.10 or newer
uv venv --python=3.10  # or 3.11, 3.12, etc.

# Activate the virtual environment (bash/zsh)
source .venv/bin/activate
# For fish shell
# source .venv/bin/activate.fish

# Install from PyPI
uv pip install kb-mcp-server
```

> **Note**: We pin transformers to version 4.49.0 to avoid deprecation warnings about `transformers.agents.tools` that appear in version 4.50.0 and newer. If you use a newer version of transformers, you may see these warnings, but they don't affect functionality.

### Using conda

```bash
# Create a new conda environment (optional)
conda create -n embedding-mcp python=3.10
conda activate embedding-mcp

# Install from PyPI
pip install kb-mcp-server
```

### From Source

```bash
# Create a new conda environment
conda create -n embedding-mcp python=3.10
conda activate embedding-mcp

# Clone the repository
git clone https://github.com/Geeksfino/kb-mcp-server.git.git
cd kb-mcp-server

# Install dependencies
pip install -e .
```

### Using uv (Faster Alternative)

```bash
# Install uv if not already installed
pip install uv

# Create a new virtual environment
uv venv
source .venv/bin/activate

# Option 1: Install from PyPI
uv pip install kb-mcp-server

# Option 2: Install from source (for development)
uv pip install -e .
```

### Using uvx (No Installation Required)

[uvx](https://github.com/astral-sh/uv) allows you to run packages directly from PyPI without installing them:

```bash
# Run the MCP server
uvx --from kb-mcp-server@0.3.0 kb-mcp-server --embeddings /path/to/knowledge_base

# Build a knowledge base
uvx --from kb-mcp-server@0.3.0 kb-build --input /path/to/documents --config config.yml

# Search a knowledge base
uvx --from kb-mcp-server@0.3.0 kb-search /path/to/knowledge_base "Your search query"
```

## Command Line Usage

### Building a Knowledge Base

You can use the command-line tools installed from PyPI, the Python module directly, or the convenient shell scripts:

#### Building from Markdown Directories (New!)

The server now supports native markdown file directories without requiring tar.gz archives:

```bash
# Build knowledge base directly from markdown directory
kb-build build-markdown --markdown-dir /path/to/markdown_docs --config config.yml

# Export to tar.gz for portability (optional)
kb-build build-markdown --markdown-dir /path/to/markdown_docs --export my_kb.tar.gz

# Update existing knowledge base with new markdown files
kb-build build-markdown --markdown-dir /path/to/new_docs --update

# Using uvx (no installation required)
uvx --from kb-mcp-server@0.3.0 kb-build build-markdown --markdown-dir /path/to/markdown_docs
```

The markdown loader features:
- Automatically segments documents by headings for optimal chunking
- Extracts YAML frontmatter as metadata
- Recursively processes subdirectories
- Preserves document structure and relationships

#### Using the PyPI Installed Commands

```bash
# Build a knowledge base from documents
kb-build --input /path/to/documents --config config.yml

# Update an existing knowledge base with new documents
kb-build --input /path/to/new_documents --update

# Export a knowledge base for portability
kb-build --input /path/to/documents --export my_knowledge_base.tar.gz

# Search a knowledge base
kb-search /path/to/knowledge_base "What is machine learning?"

# Search with graph enhancement
kb-search /path/to/knowledge_base "What is machine learning?" --graph --limit 10
```

#### Using uvx (No Installation Required)

```bash
# Build a knowledge base from documents
uvx --from kb-mcp-server@0.3.0 kb-build --input /path/to/documents --config config.yml

# Update an existing knowledge base with new documents
uvx --from kb-mcp-server@0.3.0 kb-build --input /path/to/new_documents --update

# Export a knowledge base for portability
uvx --from kb-mcp-server@0.3.0 kb-build --input /path/to/documents --export my_knowledge_base.tar.gz

# Search a knowledge base
uvx --from kb-mcp-server@0.3.0 kb-search /path/to/knowledge_base "What is machine learning?"

# Search with graph enhancement
uvx --from kb-mcp-server@0.3.0 kb-search /path/to/knowledge_base "What is machine learning?" --graph --limit 10
```

#### Using the Python Module

```bash
# Build a knowledge base from documents
python -m kb_builder build --input /path/to/documents --config config.yml

# Update an existing knowledge base with new documents
python -m kb_builder build --input /path/to/new_documents --update

# Export a knowledge base for portability
python -m kb_builder build --input /path/to/documents --export my_knowledge_base.tar.gz
```

#### Using the Convenience Scripts

The repository includes convenient wrapper scripts that make it easier to build and search knowledge bases:

```bash
# Build a knowledge base using a template configuration
./scripts/kb_build.sh /path/to/documents technical_docs

# Build using a custom configuration file
./scripts/kb_build.sh /path/to/documents /path/to/my_config.yml

# Update an existing knowledge base
./scripts/kb_build.sh /path/to/documents technical_docs --update

# Search a knowledge base
./scripts/kb_search.sh /path/to/knowledge_base "What is machine learning?"

# Search with graph enhancement
./scripts/kb_search.sh /path/to/knowledge_base "What is machine learning?" --graph
```

Run `./scripts/kb_build.sh --help` or `./scripts/kb_search.sh --help` for more options.

### Starting the MCP Server

#### Using the PyPI Installed Command

```bash
# Start with a specific knowledge base folder
kb-mcp-server --embeddings /path/to/knowledge_base_folder

# Start with a given knowledge base archive
kb-mcp-server --embeddings /path/to/knowledge_base.tar.gz
```

#### Using uvx (No Installation Required)

```bash
# Start with a specific knowledge base folder
uvx kb-mcp-server@0.2.6 --embeddings /path/to/knowledge_base_folder

# Start with a given knowledge base archive
uvx kb-mcp-server@0.2.6 --embeddings /path/to/knowledge_base.tar.gz
```

#### Using the Python Module

```bash
# Start with a specific knowledge base folder
python -m txtai_mcp_server --embeddings /path/to/knowledge_base_folder

# Start with a given knowledge base archive
python -m txtai_mcp_server --embeddings /path/to/knowledge_base.tar.gz
```
## MCP Server Configuration

The MCP server is configured using environment variables or command-line arguments, not YAML files. YAML files are only used for configuring txtai components during knowledge base building.

Here's how to configure the MCP server:

```bash
# Start the server with command-line arguments
kb-mcp-server --embeddings /path/to/knowledge_base --host 0.0.0.0 --port 8000

# Or using uvx (no installation required)
uvx kb-mcp-server@0.2.6 --embeddings /path/to/knowledge_base --host 0.0.0.0 --port 8000

# Or using the Python module
python -m txtai_mcp_server --embeddings /path/to/knowledge_base --host 0.0.0.0 --port 8000

# Or use environment variables
export TXTAI_EMBEDDINGS=/path/to/knowledge_base
export MCP_SSE_HOST=0.0.0.0
export MCP_SSE_PORT=8000
python -m txtai_mcp_server
```

Common configuration options:
- `--embeddings`: Path to the knowledge base (required)
- `--host`: Host address to bind to (default: localhost)
- `--port`: Port to listen on (default: 8000)
- `--transport`: Transport to use, either 'sse' or 'stdio' (default: stdio)
- `--enable-causal-boost`: Enable causal boost feature for enhanced relevance scoring
- `--causal-config`: Path to custom causal boost configuration YAML file

## Configuring LLM Clients to Use the MCP Server

To configure an LLM client to use the MCP server, you need to create an MCP configuration file. Here's an example `mcp_config.json`:

### Using the server directly

If you use a virtual Python environment to install the server, you can use the following configuration - note that MCP host like Claude will not be able to connect to the server if you use a virtual environment, you need to use the absolute path to the Python executable of the virtual environment where you did "pip install" or "uv pip install", for example

```json
{
  "mcpServers": {
    "kb-server": {
      "command": "/your/home/project/.venv/bin/kb-mcp-server",
      "args": [
        "--embeddings", 
        "/path/to/knowledge_base.tar.gz"
      ],
      "cwd": "/path/to/working/directory"
    }
  }
}
```

### Using system default Python

If you use your system default Python, you can use the following configuration:

```json
{
    "rag-server": {
      "command": "python3",
      "args": [
        "-m",
        "txtai_mcp_server",
        "--embeddings",
        "/path/to/knowledge_base.tar.gz",
        "--enable-causal-boost"
      ],
      "cwd": "/path/to/working/directory"
    }
}
```

Alternatively, if you're using uvx, assuming you have uvx installed in your system via "brew install uvx" etc, or you 've installed uvx and made it globally accessible via:
```
# Create a symlink to /usr/local/bin (which is typically in the system PATH)
sudo ln -s /Users/cliang/.local/bin/uvx /usr/local/bin/uvx
```
This creates a symbolic link from your user-specific installation to a system-wide location. For macOS applications like Claude Desktop, you can modify the system-wide PATH by creating or editing a launchd configuration file:
```
# Create a plist file to set environment variables for all GUI applications
sudo nano /Library/LaunchAgents/environment.plist
```
Add this content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>my.startup</string>
  <key>ProgramArguments</key>
  <array>
    <string>sh</string>
    <string>-c</string>
    <string>launchctl setenv PATH $PATH:/Users/cliang/.local/bin</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
```

Then load it:
```
sudo launchctl load -w /Library/LaunchAgents/environment.plist
```
You'll need to restart your computer for this to take effect, though.


```json
{
  "mcpServers": {
    "kb-server": {
      "command": "uvx",
      "args": [
        "kb-mcp-server@0.2.6",
        "--embeddings", "/path/to/knowledge_base",
        "--host", "localhost",
        "--port", "8000"
      ],
      "cwd": "/path/to/working/directory"
    }
  }
}
```

Place this configuration file in a location accessible to your LLM client and configure the client to use it. The exact configuration steps will depend on your specific LLM client.

## Advanced Knowledge Base Configuration

Building a knowledge base with txtai requires a YAML configuration file that controls various aspects of the embedding process. This configuration is used by the `kb_builder` tool, not the MCP server itself.

One may need to tune segmentation/chunking strategies, embedding models, and scoring methods, as well as configure graph construction, causal boosting, weights of hybrid search, and more.

Fortunately, txtai provides a powerful YAML configuration system that requires no coding. Here's an example of a comprehensive configuration for knowledge base building:

```yaml
# Path to save/load embeddings index
path: ~/.txtai/embeddings
writable: true

# Content storage in SQLite
content:
  path: sqlite:///~/.txtai/content.db

# Embeddings configuration
embeddings:
  # Model settings
  path: sentence-transformers/nli-mpnet-base-v2
  backend: faiss
  gpu: true
  batch: 32
  normalize: true
  
  # Scoring settings
  scoring: hybrid
  hybridalpha: 0.75

# Pipeline configuration
pipeline:
  workers: 2
  queue: 100
  timeout: 300

# Question-answering pipeline
extractor:
  path: distilbert-base-cased-distilled-squad
  maxlength: 512
  minscore: 0.3

# Graph configuration
graph:
  backend: sqlite
  path: ~/.txtai/graph.db
  similarity: 0.75  # Threshold for creating graph connections
  limit: 10  # Maximum connections per node
```

### Configuration Examples

The `src/kb_builder/configs` directory contains configuration templates for different use cases and storage backends:

#### Storage and Backend Configurations
- `memory.yml`: In-memory vectors (fastest for development, no persistence)
- `sqlite-faiss.yml`: SQLite for content + FAISS for vectors (local file-based persistence)
- `postgres-pgvector.yml`: PostgreSQL + pgvector (production-ready with full persistence)

#### Domain-Specific Configurations
- `base.yml`: Base configuration template
- `code_repositories.yml`: Optimized for code repositories
- `data_science.yml`: Configured for data science documents
- `general_knowledge.yml`: General purpose knowledge base
- `research_papers.yml`: Optimized for academic papers
- `technical_docs.yml`: Configured for technical documentation

You can use these as starting points for your own configurations:

```bash
python -m kb_builder build --input /path/to/documents --config src/kb_builder/configs/technical_docs.yml

# Or use a storage-specific configuration
python -m kb_builder build --input /path/to/documents --config src/kb_builder/configs/postgres-pgvector.yml
```

## Advanced Features

### Summarization Functions (New!)

The MCP server includes intelligent summarization tools designed to help AI agents manage context size and focus on critical information:

#### Available Summarization Tools

1. **summarize_text**: Condense lengthy text to key points
   - Focuses on essential information
   - Configurable summary length
   - Optional focus areas (e.g., "errors", "warnings")
   - Prevents context overflow in AI conversations

2. **summarize_file**: Technical analysis of file contents
   - Detects file types (code, config, markdown, JSON, etc.)
   - Extracts key metrics (functions, classes, headings, etc.)
   - Provides structural overview
   - Includes file metadata

3. **summarize_directory**: Directory structure overview
   - Visual tree representation
   - File type statistics
   - Size analysis and largest files
   - Configurable depth and filters

4. **summarize_search_results**: Consolidate search findings
   - Combines multiple search results
   - Extracts common themes
   - Creates coherent summaries
   - Reduces information overload

#### Use Cases

- **Managing Context**: Keep AI conversations within token limits
- **Code Review**: Quickly understand file purposes and structure
- **Log Analysis**: Extract critical errors from verbose logs
- **Documentation**: Generate overviews of large codebases
- **Research**: Synthesize information from multiple sources

These tools are optimized for various AI providers and automatically adjust output based on content type and complexity.

### Knowledge Base Management & Incremental Learning (New!)

The MCP server now includes advanced tools for **incremental learning** and **evolving knowledge bases**, allowing AI agents to dynamically manage, organize, and refine knowledge over time.

#### Knowledge Management Tools

1. **update_document**: Modify existing documents in the knowledge base
   - Refine understanding of concepts
   - Correct errors in existing knowledge
   - Add new information to existing documents
   - Support incremental learning

2. **delete_document**: Remove outdated or incorrect information
   - Clean up the knowledge base
   - Remove duplicates
   - Delete deprecated content

3. **save_to_markdown**: Persist knowledge to markdown files
   - Create new markdown documents
   - Build git-trackable knowledge base
   - Enable version control of knowledge
   - Support human review and editing

4. **update_markdown_file**: Edit existing markdown files
   - Update documentation directly
   - Append new sections
   - Refine existing content
   - Support both replace and append modes

5. **organize_knowledge**: Semantically categorize documents
   - Group related documents
   - Create semantic hierarchies
   - Improve knowledge navigation
   - Identify knowledge clusters

6. **consolidate_knowledge**: Merge duplicate/similar documents
   - Reduce redundancy
   - Improve knowledge quality
   - Optimize storage and search
   - Identify consolidation opportunities

7. **reload_markdown_kb**: Sync knowledge base with disk
   - Reload after manual edits
   - Refresh from git pulls
   - Load newly added files
   - Synchronize in-memory and file-based knowledge

8. **list_markdown_files**: Explore knowledge base structure
   - View all markdown files
   - See file metadata and statistics
   - Understand knowledge organization
   - Plan updates and improvements

#### Incremental Learning Workflow

```python
# Agent learns new information
await save_to_markdown(
    filename="python_async.md",
    content="# Python Async/Await\n\nNew async features...",
    kb_directory="./docs",
    metadata={"category": "programming", "language": "python"}
)

# Agent refines existing knowledge
await update_document(
    document_id="python_basics",
    text="Updated content with Python 3.12 features..."
)

# Agent organizes related knowledge
await organize_knowledge(
    query="python programming",
    category="python-language",
    limit=20
)

# Agent consolidates duplicate information
await consolidate_knowledge(
    topic="docker containers",
    similarity_threshold=0.85
)

# Reload knowledge base after changes
await reload_markdown_kb(
    kb_directory="./docs"
)
```

#### Benefits of Incremental Learning

- **Evolving Knowledge**: AI agents can continuously improve their knowledge base
- **Version Control**: Markdown files can be tracked with git for history and collaboration
- **Human-AI Collaboration**: Humans can review and edit markdown files, agents can reload
- **Persistent Memory**: Knowledge persists across sessions in file-based storage
- **Semantic Organization**: Automatic categorization and consolidation of knowledge
- **Context Awareness**: Agents understand and manage their own knowledge structure

### Knowledge Graph Capabilities

The MCP server leverages txtai's built-in graph functionality to provide powerful knowledge graph capabilities:

- **Automatic Graph Construction**: Build knowledge graphs from your documents automatically
- **Graph Traversal**: Navigate through related concepts and documents
- **Path Finding**: Discover connections between different pieces of information
- **Community Detection**: Identify clusters of related information

### Human Memory Features (New!)

The MCP server now includes advanced **human-like memory** capabilities, allowing AI agents to function with temporal awareness, contextual associations, and self-reflection - key aspects of how human memory works.

#### Memory Tools

1. **store_memory**: Store information as rich, contextual memories
   - Temporal context (when was this learned/experienced?)
   - Importance/priority scoring (how significant is this?)
   - Emotional/sentiment context
   - Associated people, places, topics
   - Memory source tracking
   - Related memory linking

2. **recall_by_time**: Time-based memory retrieval
   - Recall memories from specific time periods ("last week", "yesterday", "last month")
   - Filter by topics and importance
   - Temporal pattern analysis
   - Support for date ranges

3. **find_associations**: Context-based memory discovery
   - Find memories by people, places, or topics
   - Sentiment-based filtering
   - Multi-dimensional association search
   - Build contextual understanding

4. **reflect_on_memories**: Meta-analysis and insight generation
   - Identify patterns and themes
   - Temporal trend analysis
   - Access frequency patterns
   - Sentiment distribution
   - Generate recommendations for knowledge management

5. **update_memory_importance**: Dynamic importance adjustment
   - Update memory priority based on reflection
   - Track importance change history
   - Implement spaced repetition patterns
   - Adaptive memory management

#### Conversation Memory Tools

1. **store_conversation_turn**: Track conversation history
   - Store user-assistant exchanges
   - Session-based grouping
   - Topic extraction
   - Sentiment tracking
   - Importance scoring

2. **recall_conversation_history**: Retrieve past conversations
   - Session-based recall
   - Topic filtering
   - Time-based filtering
   - Maintain conversational continuity

3. **summarize_conversation_session**: Generate session summaries
   - Identify main topics
   - Extract key decisions
   - Sentiment analysis
   - High-importance highlights
   - Auto-save summaries

4. **search_conversations**: Semantic conversation search
   - Find relevant past discussions
   - Context-aware search
   - Build on previous conversations
   - Cross-session discovery

#### Memory-as-Human-Memory Design Principles

The memory system is designed to mirror human cognitive processes:

1. **Temporal Awareness**: Memories have timestamps and can be recalled by time period
2. **Importance Weighting**: Not all memories are equal - importance scores help prioritize
3. **Contextual Associations**: Memories are linked through people, places, topics, and emotions
4. **Reflection Capability**: The system can analyze its own memory patterns and generate insights
5. **Conversational Continuity**: Track and recall conversation history across sessions
6. **Dynamic Adaptation**: Memory importance can be updated based on usage and reflection

#### Example Memory Workflow

```python
# Store a memory with rich context
await store_memory(
    content="Learned about Python async/await patterns for concurrent programming",
    importance=8,
    topics=["python", "concurrency", "async"],
    source="reading",
    sentiment="positive"
)

# Recall recent memories about Python
recent_python = await recall_by_time(
    period="last_week",
    topics=["python"],
    min_importance=7
)

# Find all memories associated with a project
project_memories = await find_associations(
    topics=["project_alpha"],
    people=["Alice", "Bob"],
    min_importance=6
)

# Reflect on learning patterns
insights = await reflect_on_memories(
    aspect="all",
    time_period="last_month"
)

# Store conversation for continuity
await store_conversation_turn(
    user_message="How do I implement async patterns in Python?",
    assistant_response="To implement async patterns in Python...",
    session_id="learning_session_1",
    topics=["python", "async"],
    importance=7
)

# Recall conversation history
history = await recall_conversation_history(
    session_id="learning_session_1",
    limit=10
)

# Generate session summary
summary = await summarize_conversation_session(
    session_id="learning_session_1",
    save_summary=True
)
```

### Incremental Learning Tools ("On the Go" Learning) (New!)

The MCP server now includes powerful **incremental learning** capabilities that enable continuous knowledge acquisition and progressive refinement - essential for on-the-go learning.

#### Incremental Learning Tools

1. **quick_capture**: Rapidly capture learning moments without interruption
   - Capture fleeting thoughts during active learning
   - Record "aha moments" on the fly
   - Note questions that arise during study
   - Mark items for later expansion
   - Build knowledge incrementally

2. **expand_learning**: Transform quick captures into full memories
   - Add depth and context to captured ideas
   - Connect to related knowledge
   - Assign importance and categorization
   - Extract key insights
   - Progressive knowledge building

3. **reinforce_learning**: Strengthen knowledge through repetition
   - Track usage and application of knowledge
   - Implement spaced repetition principles
   - Boost importance based on reinforcement
   - Measure mastery progression
   - Build long-term retention

4. **track_learning_progress**: Monitor and analyze learning journey
   - Identify quick captures needing expansion
   - Track learnings requiring reinforcement
   - Measure learning streaks and momentum
   - Discover active focus areas
   - Get personalized recommendations

5. **create_learning_path**: Build adaptive learning roadmaps
   - Define learning goals and milestones
   - Identify knowledge gaps
   - Suggest prerequisite topics
   - Create structured learning phases
   - Adapt to current knowledge level

#### Incremental Learning Workflow

```python
# On the go: Quick capture during active learning
capture = await quick_capture(
    content="Event loop processes async tasks in Python - need to understand how",
    context="reading async documentation",
    tags=["python", "async", "todo"],
    expand_later=True
)

# Later: Expand with full understanding
expanded = await expand_learning(
    capture_id=capture["capture_id"],
    expanded_content="Python's event loop is the core of async programming. It manages and executes async tasks, handling I/O operations without blocking...",
    importance=8,
    topics=["python", "async", "event-loop"],
    key_insight="Event loop enables concurrent I/O without threads"
)

# Apply knowledge in practice
reinforced = await reinforce_learning(
    learning_id=expanded["expanded_id"],
    usage_context="Built async web scraper using asyncio",
    mastery_level=7
)

# Track progress
progress = await track_learning_progress(
    time_period="last_week"
)
# Returns: pending captures, reinforcement needs, learning streak, recommendations

# Plan next steps
learning_path = await create_learning_path(
    goal="master async programming in Python",
    current_level="intermediate",
    related_topics=["event-loop", "coroutines"]
)
```

#### Benefits of Incremental Learning

- **Capture Without Interruption**: Quickly save insights while staying focused
- **Progressive Refinement**: Build knowledge incrementally over time
- **Spaced Repetition**: Strengthen retention through tracked reinforcement
- **Learning Momentum**: Track streaks and maintain motivation
- **Adaptive Paths**: Personalized learning based on your current knowledge
- **Knowledge Gaps**: Identify what needs more attention
- **Mastery Tracking**: Measure progression from beginner to expert
- **On-the-Go Learning**: Perfect for continuous, real-world learning

#### Benefits of Human-like Memory

- **Temporal Awareness**: Know when information was learned or discussed
- **Priority Management**: Focus on important memories while retaining others
- **Contextual Recall**: Find information through multiple association paths
- **Self-Reflection**: Understand patterns in learning and interaction
- **Conversational Continuity**: Maintain context across sessions and conversations
- **Adaptive Learning**: Memory importance evolves based on usage and reflection
- **Emotional Context**: Track sentiment and emotional associations
- **Relationship Tracking**: Associate memories with people, places, and events

### Causal Boosting Mechanism

The MCP server includes a sophisticated causal boosting mechanism that enhances search relevance by identifying and prioritizing causal relationships:

- **Pattern Recognition**: Detects causal language patterns in both queries and documents
- **Multilingual Support**: Automatically applies appropriate patterns based on detected query language
- **Configurable Boost Multipliers**: Different types of causal matches receive customizable boost factors
- **Enhanced Relevance**: Results that explain causal relationships are prioritized in search results

This mechanism significantly improves responses to "why" and "how" questions by surfacing content that explains relationships between concepts. The causal boosting configuration is highly customizable through YAML files, allowing adaptation to different domains and languages.


## License

MIT License - see LICENSE file for details




