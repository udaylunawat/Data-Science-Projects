from typing import Dict, List

class DataConfig:
    """Configuration settings for data processing"""
    ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']
    DATE_FORMAT = '%d.%b.%y'  # Default date format
    
    # Data type inference settings
    TYPE_INFERENCE_SETTINGS = {
        'date_columns': [],  # Will be auto-detected
        'numeric_columns': [],  # Will be auto-detected
        'categorical_columns': [],  # Will be auto-detected
        'id_columns': []  # Will be auto-detected
    }
    
    # Analysis settings
    ANALYSIS_SETTINGS = {
        'default_aggregations': ['mean', 'median', 'count', 'sum', 'std'],
        'time_grouping_options': ['year', 'month', 'quarter', 'week'],
        'numeric_binning_options': {
            'default_bins': 5,
            'max_bins': 20
        }
    }
    
    # Visualization settings
    VIZ_SETTINGS = {
        'default_charts': ['bar', 'line', 'scatter', 'pie', 'heatmap'],
        'color_palette': 'default',
        'fig_size': (10, 6)
    }

class PromptTemplates:
    """Templates for agent interactions"""
    DATA_ANALYSIS_PROMPT = """
    You are a data analysis agent. Given the data and question, you should:
    1. Understand the question intent
    2. Identify relevant columns
    3. Determine appropriate analysis methods
    4. Generate appropriate code
    5. Provide insights from the analysis
    
    Current data summary:
    {data_summary}
    
    Question: {question}
    """

    VISUALIZATION_PROMPT = """
    Based on the analysis results, determine the most appropriate visualization:
    1. Consider the data types involved
    2. Consider the analysis goal (comparison, distribution, trend, etc.)
    3. Choose appropriate chart type and settings
    
    Analysis results:
    {analysis_results}
    """