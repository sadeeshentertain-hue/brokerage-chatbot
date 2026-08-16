from src.graph.state.agentstate import AgentState
from typing import Any, Dict, Literal

def should_retry_or_format(state: AgentState) -> Literal["tool1_generate_sql", "tool3_format_response", "fallback"]:
    """Determines whether to retry query compilation, output, or fail out."""
    if not state.sql_error:
        return "tool3_format_response" 
        
    if state.retry_count >= 3:
        return "fallback" 
        
    return "tool1_generate_sql" 

def fallback_failure_node(state: AgentState) -> AgentState:
    """Triggers if the system hits maximum retry limits without resolving syntax errors."""
    error_msg = "I encountered an issue processing your query directly against the store database. Please rephrase your query details."
    
    updated_history = list(state.chat_history)
    updated_history.append({"role": "user", "content": state.user_query})
    updated_history.append({"role": "assistant", "content": error_msg})
    state.chat_history = updated_history
    state.final_output = error_msg
    return state