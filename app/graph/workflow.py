from langgraph.graph import StateGraph, START, END
from app.graph.state import ArchivistState
from app.graph.nodes.context import extract_context
from app.graph.nodes.knowledge import fetch_knowledge
from app.graph.nodes.evaluation import evaluate_code
from app.graph.nodes.handoff import handoff_to_github
from app.graph.nodes.metadata import match_metadata


def scoring_gate(state: ArchivistState):

    score = state.get("metadata_score", 0)
    if score >= 5:
        print(" => Relevance high. Routing to Deep Path.")
        return "deep_path"
    
    print(" => Low relevance. Bypassing AI evaluation.")
    return "end"

def should_handoff(state: ArchivistState):

    if state.get("violation_found"):
        return "handoff"
    return "end"

workflow = StateGraph(ArchivistState)

workflow.add_node("metadata_agent", match_metadata)
workflow.add_node("context_agent", extract_context)
workflow.add_node("knowledge_agent", fetch_knowledge)
workflow.add_node("evaluation_agent", evaluate_code)
workflow.add_node("handoff_agent", handoff_to_github)

workflow.add_edge(START, "metadata_agent")

workflow.add_conditional_edges(
    "metadata_agent",
    scoring_gate,
    {
        "deep_path": "context_agent",
        "end": END
    }
)

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