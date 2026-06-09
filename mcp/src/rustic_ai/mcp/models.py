from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from rustic_ai.core.guild.dsl import BaseAgentProps
from rustic_ai.core.utils.basic_class_utils import get_class_from_name


class MCPClientType(str, Enum):
    STDIO = "stdio"
    HTTP = "http"


class MCPServerConfig(BaseModel):
    type: MCPClientType = Field(default=MCPClientType.STDIO, description="Type of connection")

    # Stdio config
    command: Optional[str] = Field(None, description="Command to execute for stdio")
    args: List[str] = Field(default_factory=list, description="Arguments for the command")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")

    # HTTP config
    url: Optional[HttpUrl] = Field(None, description="URL for HTTP connection")
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional Non-Authorization headers")
    auth_header: Optional[str] = Field("Authorization", description="Authorization header")

    @model_validator(mode="after")
    def _require_transport_fields(self) -> "MCPServerConfig":
        if self.type == MCPClientType.STDIO and not self.command:
            raise ValueError("'command' is required when type is STDIO")
        if self.type == MCPClientType.HTTP and not self.url:
            raise ValueError("'url' is required when type is HTTP")
        return self


class MCPAgentConfig(BaseAgentProps):
    server: MCPServerConfig = Field(description="MCP server configuration")


class CallToolRequest(BaseModel):
    tool_name: str
    arguments: Dict = Field(default_factory=dict)


class ToolResult(BaseModel):
    type: Literal["text", "image", "resource"]
    content: Union[str, Dict]


class CallToolResponse(BaseModel):
    results: List[ToolResult]
    is_error: bool = False
    error: Optional[str] = None


class MCPToolDeclaration(BaseModel):
    """
    Declaration of a single MCP tool exposed by a ``BoundMCPAgent``.

    ``input_class_name`` must reference an importable pydantic ``BaseModel``
    subclass whose fields define the validated argument schema for the tool.
    """

    name: str = Field(min_length=1, description="Tool name as exposed by the MCP server")
    input_class_name: str = Field(
        min_length=1,
        description="Qualified class name of a pydantic BaseModel defining the tool's arguments schema",
    )
    description: Optional[str] = Field(None, description="Human/LLM-facing description of the tool")

    @field_validator("input_class_name")
    @classmethod
    def _validate_args_class(cls, v: str) -> str:
        try:
            resolved = get_class_from_name(v)
        except Exception as e:
            raise ValueError(f"Cannot resolve input_class_name '{v}': {e}")
        if not (isinstance(resolved, type) and issubclass(resolved, BaseModel)):
            raise ValueError(f"input_class_name '{v}' must reference a pydantic BaseModel subclass")
        return v


class BoundMCPAgentConfig(BaseAgentProps):
    """
    Config for ``BoundMCPAgent``: one MCP server plus a non-empty, deduplicated
    list of tool declarations forming the agent's allowlist.
    """

    server: MCPServerConfig = Field(description="MCP server configuration")
    tools: List[MCPToolDeclaration] = Field(min_length=1, description="Declared tool allowlist")
