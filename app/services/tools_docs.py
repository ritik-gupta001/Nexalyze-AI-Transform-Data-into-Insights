from typing import Dict, Any
import io
from PyPDF2 import PdfReader
import docx

from app.core.logger import log


class DocumentProcessingTool:
    """Tool for processing and extracting text from documents"""
    
    async def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extract text from various document formats
        
        Supports: PDF, DOCX, TXT
        """
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return await self._extract_from_pdf(file_content)
            elif file_extension in ['docx', 'doc']:
                return await self._extract_from_docx(file_content)
            elif file_extension == 'txt':
                return file_content.decode('utf-8', errors='ignore')
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            log.error(f"Error extracting text from document: {e}")
            return f"Error processing document: {str(e)}"
    
    async def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PdfReader(pdf_file)
            
            text = []
            for page in pdf_reader.pages:
                text.append(page.extract_text())
            
            full_text = "\n".join(text)
            log.info(f"Extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            log.error(f"Error extracting from PDF: {e}")
            return f"Error reading PDF: {str(e)}"
    
    async def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            
            full_text = "\n".join(text)
            log.info(f"Extracted {len(full_text)} characters from DOCX")
            
            return full_text
            
        except Exception as e:
            log.error(f"Error extracting from DOCX: {e}")
            return f"Error reading DOCX: {str(e)}"
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """Split text into overlapping chunks for processing"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common document sections
        
        Returns dict with: abstract, introduction, methodology, results, conclusion
        """
        sections = {
            "full_text": text,
            "abstract": "",
            "introduction": "",
            "methodology": "",
            "results": "",
            "conclusion": ""
        }
        
        try:
            # Simple section detection (improve with better parsing)
            text_lower = text.lower()
            
            # Abstract
            if "abstract" in text_lower:
                start = text_lower.find("abstract")
                end = text_lower.find("introduction", start)
                if end == -1:
                    end = start + 500
                sections["abstract"] = text[start:end].strip()
            
            # Introduction
            if "introduction" in text_lower:
                start = text_lower.find("introduction")
                end = text_lower.find("method", start)
                if end == -1:
                    end = start + 1000
                sections["introduction"] = text[start:end].strip()
            
            # Methodology
            if "method" in text_lower:
                start = text_lower.find("method")
                end = text_lower.find("result", start)
                if end == -1:
                    end = start + 1000
                sections["methodology"] = text[start:end].strip()
            
            # Results
            if "result" in text_lower:
                start = text_lower.find("result")
                end = text_lower.find("conclusion", start)
                if end == -1:
                    end = start + 1000
                sections["results"] = text[start:end].strip()
            
            # Conclusion
            if "conclusion" in text_lower:
                start = text_lower.find("conclusion")
                sections["conclusion"] = text[start:start+1000].strip()
            
        except Exception as e:
            log.error(f"Error extracting sections: {e}")
        
        return sections
