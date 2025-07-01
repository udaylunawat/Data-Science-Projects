import pandas as pd
from pathlib import Path
from typing import Union, Optional
from ..config import DataConfig

class DataLoader:
    """Generic data loader for structured data files"""
    
    def __init__(self, config: Optional[DataConfig] = None):
        self.config = config or DataConfig()
        
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """Validate if file type is supported"""
        return Path(file_path).suffix.lower() in self.config.ALLOWED_EXTENSIONS
    
    def infer_dtypes(self, df: pd.DataFrame) -> dict:
        """Automatically infer column data types"""
        dtypes = {}
        for col in df.columns:
            # Attempt to identify column type
            if pd.api.types.is_numeric_dtype(df[col]):
                dtypes[col] = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                dtypes[col] = 'datetime'
            else:
                # Check if column could be datetime
                try:
                    pd.to_datetime(df[col])
                    dtypes[col] = 'datetime'
                except:
                    dtypes[col] = 'categorical'
        return dtypes
    
    def load_data(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load data from file with automatic type inference"""
        if not self.validate_file(file_path):
            raise ValueError(f"Unsupported file format. Supported: {self.config.ALLOWED_EXTENSIONS}")
            
        # Load data based on file type
        file_path = Path(file_path)
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path, **kwargs)
        else:
            df = pd.read_excel(file_path, **kwargs)
            
        # Infer and set column types
        dtypes = self.infer_dtypes(df)
        
        # Convert columns based on inferred types
        for col, dtype in dtypes.items():
            if dtype == 'datetime':
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif dtype == 'numeric':
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df