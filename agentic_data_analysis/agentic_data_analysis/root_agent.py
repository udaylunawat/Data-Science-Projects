import os
from google.adk import Agent
from google.adk.tools import ToolContext
from .src.utils.data_loader import DataLoader  # Fixed import
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import plotly.io as pio
from datetime import datetime
import os
import base64
from io import BytesIO

async def load_data_tool(file_path: str, tool_context: ToolContext):
    """Tool to load data from CSV/Excel files"""
    loader = DataLoader()
    try:
        # Load the data and store in state
        df = loader.load_data(file_path)
        
        # Convert DataFrame to a serializable format before storing
        tool_context.state['data'] = df.to_dict('records')
        
        # Return only serializable metadata about the data
        return {
            "status": "success", 
            "message": f"Data loaded successfully from {file_path}",
            "metadata": {
                "shape": list(df.shape),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "sample_size": min(5, len(df)),
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": list(df.select_dtypes(include=['int64', 'float64']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
                "missing_values": {df.isnull().sum().to_dict()}
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def analyze_data_tool(query: str, tool_context: ToolContext):
    """Tool to analyze data based on natural language queries"""
    data = tool_context.state.get('data')
    if data is None:
        return {"status": "error", "message": "No data loaded. Please load data first."}

    try:
        # Convert back to DataFrame
        df = pd.DataFrame(data)
        # Get numeric columns for potential analysis
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        # Basic statistics for all numeric columns
        if 'summary' in query.lower() or 'statistics' in query.lower():
            stats = {}
            for col in numeric_cols:
                stats[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
            return {
                "status": "success",
                "analysis": {
                    "type": "summary_statistics",
                    "metrics": stats
                }
            }
            
        # Group by analysis
        elif any(word in query.lower() for word in ['average', 'mean', 'group']):
            # Find potential grouping columns (categorical)
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            group_cols = []
            
            # Find which categorical columns are mentioned in the query
            for col in categorical_cols:
                if col.lower() in query.lower():
                    group_cols.append(col)
                    
            # Find which numeric column to analyze
            target_col = None
            for col in numeric_cols:
                if col.lower() in query.lower():
                    target_col = col
                    break
            
            # If no specific numeric column mentioned, use the first one
            if not target_col and len(numeric_cols) > 0:
                target_col = numeric_cols[0]
                
            if group_cols and target_col:
                result = df.groupby(group_cols)[target_col].agg(['mean', 'count']).round(2)
                return {
                    "status": "success",
                    "analysis": {
                        "type": "grouped_statistics",
                        "groups": group_cols,
                        "target_column": target_col,
                        "values": result.to_dict(orient='index')
                    }
                }

        return {
            "status": "error",
            "message": "Could not understand the analysis request. Try asking for 'summary statistics' or 'average by [column]'"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def visualize_data_tool(query: str, tool_context: ToolContext):
    """Tool to create visualizations based on data analysis"""
    data = tool_context.state.get('data')
    if data is None:
        return {"status": "error", "message": "No data loaded. Please load data first."}
    
    try:
        df = pd.DataFrame(data)
        
        # Get column types
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category', 'datetime64']).columns
        
        # Determine chart type based on query and data types
        chart_type = None
        if 'histogram' in query.lower():
            chart_type = 'histogram'
        elif 'scatter' in query.lower():
            chart_type = 'scatter'
        elif 'line' in query.lower():
            chart_type = 'line'
        elif any(word in query.lower() for word in ['bar', 'column', 'distribution']):
            chart_type = 'bar'
        else:
            # Auto-select based on data types
            if len(numeric_cols) >= 2:
                chart_type = 'scatter'
            elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                chart_type = 'bar'
            else:
                chart_type = 'histogram'
        
        # Select columns based on query and chart type
        x_col = None
        y_col = None
        
        # Find columns mentioned in query
        mentioned_cols = [col for col in df.columns if col.lower() in query.lower()]
        
        if chart_type == 'histogram':
            # For histogram, prefer numeric column
            x_col = next((col for col in mentioned_cols if col in numeric_cols), 
                        numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0])
            
        elif chart_type == 'scatter':
            # Need two numeric columns
            numeric_mentioned = [col for col in mentioned_cols if col in numeric_cols]
            if len(numeric_mentioned) >= 2:
                x_col, y_col = numeric_mentioned[:2]
            else:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
                
        else:  # bar or line
            # Prefer categorical for x and numeric for y
            if mentioned_cols:
                x_col = next((col for col in mentioned_cols if col in categorical_cols), None)
                y_col = next((col for col in mentioned_cols if col in numeric_cols), None)
            
            # Fallback defaults
            if x_col is None:
                x_col = categorical_cols[0] if len(categorical_cols) > 0 else numeric_cols[0]
            if y_col is None:
                y_col = numeric_cols[0] if len(numeric_cols) > 0 else categorical_cols[0]
        
        # Create the figure
        fig = None
        if chart_type == 'histogram':
            fig = px.histogram(df, x=x_col, title=f'Distribution of {x_col}')
        elif chart_type == 'scatter':
            fig = px.scatter(df, x=x_col, y=y_col, title=f'{y_col} vs {x_col}')
        elif chart_type == 'line':
            fig = px.line(df, x=x_col, y=y_col, title=f'{y_col} over {x_col}')
        else:  # bar
            fig = px.bar(df, x=x_col, y=y_col, title=f'{y_col} by {x_col}')
        
        # Update layout
        fig.update_layout(
            template='plotly_white',
            title_x=0.5,
            margin=dict(t=100, l=50, r=50, b=50),
            showlegend=True,
            width=800,  # Optimal for UI display
            height=600,
            autosize=False
        )

        # Create reports directory if it doesn't exist
        os.makedirs('agentic_data_analysis/data/reports', exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        img_filename = f'plot_{timestamp}.png'
        img_path = os.path.join('agentic_data_analysis/data/reports', img_filename)
        
        # Generate image as bytes
        img_bytes = pio.to_image(fig, format='png')
        
        # Convert to base64 encoded string
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Create HTML-compatible image tag
        html_img = f"<img src='data:image/png;base64,{img_base64}'/>"
        
        return {
            "status": "success",
            "visualization": {
                "plotly": fig.to_json(),
                "image_html": html_img,  # UI-renderable format
                "type": chart_type,
                "x_column": x_col,
                "y_column": y_col
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def query_data_tool(query: str, tool_context: ToolContext):
    """Tool to handle complex data queries"""
    data = tool_context.state.get('data')
    if data is None:
        return {"status": "error", "message": "No data loaded. Please load data first."}
        
    try:
        df = pd.DataFrame(data)
        
        # Extract operations from query
        operations = {
            'filter': any(word in query.lower() for word in ['where', 'filter', 'only']),
            'sort': any(word in query.lower() for word in ['sort', 'order by']),
            'limit': 'top' in query.lower() or 'limit' in query.lower()
        }
        
        result = df.copy()
        
        # Apply operations based on query
        if operations['filter']:
            # Basic filtering
            for col in df.columns:
                if col.lower() in query.lower():
                    # Look for basic comparisons
                    if 'greater than' in query.lower() or '>' in query:
                        value = float(re.findall(r'\d+', query)[0])
                        result = result[result[col] > value]
                    elif 'less than' in query.lower() or '<' in query:
                        value = float(re.findall(r'\d+', query)[0])
                        result = result[result[col] < value]
                        
        if operations['sort']:
            for col in df.columns:
                if col.lower() in query.lower():
                    ascending = 'ascending' in query.lower() or 'asc' in query.lower()
                    result = result.sort_values(by=col, ascending=ascending)
                    break
                    
        if operations['limit']:
            limit = int(re.findall(r'\d+', query)[0]) if re.findall(r'\d+', query) else 5
            result = result.head(limit)
            
        return {
            "status": "success",
            "query_result": {
                "data": result.to_dict('records'),
                "shape": list(result.shape),
                "operations_applied": [k for k, v in operations.items() if v]
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Define the root agent
root_agent = Agent(
    name="data_analysis_assistant",
    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    instruction="""You are a data analysis assistant that can:
    1. Load and examine data from CSV and Excel files
    2. Provide summary statistics and insights
    3. Create visualizations (bar charts, scatter plots, histograms)
    4. Analyze relationships between variables
    
    When handling visualization requests:
    1. Check if data is loaded
    2. Determine the appropriate chart type
    3. Select relevant columns based on the query
    4. Create clear and informative visualizations
    5. Show file paths for image if you can't display them directly
    
    Supported chart types:
    - Bar charts for categorical comparisons
    - Scatter plots for relationships
    - Line charts for trends
    - Histograms for distributions""",
    tools=[load_data_tool, analyze_data_tool, visualize_data_tool, query_data_tool]
)