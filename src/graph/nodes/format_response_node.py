from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from src.config.settings import settings
from src.languagemodels.llmprovider import get_llm_instance
from src.graph.state.agentstate import AgentState

def format_response(state:AgentState) -> AgentState:
    """Uses an LLM to transform raw SQLite results into a natural, user-friendly response."""
    user_query = state.user_query
    dbresult = state.db_query_result
    if(state.sql_error):
        state.final_output = state.sql_error
        return state
    llm = get_llm_instance(settings.GROQ_LLM_PROVIDER)  # Use the configured LLM provider
    system_instruction = (
        "You are a helpful data assistant. Your job is to format the provided data to the user's question "
        "using ONLY the provided database results. \n"
        "Follow these rules:\n"
        "- Summarize the data into natural, human conversational language.\n"
        "- Lead with the most important answer immediately.\n"
        "- Do not make up facts or columns not present in the data.\n"
        "- If the results list is long, use bold key-terms and clean markdown bullet points.\n"
        "- Treat missing data or 'None' values as 'not available'."
    )
    print(f"Generating LLM response for user query: '{user_query}' with database results: {dbresult}")

    user_prompt = f"""
User Question: "{user_query}"

Database Query Results:
\"\"\"
{dbresult}
\"\"\"

Please provide a clean, direct answer to the user based on the database results above.
"""
    print(f"User prompt for LLM:\n{user_prompt}")

    try:
        response = llm.invoke(
            [
                SystemMessage(content=system_instruction),
                HumanMessage(content=user_prompt),
            ]
        )

        print(f"LLM response content: {response.content}")

        state.final_output = response.content
        return state

    except Exception as e:
        state.final_output = f"🚨 Error generating LLM response: {e}"
        return state