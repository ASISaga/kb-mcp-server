"""
Tests for memory and conversation tools.
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest


class TestMemoryTools:
    """Test memory-focused tools."""

    def test_imports(self):
        """Test that new modules can be imported."""
        from txtai_mcp_server.tools.conversation import register_conversation_tools
        from txtai_mcp_server.tools.memory import register_memory_tools

        assert callable(register_memory_tools)
        assert callable(register_conversation_tools)

    def test_graph_tools_import(self):
        """Test that graph tools can be imported."""
        from txtai_mcp_server.tools.graph import register_graph_tools

        assert callable(register_graph_tools)


class TestServerIntegration:
    """Test that all tools are properly registered in the server."""

    def test_server_imports(self):
        """Test that server can import all tool registrations."""
        from txtai_mcp_server.server import create_server

        assert callable(create_server)

    def test_server_creation(self):
        """Test that server can be created with all tools."""
        from txtai_mcp_server.server import create_server

        # Create server instance (without starting it)
        server = create_server()

        # Verify it's a valid server instance
        assert server is not None
        assert hasattr(server, "name")
        assert server.name == "Knowledgebase Server"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
