from unittest.mock import AsyncMock

from pydantic import ValidationError
import pytest
from rustic_ai.testing.helpers import wrap_agent_for_testing

from rustic_ai.core.guild.builders import AgentBuilder
from rustic_ai.core.guild.dsl import GuildTopics
from rustic_ai.core.messaging.core.message import AgentTag, Message
from rustic_ai.core.utils.basic_class_utils import get_qualified_class_name
from rustic_ai.core.utils.gemstone_id import GemstoneGenerator
from rustic_ai.core.utils.priority import Priority
from rustic_ai.mcp.bound_agent import BoundMCPAgent
from rustic_ai.mcp.client import MCPClient
from rustic_ai.mcp.connectors.godaddy import (
    DomainsCheckAvailabilityInput,
    DomainsSuggestInput,
)
from rustic_ai.mcp.models import (
    BoundMCPAgentConfig,
    CallToolRequest,
    CallToolResponse,
    MCPClientType,
    MCPServerConfig,
    MCPToolDeclaration,
    ToolResult,
)


def _server() -> MCPServerConfig:
    return MCPServerConfig(type=MCPClientType.HTTP, url="https://api.godaddy.com/v1/domains/mcp")


def _suggest_decl() -> MCPToolDeclaration:
    return MCPToolDeclaration(name="domains_suggest", input_class_name=get_qualified_class_name(DomainsSuggestInput))


def _check_decl() -> MCPToolDeclaration:
    return MCPToolDeclaration(
        name="domains_check_availability",
        input_class_name=get_qualified_class_name(DomainsCheckAvailabilityInput),
    )


@pytest.fixture
def generator() -> GemstoneGenerator:
    return GemstoneGenerator(1)


def _build_msg(generator: GemstoneGenerator, payload: CallToolRequest) -> Message:
    return Message(
        id_obj=generator.get_id(Priority.NORMAL),
        sender=AgentTag(name="test", id="t-1"),
        topics=GuildTopics.DEFAULT_TOPICS,
        payload=payload.model_dump(),
        format=get_qualified_class_name(CallToolRequest),
    )


def _build_agent(call_tool_response: CallToolResponse | None = None):
    config = BoundMCPAgentConfig(
        server=_server(),
        tools=[_suggest_decl(), _check_decl()],
    )
    spec = (
        AgentBuilder(BoundMCPAgent)
        .set_id("bound_mcp_agent")
        .set_name("Bound MCP Agent")
        .set_description("test")
        .set_properties(config)
        .build_spec()
    )
    agent, results = wrap_agent_for_testing(spec)

    mock_client = AsyncMock(spec=MCPClient)
    mock_client.call_tool.return_value = call_tool_response or CallToolResponse(
        results=[ToolResult(type="text", content="ok")]
    )
    agent._mcp_client = mock_client
    return agent, results, mock_client


class TestBoundMCPAgentConfig:
    """Pydantic config validation tests — no agent instantiation."""

    def test_rejects_empty_tools(self):
        with pytest.raises(ValidationError):
            BoundMCPAgentConfig(server=_server(), tools=[])

    def test_rejects_unimportable_args_class(self):
        with pytest.raises(ValidationError, match="Cannot resolve"):
            MCPToolDeclaration(name="x", input_class_name="not.a.real.module.Class")

    def test_rejects_non_basemodel_args_class(self):
        with pytest.raises(ValidationError, match="BaseModel"):
            MCPToolDeclaration(name="x", input_class_name="builtins.str")


class TestBoundMCPAgentDispatch:
    """End-to-end dispatch with a mocked MCP client."""

    def test_happy_path(self, generator):
        agent, results, mock_client = _build_agent()
        msg = _build_msg(
            generator,
            CallToolRequest(tool_name="domains_suggest", arguments={"query": "tech startup"}),
        )
        agent._on_message(msg)

        assert mock_client.call_tool.await_count == 1
        forwarded = mock_client.call_tool.await_args.args[0]
        assert isinstance(forwarded, CallToolRequest)
        assert forwarded.tool_name == "domains_suggest"
        # Default 'limit=40' should be filled in by validation before forwarding.
        assert forwarded.arguments == {"query": "tech startup", "limit": 40}
        assert len(results) == 1
        assert results[0].format == get_qualified_class_name(CallToolResponse)
        assert results[0].payload["results"][0]["content"] == "ok"

    def test_tool_not_in_allowlist(self, generator):
        agent, results, mock_client = _build_agent()
        msg = _build_msg(
            generator,
            CallToolRequest(tool_name="not_declared", arguments={}),
        )
        agent._on_message(msg)

        assert mock_client.call_tool.await_count == 0
        assert len(results) == 1
        err = results[0].payload
        assert err["error_type"] == "ToolNotAllowed"
        # Error message should enumerate the allowed tools so the caller can recover.
        assert "domains_suggest" in err["error_message"]
        assert "domains_check_availability" in err["error_message"]

    def test_invalid_arguments_missing_required(self, generator):
        agent, results, mock_client = _build_agent()
        msg = _build_msg(
            generator,
            CallToolRequest(tool_name="domains_suggest", arguments={}),
        )
        agent._on_message(msg)

        assert mock_client.call_tool.await_count == 0
        assert len(results) == 1
        assert results[0].payload["error_type"] == "InvalidToolArguments"

    def test_invalid_arguments_wrong_type(self, generator):
        agent, results, mock_client = _build_agent()
        msg = _build_msg(
            generator,
            CallToolRequest(
                tool_name="domains_suggest",
                arguments={"query": "tech startup", "limit": "not_an_int"},
            ),
        )
        agent._on_message(msg)

        assert mock_client.call_tool.await_count == 0
        assert len(results) == 1
        assert results[0].payload["error_type"] == "InvalidToolArguments"

    def test_extra_fields_rejected(self, generator):
        agent, results, mock_client = _build_agent()
        msg = _build_msg(
            generator,
            CallToolRequest(
                tool_name="domains_suggest",
                arguments={"query": "tech startup", "bogus": "field"},
            ),
        )
        agent._on_message(msg)

        assert mock_client.call_tool.await_count == 0
        assert len(results) == 1
        err = results[0].payload
        assert err["error_type"] == "InvalidToolArguments"
        assert "bogus" in err["error_message"]

    def test_client_returned_error_is_propagated(self, generator):
        agent, results, mock_client = _build_agent(
            call_tool_response=CallToolResponse(results=[], is_error=True, error="upstream failed")
        )
        msg = _build_msg(
            generator,
            CallToolRequest(tool_name="domains_suggest", arguments={"query": "tech startup"}),
        )
        agent._on_message(msg)

        assert mock_client.call_tool.await_count == 1
        assert len(results) == 1
        err = results[0].payload
        assert err["error_type"] == "ErrorProcessingMCPRequest"
        assert "upstream failed" in err["error_message"]
