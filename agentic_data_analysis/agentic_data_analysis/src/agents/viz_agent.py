from google.adk import Agent, AgentContext, AgentResponse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from ..config import DataConfig, PromptTemplates

class VizAgent(Agent):
    """Agent for creating visualizations based on analysis results"""
    
    def __init__(self):
        super().__init__()
        self.config = DataConfig()
    
    def determine_chart_type(self, data: pd.DataFrame, analysis_type: str) -> str:
        """Determine the most appropriate chart type"""
        if data.index.nlevels > 1:
            return 'heatmap'
        elif len(data.columns) == 1:
            return 'bar'
        else:
            return 'line' if 'time' in analysis_type.lower() else 'bar'
    
    def create_visualization(self, data: pd.DataFrame, chart_type: str) -> Dict[str, Any]:
        """Create visualization using plotly"""
        fig = None
        
        if chart_type == 'bar':
            fig = px.bar(data)
        elif chart_type == 'line':
            fig = px.line(data)
        elif chart_type == 'heatmap':
            fig = px.imshow(data)
        elif chart_type == 'scatter':
            fig = px.scatter(data)
            
        return fig.to_dict() if fig else None
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Process visualization request"""
        try:
            analysis_result = context.state.get('analysis_result')
            if analysis_result is None:
                raise ValueError("No analysis results available for visualization")
                
            # Determine chart type
            chart_type = self.determine_chart_type(
                analysis_result,
                context.state.get('analysis_type', '')
            )
            
            # Create visualization
            viz = self.create_visualization(analysis_result, chart_type)
            
            return AgentResponse(
                success=True,
                message="Visualization created successfully",
                data={'visualization': viz, 'chart_type': chart_type}
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error creating visualization: {str(e)}"
            )