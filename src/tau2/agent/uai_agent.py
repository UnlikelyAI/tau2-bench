from typing import Any, Optional
from httpx import Client
from pydantic import BaseModel

from tau2.agent.base import (
    LocalAgent,
    ValidAgentInputMessage,
    is_valid_agent_history_message,
)
from tau2.data_model.message import (
    APICompatibleMessage,
    AssistantMessage,
    Message,
    MultiToolMessage,
    SystemMessage,
    ToolCall,
)
from tau2.environment.tool import Tool


class UAIAgentState(BaseModel):
    """
    UAI agent state
    """

    system_messages: list[SystemMessage]
    messages: list[APICompatibleMessage]


class UAIAgentRequest(BaseModel):
    """
    UAI agent request
    """

    messages: list[APICompatibleMessage]
    tools: list[dict[str, Any]]


class UAIAgentResponse(BaseModel):
    """
    UAI agent response
    """

    message_content: str
    tool_calls: list[dict[str, Any]]


class UAIAgent(LocalAgent[UAIAgentState]):
    """
    UAI agent implementation
    """

    def __init__(self, tools: list[Tool], domain_policy: str):
        super().__init__(tools, domain_policy)

        self.client = Client(
            base_url="http://localhost:8026/api/v1",
        )

    async def generate_next_message(
        self, message: ValidAgentInputMessage, state: UAIAgentState
    ) -> tuple[AssistantMessage, UAIAgentState]:
        if isinstance(message, MultiToolMessage):
            state.messages.extend(message.tool_messages)
        else:
            state.messages.append(message)
        messages = state.system_messages + state.messages

        request = UAIAgentRequest(
            messages=messages,
            tools=[t.openai_schema for t in self.tools],
        )
        response = await self.client.post(
            "/benchmarks/tau/process_message", json=request.model_dump()
        )

        if response.status_code != 200:
            raise Exception(f"Failed to generate next message: {response.text}")

        response_data = UAIAgentResponse.model_validate_json(response.json())
        assistant_message = AssistantMessage(
            content=response_data.message_content,
            tool_calls=[
                ToolCall.model_validate(tool) for tool in response_data.tool_calls
            ],
        )

        return assistant_message, state

    def get_init_state(
        self, message_history: Optional[list[Message]] = None
    ) -> UAIAgentState:
        """Get the initial state of the agent.

        Args:
            message_history: The message history of the conversation.

        Returns:
            The initial state of the agent.
        """
        if message_history is None:
            message_history = []
        assert all(
            is_valid_agent_history_message(m) for m in message_history
        ), "Message history must contain only AssistantMessage, UserMessage, or ToolMessage to Agent."
        return UAIAgentState(
            system_messages=[SystemMessage(role="system", content=self.system_prompt)],
            messages=message_history,
        )
