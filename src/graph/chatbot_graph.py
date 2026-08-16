from langgraph.graph import StateGraph, START, END

from src.graph.nodes.extract_data_node import run_sqlite_query
from src.graph.nodes.format_response_node import format_response
from src.graph.state.agentstate import AgentState
from src.graph.nodes.generate_sql_node import generate_sql_from_question

def create_and_compile_workflow() -> StateGraph:
    """Creates a workflow graph for the chatbot application."""
    workflow = StateGraph(AgentState)
    workflow.add_node("tool1_generate_sql", generate_sql_from_question)
    workflow.add_node("tool2_execute_sql", run_sqlite_query)   
    workflow.add_node("tool3_format_response", format_response)  
    workflow.add_edge(START, "tool1_generate_sql")
    workflow.add_edge("tool1_generate_sql", "tool2_execute_sql")
    workflow.add_edge("tool2_execute_sql", "tool3_format_response")
    workflow.add_edge("tool3_format_response", END)
    react_agent_app = workflow.compile()
    print("Workflow graph compiled successfully.")
    print(react_agent_app)
    return react_agent_app