from src.config.settings import settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.languagemodels.llmprovider import get_llm_instance
from src.rag.schema_retrival import get_relevant_schemas
from src.graph.state.agentstate import AgentState


def generate_sql_from_question(state: AgentState) -> AgentState:
    """Generates SQL query from a natural language question using RAG approach."""
    # Step A: Retrieve target schemas from vector DB
    question = state.user_query 
    context = get_relevant_schemas(question, num_tables=4)
    sql_generation_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert SQL engineer. Your task is to generate valid SQL statements "
        "based ONLY on the provided database table schemas and a natural language query.\n\n"
        "### RULES:\n"
        "1. Return ONLY the raw SQL code. Do not wrap it in markdown code blocks like ```sql.\n"
        "2. Only use the tables and columns explicitly defined in the context below.\n"
        "3. Pay close attention to PRIMARY KEY and FOREIGN KEY notes to perform accurate joins.\n\n"
        "### DATABASE SCHEMA CONTEXT:\n{schema_context}"
    )),
    ("human", "Natural Language Query: {user_query}\n\nGenerated SQL:")
    ])

    print(f"Retrieved schema context for question '{question}':\n{context}")
    if not context.strip():
        return state
    
    llm = get_llm_instance(settings.GROQ_LLM_PROVIDER)  # Use the configured LLM provider
    sql_chain = sql_generation_prompt | llm | StrOutputParser()
    
        # Step B: Pass question and schemas to LLM to create SQL
    sql_query = sql_chain.invoke({
        "schema_context": context,
        "user_query": question
    })
    print(f"Generated SQL query for question '{question}':\n{sql_query}")
        
    state.generated_sql = sql_query
    return state