import json
import operator
import uuid
from typing import Annotated, Optional

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from app.tools import (
    log_interaction_tool,
    edit_interaction_tool,
    search_hcp_tool,
    suggest_next_steps_tool,
    validate_interaction_tool,
)


class AgentState(TypedDict):
    messages: list
    interaction: dict
    conversation_id: str
    last_tool_called: str
    tool_result: Optional[dict]


_conversations: dict[str, AgentState] = {}


_HCP_KEYWORDS = ["dr.", "doctor", "met with", "called", "meeting", "interaction",
                   "discussed", "hcp", "patient", "clinic", "hospital", "specialist",
                   "sent an email", "pharmaceutical", "product", "treatment", "prescribe"]

def _detect_intent(user_message: str) -> str:
    msg = user_message.lower()
    if any(kw in msg for kw in ["edit", "update", "change", "correct", "fix", "modify", "revise", "adjust"]):
        return "edit"
    if any(kw in msg for kw in ["search", "find", "look up", "who is", "show me", "list"]):
        return "search"
    if any(kw in msg for kw in ["suggest", "next step", "recommend", "what should", "follow up", "strategy"]):
        return "suggest"
    if any(kw in msg for kw in ["validate", "check", "verify", "review", "complete", "missing"]):
        return "validate"
    if any(kw in msg for kw in _HCP_KEYWORDS):
        return "log"
    return "general"


def _build_tool_response(tool_name: str, result: dict) -> str:
    if tool_name == "log_interaction":
        name = result.get("hcp_name", "Unknown")
        return f"I've logged the interaction with **{name}**.\n\n{_summarize_interaction(result)}"
    elif tool_name == "edit_interaction":
        return f"I've updated the interaction record.\n\n{_summarize_interaction(result)}"
    elif tool_name == "search_hcp":
        results = result.get("results", [])
        if not results:
            return "No HCPs found matching your search criteria."
        lines = [f"Found {len(results)} HCP(s):"]
        for h in results:
            lines.append(f"• **{h['name']}** — {h['specialty']}, {h['region']} (Last: {h.get('last_interaction', 'N/A')})")
        return "\n".join(lines)
    elif tool_name == "suggest_next_steps":
        suggestions = result.get("suggestions", [])
        if not suggestions:
            return "I need more interaction data to suggest next steps. Please log an interaction first."
        lines = ["Here are your recommended next steps:"]
        for s in suggestions:
            badge = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(s.get("priority", ""), "⚪")
            lines.append(f"{badge} **{s['suggestion']}** — _{s.get('timeframe', '')}_")
        return "\n".join(lines)
    elif tool_name == "validate":
        if result.get("is_valid"):
            parts = ["✅ Your interaction record looks complete and valid!"]
            if result.get("suggestions"):
                parts.append("Tips: " + "; ".join(result["suggestions"]))
            return "\n".join(parts)
        missing = result.get("missing_fields", [])
        parts = ["⚠️ The interaction record needs attention:"]
        if missing:
            parts.append(f"Missing or incomplete: {', '.join(missing)}")
        if result.get("suggestions"):
            parts.append("Suggestions: " + "; ".join(result["suggestions"]))
        return "\n".join(parts)
    return json.dumps(result, indent=2)


def _summarize_interaction(interaction: dict) -> str:
    parts = []
    if interaction.get("interaction_type"):
        parts.append(f"• Type: {interaction['interaction_type']}")
    if interaction.get("interaction_date"):
        parts.append(f"• Date: {interaction['interaction_date']}")
    if interaction.get("sentiment"):
        parts.append(f"• Sentiment: {interaction['sentiment']}")
    if interaction.get("key_discussion_points"):
        p = interaction["key_discussion_points"][:120]
        parts.append(f"• Discussion: {p}{'...' if len(interaction['key_discussion_points']) > 120 else ''}")
    if interaction.get("action_items"):
        p = interaction["action_items"][:100]
        parts.append(f"• Action: {p}{'...' if len(interaction['action_items']) > 100 else ''}")
    return "\n".join(parts)


def parse_and_route(state: AgentState) -> AgentState:
    return state


def router(state: AgentState) -> str:
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""
    return _detect_intent(last_msg)


def execute_log_interaction(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""
    result = log_interaction_tool(last_msg, state.get("interaction"))
    state["interaction"] = result
    state["last_tool_called"] = "log_interaction"
    state["tool_result"] = result
    return state


def execute_edit_interaction(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""
    result = edit_interaction_tool(last_msg, state.get("interaction", {}))
    state["interaction"] = result
    state["last_tool_called"] = "edit_interaction"
    state["tool_result"] = result
    return state


def execute_search_hcp(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""
    result = search_hcp_tool(last_msg)
    state["last_tool_called"] = "search_hcp"
    state["tool_result"] = result
    return state


def execute_suggest_next_steps(state: AgentState) -> AgentState:
    result = suggest_next_steps_tool(state.get("interaction", {}))
    state["last_tool_called"] = "suggest_next_steps"
    state["tool_result"] = result
    return state


def execute_validate(state: AgentState) -> AgentState:
    result = validate_interaction_tool(state.get("interaction", {}))
    state["last_tool_called"] = "validate"
    state["tool_result"] = result
    return state


def execute_general(state: AgentState) -> AgentState:
    has_data = state.get("interaction", {}) and any(v for v in state["interaction"].values())
    state["last_tool_called"] = "general"
    state["tool_result"] = {"has_interaction_data": has_data}
    return state


def generate_response(state: AgentState) -> AgentState:
    tool_name = state.get("last_tool_called", "log_interaction")
    tool_result = state.get("tool_result", {})

    if tool_name == "general":
        has_data = tool_result.get("has_interaction_data", False)
        if has_data:
            reply = (
                "I've already captured the interaction data in the form. Here's what you can do next:\n\n"
                "• **Edit** — say \"Edit the sentiment to Positive\"\n"
                "• **Search** — say \"Search for cardiologists in New York\"\n"
                "• **Suggest** — say \"Suggest next steps\"\n"
                "• **Validate** — say \"Validate the record\"\n\n"
                "Or tell me about a new HCP interaction to log."
            )
        else:
            reply = (
                "Hi! I'm your AI assistant for logging HCP interactions. "
                "Tell me about your interaction with a Healthcare Professional, and I'll populate the form automatically.\n\n"
                "You can also:\n"
                "• **Search** for HCPs: \"Search for cardiologists in San Francisco\"\n"
                "• Ask me to **suggest** next steps after logging\n"
                "• Ask me to **validate** or **edit** the record"
            )
    else:
        reply = _build_tool_response(tool_name, tool_result)

    state["messages"].append({"role": "assistant", "content": reply})
    return state


# ─── Graph Construction ───────────────────────────────────────────────

def build_agent() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("parse_and_route", parse_and_route)
    workflow.add_node("log_interaction", execute_log_interaction)
    workflow.add_node("edit_interaction", execute_edit_interaction)
    workflow.add_node("search_hcp", execute_search_hcp)
    workflow.add_node("suggest_next_steps", execute_suggest_next_steps)
    workflow.add_node("validate", execute_validate)
    workflow.add_node("general", execute_general)
    workflow.add_node("generate_response", generate_response)

    workflow.set_entry_point("parse_and_route")

    workflow.add_conditional_edges(
        "parse_and_route",
        router,
        {
            "log": "log_interaction",
            "edit": "edit_interaction",
            "search": "search_hcp",
            "suggest": "suggest_next_steps",
            "validate": "validate",
            "general": "general",
        },
    )

    workflow.add_edge("log_interaction", "generate_response")
    workflow.add_edge("edit_interaction", "generate_response")
    workflow.add_edge("search_hcp", "generate_response")
    workflow.add_edge("suggest_next_steps", "generate_response")
    workflow.add_edge("validate", "generate_response")
    workflow.add_edge("general", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()


agent_app = build_agent()


def process_message(message: str, conversation_id: Optional[str] = None) -> tuple[str, dict, str]:
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    # Resume conversation state if it exists
    prev = _conversations.get(conversation_id)
    prev_interaction = prev.get("interaction", {}) if prev else {}

    initial_state: AgentState = {
        "messages": [{"role": "user", "content": message}],
        "interaction": dict(prev_interaction),
        "conversation_id": conversation_id,
        "last_tool_called": "",
        "tool_result": None,
    }

    final_state = agent_app.invoke(initial_state)

    # Persist conversation state
    _conversations[conversation_id] = final_state

    reply = ""
    for msg in reversed(final_state.get("messages", [])):
        if msg.get("role") == "assistant" and msg.get("content"):
            reply = msg["content"]
            break

    interaction = final_state.get("interaction", {})

    return reply, interaction, conversation_id
