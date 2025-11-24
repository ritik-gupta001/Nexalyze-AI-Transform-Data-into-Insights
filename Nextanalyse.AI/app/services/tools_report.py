from fpdf import FPDF
from pathlib import Path
from typing import Optional
import markdown
from datetime import datetime

from app.core.config import get_settings
from app.core.logger import log

settings = get_settings()


class ReportGenerator:
    """Tool for generating reports in various formats"""
    
    async def generate_pdf_report(
        self,
        task_id: str,
        title: str,
        content: str,
        charts: list = None
    ) -> str:
        """
        Generate PDF report from markdown content
        
        Returns: path to generated PDF
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Title
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, title, ln=True, align='C')
            pdf.ln(5)
            
            # Date
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.ln(5)
            
            # Content
            pdf.set_font('Arial', '', 11)
            
            # Parse markdown content
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    pdf.set_font('Arial', 'B', 14)
                    pdf.cell(0, 10, line[2:], ln=True)
                    pdf.set_font('Arial', '', 11)
                elif line.startswith('## '):
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 8, line[3:], ln=True)
                    pdf.set_font('Arial', '', 11)
                elif line.startswith('### '):
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 7, line[4:], ln=True)
                    pdf.set_font('Arial', '', 11)
                elif line.startswith('- ') or line.startswith('* '):
                    pdf.cell(10, 6, '', ln=False)
                    pdf.multi_cell(0, 6, f"• {line[2:]}")
                elif line.startswith('**') and line.endswith('**'):
                    pdf.set_font('Arial', 'B', 11)
                    pdf.multi_cell(0, 6, line.strip('*'))
                    pdf.set_font('Arial', '', 11)
                elif line.strip():
                    pdf.multi_cell(0, 6, line)
                else:
                    pdf.ln(3)
            
            # Add charts if provided
            if charts:
                pdf.add_page()
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Visualizations', ln=True)
                pdf.ln(5)
                
                for chart_path in charts:
                    if Path(chart_path).exists():
                        try:
                            pdf.image(chart_path, x=10, w=180)
                            pdf.ln(5)
                        except Exception as e:
                            log.warning(f"Could not add chart to PDF: {e}")
            
            # Save PDF
            filename = f"{task_id}-report.pdf"
            report_path = f"{settings.REPORTS_DIR}/{filename}"
            Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
            pdf.output(report_path)
            
            # Return URL path, not file system path
            report_url = f"/reports/{filename}"
            log.info(f"PDF report generated: {report_path} -> URL: {report_url}")
            return report_url
            
        except Exception as e:
            log.error(f"Error generating PDF report: {e}")
            # Fallback to markdown
            return await self.generate_markdown_report(task_id, title, content)
    
    async def generate_markdown_report(
        self,
        task_id: str,
        title: str,
        content: str
    ) -> str:
        """
        Generate Markdown report
        
        Returns: path to generated markdown file
        """
        try:
            full_content = f"# {title}\n\n"
            full_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            full_content += "---\n\n"
            full_content += content
            
            filename = f"{task_id}-report.md"
            report_path = f"{settings.REPORTS_DIR}/{filename}"
            Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # Return URL path, not file system path
            report_url = f"/reports/{filename}"
            log.info(f"Markdown report generated: {report_path} -> URL: {report_url}")
            return report_url
            
        except Exception as e:
            log.error(f"Error generating markdown report: {e}")
            return ""
    
    def create_executive_summary(
        self,
        task_type: str,
        entity: Optional[str],
        key_findings: list
    ) -> str:
        """Create executive summary section"""
        summary = f"## Executive Summary\n\n"
        summary += f"**Analysis Type:** {task_type.replace('_', ' ').title()}\n\n"
        
        if entity:
            summary += f"**Subject:** {entity}\n\n"
        
        summary += "**Key Findings:**\n\n"
        for finding in key_findings:
            summary += f"- {finding}\n"
        
        summary += "\n"
        return summary
    
    def format_sentiment_summary(self, sentiment_data: dict) -> str:
        """Format sentiment data for report"""
        content = "## Sentiment Analysis\n\n"
        content += f"**Overall Sentiment:** {sentiment_data.get('overall', 'N/A')}\n\n"
        content += f"- Positive: {sentiment_data.get('positive', 0) * 100:.1f}%\n"
        content += f"- Neutral: {sentiment_data.get('neutral', 0) * 100:.1f}%\n"
        content += f"- Negative: {sentiment_data.get('negative', 0) * 100:.1f}%\n"
        content += f"- Confidence: {sentiment_data.get('confidence', 0) * 100:.1f}%\n\n"
        return content
