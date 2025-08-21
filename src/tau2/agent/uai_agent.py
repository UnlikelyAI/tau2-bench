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

    session_id: str | None
    system_messages: list[SystemMessage]
    messages: list[APICompatibleMessage]


class UAIAgentRequest(BaseModel):
    """
    UAI agent request
    """

    session_id: str | None
    messages: list[APICompatibleMessage]
    tools: list[dict[str, Any]]


class UAIAgentResponse(BaseModel):
    """
    UAI agent response
    """

    session_id: str
    message_content: str
    tool_calls: list[dict[str, Any]]


AGENT_INSTRUCTION = """
You are a customer service agent that helps the user according to the <policy> provided below.
In each turn you can either:
- Send a message to the user.
- Make a tool call.
You cannot do both at the same time.

Try to be helpful and always follow the policy. Always make sure you generate valid JSON only.
""".strip()

SYSTEM_PROMPT = """
<instructions>
{agent_instruction}
</instructions>
<policy>
{domain_policy}
</policy>
""".strip()


class UAIAgent(LocalAgent[UAIAgentState]):
    """
    UAI agent implementation
    """

    def __init__(self, tools: list[Tool], domain_policy: str):
        super().__init__(tools, domain_policy)

        self.client = Client(
            base_url="http://localhost:8026/api/v1",
            timeout=30.0,
        )

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT.format(
            domain_policy=self.domain_policy, agent_instruction=AGENT_INSTRUCTION
        )

    def generate_next_message(
        self, message: ValidAgentInputMessage, state: UAIAgentState
    ) -> tuple[AssistantMessage, UAIAgentState]:
        if isinstance(message, MultiToolMessage):
            state.messages.extend(message.tool_messages)
        else:
            state.messages.append(message)

        messages = state.system_messages + state.messages

        request = UAIAgentRequest(
            session_id=state.session_id,
            messages=messages,
            tools=[t.openai_schema for t in self.tools],
        )

        import asyncio

        async def _make_request():
            return self.client.post(
                "/benchmarks/tau/process_message", json=request.model_dump()
            )

        response = asyncio.run(_make_request())

        if response.status_code != 200:
            raise Exception(f"Failed to generate next message: {response.text}")

        response_data = UAIAgentResponse.model_validate(response.json())

        tool_calls = (
            [ToolCall.model_validate(tool) for tool in response_data.tool_calls]
            if len(response_data.tool_calls) > 0
            else None
        )

        assistant_message = AssistantMessage(
            role="assistant",
            content=(
                response_data.message_content if response_data.message_content else None
            ),
            tool_calls=tool_calls,
        )

        if response_data.session_id is None:
            raise Exception("Session ID is None")

        state.session_id = response_data.session_id
        state.messages.append(assistant_message)

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
            session_id=None,
            system_messages=[SystemMessage(role="system", content=self.system_prompt)],
            messages=message_history,
        )
