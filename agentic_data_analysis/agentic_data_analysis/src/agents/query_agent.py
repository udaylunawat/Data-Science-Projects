from google.adk import Agent, AgentContext, AgentResponse
import pandas as pd
import numpy as np
from typing import Dict, List
import re

class QueryAgent(Agent):
    """Agent for converting natural language questions to data analysis operations"""
    
    def __init__(self):
        super().__init__()
        
    def extract_analysis_params(self, question: str) -> Dict:
        """Extract analysis parameters from question"""
        params = {
            'aggregations': [],
            'group_by': [],
            'filters': [],
            'sort_by': [],
            'limit': None
        }
        
        # Extract aggregations (e.g., average, sum, count)
        agg_patterns = {
            'mean': r'average|mean',
            'sum': r'sum|total',
            'count': r'count|number of|how many',
            'max': r'maximum|highest|top',
            'min': r'minimum|lowest|bottom'
        }
        
        for agg, pattern in agg_patterns.items():
            if re.search(pattern, question, re.IGNORECASE):
                params['aggregations'].append(agg)
        
        # Extract group by columns
        if 'by' in question.lower():
            by_parts = question.lower().split('by')[1].split('and')
            params['group_by'] = [part.strip() for part in by_parts]
            
        return params
    
    async def process(self, context: AgentContext) -> AgentResponse:
        """Process the analysis request"""
        try:
            question = context.state.get('prompt')
            df = context.state.get('data')
            
            if df is None:
                raise ValueError("No data available for analysis")
                
            # Extract analysis parameters
            params = self.extract_analysis_params(question)
            
            # Generate and execute analysis code
            result = self.execute_analysis(df, params)
            
            context.state['analysis_result'] = result
            return AgentResponse(
                success=True,
                message="Analysis completed successfully",
                data=result
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error in analysis: {str(e)}"
            )
            
    def execute_analysis(self, df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """Execute the analysis based on extracted parameters"""
        if not params['aggregations']:
            params['aggregations'] = ['count']
            
        if params['group_by']:
            result = df.groupby(params['group_by']).agg(
                {col: params['aggregations'] for col in df.select_dtypes(include=['number']).columns}
            )
        else:
            result = df.agg(
                {col: params['aggregations'] for col in df.select_dtypes(include=['number']).columns}
            )
            
        return result