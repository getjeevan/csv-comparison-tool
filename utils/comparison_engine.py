import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st

class ComparisonEngine:
    """Handles data comparison operations including VLOOKUP-like functionality"""
    
    def __init__(self):
        self.comparison_stats = {}
    
    def vlookup_comparison(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          lookup_col1: str, lookup_col2: str, 
                          return_columns: List[str], match_types: List[str] = ["Exact Match"],
                          include_unmatched: bool = True) -> Dict[str, Any]:
        """
        Perform VLOOKUP-like comparison between two dataframes
        
        Args:
            df1: Primary dataframe (left table)
            df2: Lookup dataframe (right table) 
            lookup_col1: Column name in df1 to use as lookup key
            lookup_col2: Column name in df2 to use as lookup key
            return_columns: List of columns from df2 to include in results
            match_type: "Exact Match" or "Case Insensitive"
            include_unmatched: Whether to include unmatched records from df1
            
        Returns:
            Dict containing comparison results and statistics
        """
        # Prepare data for comparison
        df1_prep = df1.copy()
        df2_prep = df2.copy()
        
        # Create multiple lookup keys for different match types
        for i, match_type in enumerate(match_types):
            df1_prep[f'_lookup_key_{i}'] = self._standardize_lookup_key(
                df1_prep[lookup_col1], match_type
            )
            df2_prep[f'_lookup_key_{i}'] = self._standardize_lookup_key(
                df2_prep[lookup_col2], match_type
            )
        
        # Ensure return columns are valid
        valid_return_columns = [col for col in return_columns if col in df2.columns]
        if not valid_return_columns:
            valid_return_columns = df2.columns.tolist()
        
        # Create lookup dictionaries for each match type
        lookup_dicts = []
        for i in range(len(match_types)):
            lookup_dict = self._create_lookup_dict(df2_prep, valid_return_columns, f'_lookup_key_{i}')
            lookup_dicts.append(lookup_dict)
        
        # Perform the lookup with multiple match types
        results = self._perform_lookup(df1_prep, lookup_dicts, include_unmatched, match_types)
        
        # Calculate statistics
        stats = self._calculate_comparison_stats(results, df1, df2_prep)
        
        # Clean up temporary columns
        results = self._cleanup_results(results, lookup_col1, lookup_col2)
        
        return {
            'combined_data': results,
            'stats': stats,
            'lookup_info': {
                'primary_dataset_size': len(df1),
                'lookup_dataset_size': len(df2),
                'lookup_column_1': lookup_col1,
                'lookup_column_2': lookup_col2,
                'return_columns': valid_return_columns,
                'match_types': match_types
            }
        }
    
    def _standardize_lookup_key(self, series: pd.Series, match_type: str = "Exact Match") -> pd.Series:
        """Standardize lookup keys for comparison based on match type"""
        # Convert to string and handle NaN
        standardized = series.astype(str)
        standardized = standardized.replace('nan', np.nan)
        
        # Apply case sensitivity
        if match_type != "Exact Match":
            standardized = standardized.str.lower()
        
        # Strip whitespace
        standardized = standardized.str.strip()
        
        # Apply specific transformations based on match type
        if match_type == "Domain Prefix Match":
            # Extract prefix before first dot (for domain names)
            standardized = standardized.str.split('.').str[0]
        elif match_type == "Remove Special Chars":
            # Remove all non-alphanumeric characters
            standardized = standardized.str.replace(r'[^a-zA-Z0-9]', '', regex=True)
        elif match_type == "Numbers Only":
            # Extract only numeric characters
            standardized = standardized.str.extract(r'(\d+)', expand=False)
        elif match_type in ["Prefix Match", "Suffix Match", "Contains Match", "Fuzzy Match", "Word Order Insensitive"]:
            # Keep as is - these will be handled during lookup
            pass
        
        return standardized
    
    def _create_lookup_dict(self, df2_prep: pd.DataFrame, return_columns: List[str], lookup_key_col: str = '_lookup_key') -> Dict:
        """Create lookup dictionary from the second dataframe"""
        lookup_dict = {}
        
        # Include the lookup key and all return columns
        columns_to_include = [lookup_key_col] + return_columns
        
        for _, row in df2_prep.iterrows():
            key = row[lookup_key_col]
            if pd.notna(key):  # Only include non-null keys
                if key in lookup_dict:
                    # Handle duplicates - keep first occurrence but track duplicates
                    if '_duplicate_count' not in lookup_dict[key]:
                        lookup_dict[key]['_duplicate_count'] = 1
                    lookup_dict[key]['_duplicate_count'] += 1
                else:
                    # Create lookup entry
                    lookup_dict[key] = {}
                    for col in return_columns:
                        lookup_dict[key][col] = row.get(col, np.nan)
                    lookup_dict[key]['_duplicate_count'] = 0
        
        return lookup_dict
    
    def _perform_lookup(self, df1_prep: pd.DataFrame, lookup_dicts: List[Dict], 
                       include_unmatched: bool, match_types: List[str] = ["Exact Match"]) -> pd.DataFrame:
        """Perform the actual lookup operation"""
        results_list = []
        
        for _, row in df1_prep.iterrows():
            result_row = row.to_dict()
            match_found = False
            matched_with_type = None
            
            # Try each match type in order until we find a match
            for i, match_type in enumerate(match_types):
                if match_found:
                    break
                    
                lookup_key = row[f'_lookup_key_{i}']
                lookup_dict = lookup_dicts[i]
                
                if pd.notna(lookup_key):
                    # Try exact match first for preprocessing-based match types
                    if lookup_key in lookup_dict:
                        lookup_data = lookup_dict[lookup_key]
                        match_found = True
                        matched_with_type = match_type
                    elif match_type == "Prefix Match":
                        # Try prefix matching - find keys that start with lookup_key or vice versa
                        for dict_key in lookup_dict.keys():
                            if (str(lookup_key).startswith(str(dict_key)) or 
                                str(dict_key).startswith(str(lookup_key))):
                                lookup_data = lookup_dict[dict_key]
                                match_found = True
                                matched_with_type = match_type
                                break
                    elif match_type == "Suffix Match":
                        # Try suffix matching - find keys that end with lookup_key or vice versa
                        for dict_key in lookup_dict.keys():
                            if (str(lookup_key).endswith(str(dict_key)) or 
                                str(dict_key).endswith(str(lookup_key))):
                                lookup_data = lookup_dict[dict_key]
                                match_found = True
                                matched_with_type = match_type
                                break
                    elif match_type == "Contains Match":
                        # Try contains matching - find keys that contain lookup_key or vice versa
                        for dict_key in lookup_dict.keys():
                            if (str(dict_key) in str(lookup_key) or 
                                str(lookup_key) in str(dict_key)):
                                lookup_data = lookup_dict[dict_key]
                                match_found = True
                                matched_with_type = match_type
                                break
                    elif match_type == "Word Order Insensitive":
                        # Try word order insensitive matching
                        lookup_words = set(str(lookup_key).lower().split())
                        for dict_key in lookup_dict.keys():
                            dict_words = set(str(dict_key).lower().split())
                            if lookup_words == dict_words:
                                lookup_data = lookup_dict[dict_key]
                                match_found = True
                                matched_with_type = match_type
                                break
                    elif match_type == "Fuzzy Match":
                        # Try fuzzy matching with similarity threshold
                        from difflib import SequenceMatcher
                        best_score = 0
                        best_key = None
                        for dict_key in lookup_dict.keys():
                            score = SequenceMatcher(None, str(lookup_key), str(dict_key)).ratio()
                            if score > best_score and score >= 0.8:  # 80% similarity threshold
                                best_score = score
                                best_key = dict_key
                        if best_key:
                            lookup_data = lookup_dict[best_key]
                            match_found = True
                            matched_with_type = match_type
            
            if match_found:
                # Match found
                for col, value in lookup_data.items():
                    if col != '_duplicate_count':
                        result_row[f"{col}_from_lookup"] = value
                result_row['_match_status'] = 'Matched'
                result_row['_match_type_used'] = matched_with_type
                result_row['_has_duplicates'] = lookup_data.get('_duplicate_count', 0) > 0
            else:
                # No match found with any method
                if include_unmatched:
                    # Add empty columns for lookup data
                    if lookup_dicts and lookup_dicts[0]:
                        sample_key = next(iter(lookup_dicts[0]))
                        for col in lookup_dicts[0][sample_key].keys():
                            if col != '_duplicate_count':
                                result_row[f"{col}_from_lookup"] = np.nan
                    result_row['_match_status'] = 'Unmatched'
                    result_row['_match_type_used'] = None
                    result_row['_has_duplicates'] = False
                else:
                    continue  # Skip unmatched records
            
            # Clean up temporary lookup key columns
            for i in range(len(match_types)):
                if f'_lookup_key_{i}' in result_row:
                    del result_row[f'_lookup_key_{i}']
            
            results_list.append(result_row)
        
        return pd.DataFrame(results_list)
    
    def _calculate_comparison_stats(self, results: pd.DataFrame, 
                                   original_df1: pd.DataFrame, 
                                   df2_prep: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive comparison statistics"""
        total_records = len(original_df1)
        matched_count = len(results[results['_match_status'] == 'Matched'])
        unmatched_count = total_records - matched_count
        
        # Calculate duplicate keys in lookup dataset (use first lookup key column)
        lookup_key_cols = [col for col in df2_prep.columns if col.startswith('_lookup_key_')]
        if lookup_key_cols:
            duplicate_keys = df2_prep[lookup_key_cols[0]].duplicated().sum()
            unique_lookup_keys = df2_prep[lookup_key_cols[0]].nunique()
        else:
            duplicate_keys = 0
            unique_lookup_keys = 0
        
        # Calculate percentages
        match_percentage = (matched_count / total_records * 100) if total_records > 0 else 0
        unmatch_percentage = 100 - match_percentage
        
        stats = {
            'total_records': total_records,
            'matched_count': matched_count,
            'unmatched_count': unmatched_count,
            'match_percentage': match_percentage,
            'unmatch_percentage': unmatch_percentage,
            'duplicate_keys': duplicate_keys,
            'lookup_dataset_size': len(df2_prep),
            'unique_lookup_keys': unique_lookup_keys
        }
        
        return stats
    
    def _cleanup_results(self, results: pd.DataFrame, lookup_col1: str, 
                        lookup_col2: str) -> pd.DataFrame:
        """Clean up temporary columns and reorganize results"""
        # Remove temporary lookup key column
        if '_lookup_key' in results.columns:
            results = results.drop('_lookup_key', axis=1)
        
        # Reorder columns to put match status and original data first
        column_order = []
        
        # Add match status columns first
        status_columns = ['_match_status', '_match_type_used', '_has_duplicates']
        for col in status_columns:
            if col in results.columns:
                column_order.append(col)
        
        # Add original dataframe columns
        for col in results.columns:
            if not col.endswith('_from_lookup') and col not in status_columns:
                column_order.append(col)
        
        # Add lookup columns
        lookup_columns = [col for col in results.columns if col.endswith('_from_lookup')]
        column_order.extend(lookup_columns)
        
        # Reorder and return
        results = results[column_order]
        
        return results
    
    def generate_comparison_report(self, comparison_results: Dict[str, Any]) -> str:
        """Generate a text report of the comparison results"""
        stats = comparison_results['stats']
        lookup_info = comparison_results['lookup_info']
        
        report = f"""
        CSV Comparison Report
        =====================
        
        Dataset Information:
        - Primary Dataset: {lookup_info['primary_dataset_size']} records
        - Lookup Dataset: {lookup_info['lookup_dataset_size']} records
        - Lookup Column (Primary): {lookup_info['lookup_column_1']}
        - Lookup Column (Secondary): {lookup_info['lookup_column_2']}
        - Match Types: {', '.join(lookup_info.get('match_types', ['N/A']))}
        
        Comparison Results:
        - Total Records Processed: {stats['total_records']}
        - Matched Records: {stats['matched_count']} ({stats['match_percentage']:.1f}%)
        - Unmatched Records: {stats['unmatched_count']} ({stats['unmatch_percentage']:.1f}%)
        - Duplicate Keys in Lookup: {stats['duplicate_keys']}
        - Unique Lookup Keys: {stats['unique_lookup_keys']}
        
        Return Columns: {', '.join(lookup_info['return_columns'])}
        """
        
        return report.strip()
    
    def find_potential_matches(self, df1: pd.DataFrame, df2: pd.DataFrame,
                              col1: str, col2: str, similarity_threshold: float = 0.8) -> pd.DataFrame:
        """
        Find potential fuzzy matches between two columns
        
        Args:
            df1, df2: DataFrames to compare
            col1, col2: Column names to compare
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            DataFrame with potential matches and similarity scores
        """
        from difflib import SequenceMatcher
        
        potential_matches = []
        
        # Get unique values from both columns
        values1 = df1[col1].dropna().unique()
        values2 = df2[col2].dropna().unique()
        
        for val1 in values1:
            best_match = None
            best_score = 0
            
            for val2 in values2:
                # Calculate similarity
                score = SequenceMatcher(None, str(val1), str(val2)).ratio()
                
                if score > best_score and score >= similarity_threshold:
                    best_score = score
                    best_match = val2
            
            if best_match is not None:
                potential_matches.append({
                    'value_1': val1,
                    'value_2': best_match,
                    'similarity_score': best_score
                })
        
        return pd.DataFrame(potential_matches).sort_values('similarity_score', ascending=False)
