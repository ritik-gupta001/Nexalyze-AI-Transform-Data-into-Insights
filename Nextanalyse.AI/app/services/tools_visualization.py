import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict
from pathlib import Path

from app.core.config import get_settings
from app.core.logger import log

settings = get_settings()


class VisualizationTool:
    """Tool for creating charts and visualizations"""
    
    def __init__(self):
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    async def create_sentiment_chart(
        self,
        task_id: str,
        sentiment_data: List[Dict[str, float]],
        entity: str = "Entity"
    ) -> str:
        """
        Create sentiment trend chart
        
        Returns: path to saved chart
        """
        try:
            # Extract data
            if not sentiment_data:
                return ""
            
            positive = [s.get('positive', 0) for s in sentiment_data]
            neutral = [s.get('neutral', 0) for s in sentiment_data]
            negative = [s.get('negative', 0) for s in sentiment_data]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x = np.arange(len(positive))
            width = 0.25
            
            ax.bar(x - width, positive, width, label='Positive', color='#2ecc71', alpha=0.8)
            ax.bar(x, neutral, width, label='Neutral', color='#95a5a6', alpha=0.8)
            ax.bar(x + width, negative, width, label='Negative', color='#e74c3c', alpha=0.8)
            
            ax.set_xlabel('Article Index')
            ax.set_ylabel('Sentiment Score')
            ax.set_title(f'Sentiment Analysis: {entity}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Save
            filename = f"{task_id}-sentiment.png"
            chart_path = f"{settings.CHARTS_DIR}/{filename}"
            Path(settings.CHARTS_DIR).mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Return URL path, not file system path
            chart_url = f"/charts/{filename}"
            log.info(f"Sentiment chart saved: {chart_path} -> URL: {chart_url}")
            return chart_url
            
        except Exception as e:
            log.error(f"Error creating sentiment chart: {e}")
            return ""
    
    async def create_trend_chart(
        self,
        task_id: str,
        historical_scores: List[float],
        forecast_scores: List[float],
        entity: str = "Entity"
    ) -> str:
        """
        Create trend forecast chart
        
        Returns: path to saved chart
        """
        try:
            if not historical_scores:
                return ""
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Historical data
            hist_x = np.arange(len(historical_scores))
            ax.plot(hist_x, historical_scores, 'o-', label='Historical', 
                   color='#3498db', linewidth=2, markersize=6)
            
            # Forecast data
            if forecast_scores:
                forecast_x = np.arange(len(historical_scores), 
                                      len(historical_scores) + len(forecast_scores))
                ax.plot(forecast_x, forecast_scores, 's--', label='Forecast', 
                       color='#e67e22', linewidth=2, markersize=6, alpha=0.7)
                
                # Add shaded region for forecast
                ax.axvspan(len(historical_scores)-0.5, forecast_x[-1]+0.5, 
                          alpha=0.1, color='orange')
            
            ax.set_xlabel('Time Period')
            ax.set_ylabel('Sentiment Score')
            ax.set_title(f'Sentiment Trend & Forecast: {entity}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_ylim([0, 1])
            
            # Save
            # Save
            filename = f"{task_id}-trend.png"
            chart_path = f"{settings.CHARTS_DIR}/{filename}"
            Path(settings.CHARTS_DIR).mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Return URL path, not file system path
            chart_url = f"/charts/{filename}"
            log.info(f"Trend chart saved: {chart_path} -> URL: {chart_url}")
            return chart_url
            
        except Exception as e:
            log.error(f"Error creating trend chart: {e}")
            return ""
    
    async def create_distribution_chart(
        self,
        task_id: str,
        data: np.ndarray,
        title: str = "Distribution"
    ) -> str:
        """Create distribution/histogram chart"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.hist(data, bins=30, color='#3498db', alpha=0.7, edgecolor='black')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
            
            # Save
            # Save
            filename = f"{task_id}-distribution.png"
            chart_path = f"{settings.CHARTS_DIR}/{filename}"
            Path(settings.CHARTS_DIR).mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Return URL path, not file system path
            chart_url = f"/charts/{filename}"
            log.info(f"Distribution chart saved: {chart_path} -> URL: {chart_url}")
            return chart_url
            
        except Exception as e:
            log.error(f"Error creating distribution chart: {e}")
            return ""
    
    async def create_correlation_heatmap(
        self,
        task_id: str,
        correlation_matrix,
        title: str = "Correlation Matrix"
    ) -> str:
        """Create correlation heatmap from DataFrame corr()"""
        try:
            import pandas as pd
            
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Handle both numpy array and pandas DataFrame
            if isinstance(correlation_matrix, pd.DataFrame):
                sns.heatmap(
                    correlation_matrix,
                    annot=True,
                    fmt='.2f',
                    cmap='RdYlGn',
                    center=0,
                    square=True,
                    linewidths=0.5,
                    cbar_kws={"shrink": 0.8},
                    ax=ax
                )
            else:
                sns.heatmap(
                    correlation_matrix,
                    annot=True,
                    fmt='.2f',
                    cmap='RdYlGn',
                    center=0,
                    square=True,
                    ax=ax
                )
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # Save
            # Save
            filename = f"{task_id}-correlation.png"
            chart_path = f"{settings.CHARTS_DIR}/{filename}"
            Path(settings.CHARTS_DIR).mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Return URL path, not file system path
            chart_url = f"/charts/{filename}"
            log.info(f"Correlation heatmap saved: {chart_path} -> URL: {chart_url}")
            return chart_url
            
        except Exception as e:
            log.error(f"Error creating correlation heatmap: {e}")
            return ""
    
    async def create_time_series_chart(
        self,
        task_id: str,
        df,
        date_column: str,
        value_column: str,
        title: str
    ) -> str:
        """Create time series / trend chart"""
        try:
            import pandas as pd
            
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # Sort by date
            df_sorted = df[[date_column, value_column]].copy()
            df_sorted = df_sorted.sort_values(date_column)
            df_sorted = df_sorted.dropna()
            
            # Plot
            ax.plot(df_sorted[date_column], df_sorted[value_column], 
                   linewidth=2, color='#2ecc71', marker='o', markersize=4)
            
            ax.set_xlabel(date_column, fontsize=11)
            ax.set_ylabel(value_column, fontsize=11)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save
            # Save
            filename = f"{task_id}-timeseries.png"
            chart_path = f"{settings.CHARTS_DIR}/{filename}"
            Path(settings.CHARTS_DIR).mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Return URL path, not file system path
            chart_url = f"/charts/{filename}"
            log.info(f"Time series chart saved: {chart_path} -> URL: {chart_url}")
            return chart_url
            
        except Exception as e:
            log.error(f"Error creating time series chart: {e}")
            return ""
    
    async def create_bar_chart(
        self,
        task_id: str,
        labels: List[str],
        values: List[float],
        title: str
    ) -> str:
        """Create horizontal bar chart"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create horizontal bar chart
            colors = ['#2ecc71' if v > 0 else '#e74c3c' for v in values]
            ax.barh(labels, values, color=colors, alpha=0.8)
            
            ax.set_xlabel('Correlation Coefficient', fontsize=11)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            ax.axvline(x=0, color='black', linewidth=0.8)
            
            plt.tight_layout()
            
            # Save
            filename = f"{task_id}-barchart.png"
            chart_path = f"{settings.CHARTS_DIR}/{filename}"
            Path(settings.CHARTS_DIR).mkdir(parents=True, exist_ok=True)
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Return URL path, not file system path
            chart_url = f"/charts/{filename}"
            log.info(f"Bar chart saved: {chart_path} -> URL: {chart_url}")
            return chart_url
            
        except Exception as e:
            log.error(f"Error creating bar chart: {e}")
            return ""
