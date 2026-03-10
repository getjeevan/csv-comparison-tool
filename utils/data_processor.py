import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Dict, Any

class DataProcessor:
    """Handles CSV file loading and basic data processing operations"""
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    def load_csv(self, uploaded_file) -> pd.DataFrame:
        """
        Load CSV file with automatic encoding detection and error handling
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pandas.DataFrame: Loaded and processed dataframe
            
        Raises:
            Exception: If file cannot be loaded with any supported encoding
        """
        # Common delimiters to try
        delimiters = [',', ';', '\t', '|']
        
        for encoding in self.supported_encodings:
            for delimiter in delimiters:
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Try to read with current encoding and delimiter
                    df = pd.read_csv(
                        uploaded_file, 
                        encoding=encoding,
                        delimiter=delimiter,
                        quotechar='"',
                        quoting=1,  # QUOTE_ALL
                        skipinitialspace=True,
                        on_bad_lines='skip',  # Skip problematic lines
                        engine='python'  # More flexible than C engine
                    )
                    
                    # Basic validation
                    if df.empty:
                        continue
                    
                    # Check if we got reasonable columns (not just one huge column)
                    if len(df.columns) == 1 and delimiter != delimiters[-1]:
                        continue
                    
                    # Clean the dataframe
                    df = self._clean_dataframe(df)
                    
                    return df
                    
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    # If this is the last combination, try with error handling
                    if encoding == self.supported_encodings[-1] and delimiter == delimiters[-1]:
                        try:
                            uploaded_file.seek(0)
                            # Last resort: try with maximum flexibility
                            df = pd.read_csv(
                                uploaded_file,
                                encoding=encoding,
                                delimiter=',',
                                quotechar='"',
                                quoting=1,
                                skipinitialspace=True,
                                on_bad_lines='skip',
                                engine='python',
                                error_bad_lines=False  # For older pandas versions
                            )
                            if not df.empty:
                                return self._clean_dataframe(df)
                        except:
                            pass
                        raise Exception(f"Could not load file: {str(e)}")
                    continue
        
        raise Exception("Could not load file with any supported encoding or delimiter")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess the dataframe
        
        Args:
            df: Input dataframe
            
        Returns:
            pandas.DataFrame: Cleaned dataframe
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Strip whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].astype(str).str.strip()
            # Replace 'nan' strings with actual NaN
            df[col] = df[col].replace('nan', np.nan)
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def get_column_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get detailed information about dataframe columns
        
        Args:
            df: Input dataframe
            
        Returns:
            Dict containing column information
        """
        column_info = {}
        
        for col in df.columns:
            column_info[col] = {
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique(),
                'sample_values': df[col].dropna().head(3).tolist()
            }
        
        return column_info
    
    def detect_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Automatically detect and convert appropriate data types
        
        Args:
            df: Input dataframe
            
        Returns:
            pandas.DataFrame: DataFrame with optimized data types
        """
        df_copy = df.copy()
        
        for col in df_copy.columns:
            # Try to convert to numeric
            if df_copy[col].dtype == 'object':
                # Try integer conversion
                try:
                    numeric_series = pd.to_numeric(df_copy[col], errors='coerce')
                    if numeric_series.notna().sum() > len(df_copy) * 0.8:  # 80% success rate
                        if numeric_series.dropna().apply(lambda x: x.is_integer()).all():
                            df_copy[col] = numeric_series.astype('Int64')  # Nullable integer
                        else:
                            df_copy[col] = numeric_series
                except:
                    pass
                
                # Try datetime conversion
                try:
                    datetime_series = pd.to_datetime(df_copy[col], errors='coerce')
                    if datetime_series.notna().sum() > len(df_copy) * 0.8:  # 80% success rate
                        df_copy[col] = datetime_series
                except:
                    pass
        
        return df_copy
    
    def standardize_key_column(self, series: pd.Series, case_sensitive: bool = True) -> pd.Series:
        """
        Standardize a key column for comparison
        
        Args:
            series: Input pandas Series
            case_sensitive: Whether to maintain case sensitivity
            
        Returns:
            pandas.Series: Standardized series
        """
        # Convert to string and handle NaN values
        standardized = series.astype(str)
        
        # Handle NaN values
        standardized = standardized.replace('nan', np.nan)
        
        if not case_sensitive:
            # Convert to lowercase for case-insensitive comparison
            standardized = standardized.str.lower()
        
        # Strip whitespace
        standardized = standardized.str.strip()
        
        return standardized
    
    def validate_comparison_columns(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                                   col1: str, col2: str) -> Dict[str, Any]:
        """
        Validate columns selected for comparison
        
        Args:
            df1, df2: DataFrames to compare
            col1, col2: Column names for comparison
            
        Returns:
            Dict containing validation results and recommendations
        """
        validation_result = {
            'valid': True,
            'warnings': [],
            'recommendations': []
        }
        
        # Check if columns exist
        if col1 not in df1.columns:
            validation_result['valid'] = False
            validation_result['warnings'].append(f"Column '{col1}' not found in Dataset 1")
        
        if col2 not in df2.columns:
            validation_result['valid'] = False
            validation_result['warnings'].append(f"Column '{col2}' not found in Dataset 2")
        
        if not validation_result['valid']:
            return validation_result
        
        # Check data types compatibility
        dtype1 = df1[col1].dtype
        dtype2 = df2[col2].dtype
        
        if dtype1 != dtype2:
            validation_result['warnings'].append(
                f"Data type mismatch: {col1} ({dtype1}) vs {col2} ({dtype2})"
            )
            validation_result['recommendations'].append(
                "Consider converting both columns to the same data type"
            )
        
        # Check for high null percentage
        null_pct1 = df1[col1].isnull().sum() / len(df1) * 100
        null_pct2 = df2[col2].isnull().sum() / len(df2) * 100
        
        if null_pct1 > 20:
            validation_result['warnings'].append(
                f"High null percentage in {col1}: {null_pct1:.1f}%"
            )
        
        if null_pct2 > 20:
            validation_result['warnings'].append(
                f"High null percentage in {col2}: {null_pct2:.1f}%"
            )
        
        # Check for duplicates in lookup column (df2)
        duplicate_count = df2[col2].duplicated().sum()
        if duplicate_count > 0:
            validation_result['warnings'].append(
                f"Found {duplicate_count} duplicate values in lookup column '{col2}'"
            )
            validation_result['recommendations'].append(
                "Duplicate keys in lookup column may cause unexpected results"
            )
        
        return validation_result
