import os
import pandas as pd
from google.adk import Agent
from google.adk.tools import ToolContext
import pandasql as psql
from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Hardcoded path to CSV
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", "P1-UK-Bank-Customers.csv")

artifact_service = InMemoryArtifactService()
session_service = InMemorySessionService()

# --- Data Loader Function ---
def _is_csv_content(s: str) -> bool:
    return isinstance(s, str) and '\n' in s and ',' in s and not os.path.exists(s)

def _load_dataframe(file_path_or_content):
    # If a DataFrame, return as is.
    if isinstance(file_path_or_content, pd.DataFrame):
        return file_path_or_content
    if _is_csv_content(file_path_or_content):
        from io import StringIO
        return pd.read_csv(StringIO(file_path_or_content))
    if not os.path.exists(file_path_or_content):
        raise FileNotFoundError(f"File not found: {file_path_or_content}")
    ext = os.path.splitext(file_path_or_content)[-1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path_or_content)
    elif ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path_or_content)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

# --- Tool: Execute SQL ---
async def execute_sql_tool(query: str, tool_context: ToolContext):
    # Retrieve preloaded data from the tool context state
    data = tool_context.state.get('data')
    if not data:
        return {"status": "error", "message": "No data loaded. Preload the data first."}
    try:
        # Create a DataFrame from the preloaded data
        df = pd.DataFrame(data)
        # If the user is asking for table info, return column details directly
        if query.strip().upper().startswith("PRAGMA TABLE_INFO"):
            # Create a synthetic result with common PRAGMA table_info columns:
            # cid, name, type, notnull, dflt_value, pk.
            result = []
            for i, col in enumerate(df.columns):
                result.append({
                    "cid": i,
                    "name": col,
                    "type": str(df[col].dtype),
                    "notnull": int(not df[col].isnull().all()),
                    "dflt_value": None,
                    "pk": 0
                })
            return {
                "status": "success",
                "query_result": {
                    "data": result,
                    "shape": [len(result), 6],
                    "sql_query": query
                }
            }
        # Otherwise execute the SQL query normally
        result = psql.sqldf(query, {"data": df})
        return {
            "status": "success",
            "query_result": {
                "data": result.to_dict('records'),
                "shape": list(result.shape),
                "sql_query": query
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"SQL Error: {str(e)}"}

# --- Preload Data ---
async def preload_data_tool(tool_context: ToolContext):
    try:
        # Load CSV data into a DataFrame
        df = _load_dataframe(CSV_FILE_PATH)
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
        # Store the data directly in the tool context state (without nesting)
        tool_context.state["data"] = df.to_dict('records')
        print(f"Preloaded data: {df.shape[0]} records, columns: {list(df.columns)}")
        return {"status": "success", "message": "Data preloaded successfully."}
    except Exception as e:
        return {"status": "error", "message": f"Error preloading data: {str(e)}"}


# --- Agent Configuration ---
# SQL Executor Agent: Assumes data is already loaded
root_agent = Agent(
    name="sql_executor_agent",
    model="gemini-2.0-flash",
    instruction="""
You are an expert SQL executor.
The dataset is already loaded into memory.
Your task is to generate and execute clean and executable SQL queries on the dataset based on user request. Table name is data
""",
    tools=[execute_sql_tool, preload_data_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=3000
    )
)

# --- Runner ---
runner = Runner(
    agent=root_agent,
    app_name="agentic_data_analysis",
    session_service=session_service,
    artifact_service=artifact_service
)