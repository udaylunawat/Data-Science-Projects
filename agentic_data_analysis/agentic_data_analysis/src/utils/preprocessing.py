import pandas as pd
import numpy as np
from typing import List, Dict, Union
from ..config import DataConfig

class DataPreprocessor:
    """Generic data preprocessor for structured data"""
    
    def __init__(self, config: DataConfig = None):
        self.config = config or DataConfig()
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        return df
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: Dict = None) -> pd.DataFrame:
        """Handle missing values based on column types"""
        df = df.copy()
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna('Unknown')
                
        return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features based on data types"""
        df = df.copy()
        
        # Handle datetime columns
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            df[f'{col}_year'] = df[col].dt.year
            df[f'{col}_month'] = df[col].dt.month
            df[f'{col}_quarter'] = df[col].dt.quarter
            
        # Handle numeric columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_columns:
            df[f'{col}_binned'] = pd.qcut(df[col], 
                                        q=self.config.ANALYSIS_SETTINGS['numeric_binning_options']['default_bins'],
                                        duplicates='drop')
            
        return df