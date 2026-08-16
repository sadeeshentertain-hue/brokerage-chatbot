
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    user_query: str
    chat_history: List[Dict[str, str]] = Field(default_factory=list)
    generated_sql: str = ""
    db_columns: list = []
    db_rows: list = []
    db_schema: Dict[str, Any] = {} 
    db_query_result: List = []
    sql_error: str = ""
    retry_count: int = 0
    final_output: str = ""