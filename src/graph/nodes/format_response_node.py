from langchain_core.messages import HumanMessage, SystemMessage

from src.config.settings import settings
from src.languagemodels.llmprovider import get_llm_instance
from src.graph.state.agentstate import AgentState


def format_response(state: AgentState) -> AgentState:
    """Uses an LLM to transform raw SQLite results into a natural, user-friendly response."""
    user_query = state.get("user_query", "")
    dbresult = state.get("db_query_result", [])

    if state.get("sql_error"):
        return {"final_output": state["sql_error"]}

    llm = get_llm_instance(settings.GROQ_LLM_PROVIDER)
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
        updated_history = list(state.get("chat_history", []))
        updated_history.append({"role": "user", "content": user_query})
        updated_history.append({"role": "assistant", "content": response.content})
        return {
            "final_output": response.content,
            "chat_history": updated_history,
        }

    except Exception as e:
        updated_history = list(state.get("chat_history", []))
        updated_history.append({"role": "user", "content": user_query})
        updated_history.append({"role": "assistant", "content": str(e)})
        return {
            "final_output": f"🚨 Error generating LLM response: {e}",
            "chat_history": updated_history,
        }