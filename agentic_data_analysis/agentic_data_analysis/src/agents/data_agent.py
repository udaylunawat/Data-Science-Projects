import os
from google.adk import Agent
from google.adk.tools import ToolContext
from src.utils.data_loader import DataLoader
import pandas as pd

async def load_data_tool(file_path: str, tool_context: ToolContext):
    """Tool to load data from CSV/Excel files"""
    loader = DataLoader()
    try:
        df = loader.load_data(file_path)
        tool_context.state['data'] = df  # Store DataFrame in state
        # Return a serializable summary
        return {
            "message": f"Data loaded successfully from {file_path}",
            "shape": str(df.shape),  # Convert to string
            "columns": list(df.columns),
            "head": df.head().to_dict(orient='records')  # Convert to dict
        }
    except Exception as e:
        return {"error": str(e)}

async def analyze_data_tool(query: str, tool_context: ToolContext):
    """Tool to analyze data based on natural language queries"""
    df = tool_context.state.get('data')
    if df is None:
        return "No data loaded. Please load data first."

    try:
        # Basic analysis based on query
        if 'average' in query.lower() or 'mean' in query.lower():
            group_cols = []
            if 'gender' in query.lower():
                group_cols.append('Gender')
            if 'job' in query.lower() or 'classification' in query.lower():
                group_cols.append('Job Classification')

            if group_cols:
                result = df.groupby(group_cols)['Balance'].mean()
                # Convert result to serializable format
                result_dict = result.to_dict()
                return {"analysis_result": result_dict}
            else:
                return "Could not find appropriate columns for analysis."
        else:
            return "Could not understand the analysis request"
    except Exception as e:
        return {"error": str(e)}

# Define the root agent
root_agent = Agent(
    name="data_analysis_assistant",
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    instruction="""You are a data analysis assistant that can:
    1. Load data from CSV and Excel files
    2. Perform statistical analysis
    3. Generate visualizations

    When handling requests:
    1. First check if data needs to be loaded
    2. Then understand the analysis requirements
    3. Use appropriate tools to perform the analysis
    4. Present results clearly""",
    tools=[load_data_tool, analyze_data_tool]
)