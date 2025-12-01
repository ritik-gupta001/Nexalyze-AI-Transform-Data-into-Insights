import pandas as pd
import numpy as np
from typing import Dict, Any, List
import io

from app.core.logger import log


class DataAnalysisTool:
    """Tool for analyzing CSV/Excel data"""
    
    async def load_data(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Load data from CSV or Excel file"""
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'csv':
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            log.info(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            log.error(f"Error loading data: {e}")
            raise
    
    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive statistics about the dataset"""
        try:
            stats = {
                "shape": {
                    "rows": int(df.shape[0]),
                    "columns": int(df.shape[1])
                },
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "numeric_summary": {},
                "categorical_summary": {}
            }
            
            # Numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                stats["numeric_summary"] = df[numeric_cols].describe().to_dict()
            
            # Categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                stats["categorical_summary"] = {
                    col: {
                        "unique": int(df[col].nunique()),
                        "top": str(df[col].mode()[0]) if not df[col].mode().empty else "N/A",
                        "freq": int(df[col].value_counts().iloc[0]) if len(df[col].value_counts()) > 0 else 0
                    }
                    for col in categorical_cols[:5]  # Limit to first 5
                }
            
            return stats
            
        except Exception as e:
            log.error(f"Error calculating statistics: {e}")
            return {}
    
    def format_stats_for_display(self, stats: Dict) -> str:
        """Format statistics for readable display"""
        lines = []
        
        lines.append(f"Dataset Shape: {stats['shape']['rows']} rows × {stats['shape']['columns']} columns")
        lines.append(f"\nColumns: {', '.join(stats['columns'])}")
        
        if stats.get('numeric_summary'):
            lines.append("\n### Numeric Summary:")
            for col, values in list(stats['numeric_summary'].items())[:3]:
                lines.append(f"\n{col}:")
                lines.append(f"  Mean: {values.get('mean', 0):.2f}")
                lines.append(f"  Std: {values.get('std', 0):.2f}")
                lines.append(f"  Min: {values.get('min', 0):.2f}")
                lines.append(f"  Max: {values.get('max', 0):.2f}")
        
        return "\n".join(lines)
    
    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns and insights in data"""
        patterns = {
            "correlations": [],
            "trends": [],
            "outliers": []
        }
        
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            
            # Correlations
            if len(numeric_df.columns) >= 2:
                corr_matrix = numeric_df.corr()
                
                # Find strong correlations
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            patterns["correlations"].append({
                                "col1": corr_matrix.columns[i],
                                "col2": corr_matrix.columns[j],
                                "correlation": float(corr_val)
                            })
            
            # Simple trend detection (if there's a date/time column)
            for col in numeric_df.columns[:3]:  # Check first 3 numeric columns
                values = numeric_df[col].dropna()
                if len(values) > 10:
                    # Linear trend
                    x = np.arange(len(values))
                    slope = np.polyfit(x, values, 1)[0]
                    
                    if abs(slope) > values.std() * 0.01:
                        patterns["trends"].append({
                            "column": col,
                            "trend": "increasing" if slope > 0 else "decreasing",
                            "slope": float(slope)
                        })
            
        except Exception as e:
            log.error(f"Error detecting patterns: {e}")
        
        return patterns
    
    def find_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """Find anomalies in numeric columns"""
        anomalies = []
        
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            
            for col in numeric_df.columns[:5]:  # Limit to first 5 columns
                values = numeric_df[col].dropna()
                
                if len(values) > 3:
                    mean = values.mean()
                    std = values.std()
                    
                    if std > 0:
                        z_scores = np.abs((values - mean) / std)
                        outlier_indices = np.where(z_scores > 3)[0]
                        
                        if len(outlier_indices) > 0:
                            anomalies.append({
                                "column": col,
                                "count": len(outlier_indices),
                                "examples": values.iloc[outlier_indices[:3]].tolist()
                            })
        
        except Exception as e:
            log.error(f"Error finding anomalies: {e}")
        
        return anomalies
