from langgraph.graph import StateGraph, START, END
from app.graph.state import ArchivistState
from app.graph.nodes.context import extract_context
from app.graph.nodes.knowledge import fetch_knowledge
from app.graph.nodes.evaluation import evaluate_code
from app.graph.nodes.handoff import handoff_to_github

def should_handoff(state: ArchivistState):

    if state.get("violation_found"):
        return "handoff"
    return "end"

workflow = StateGraph(ArchivistState)

workflow.add_node("context_agent", extract_context)
workflow.add_node("knowledge_agent", fetch_knowledge)
workflow.add_node("evaluation_agent", evaluate_code)
workflow.add_node("handoff_agent", handoff_to_github)

workflow.add_edge(START, "context_agent")
workflow.add_edge("context_agent", "knowledge_agent")
workflow.add_edge("knowledge_agent", "evaluation_agent")

workflow.add_conditional_edges(
    "evaluation_agent",
    should_handoff,
    {
        "handoff": "handoff_agent",
        "end": END
    }
)

workflow.add_edge("handoff_agent", END)

archivist_app = workflow.compile()