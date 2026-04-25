import os
import io
import csv
from pypdf import PdfReader
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentService:
    """Service for extracting and chunking text from documents"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from a file based on its extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.txt' or ext == '.md':
            return file_content.decode('utf-8')
            
        elif ext == '.pdf':
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        
        elif ext == '.docx':
            docx_file = io.BytesIO(file_content)
            doc = DocxDocument(docx_file)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        
        elif ext == '.csv':
            text_content = file_content.decode('utf-8')
            reader = csv.reader(io.StringIO(text_content))
            rows = list(reader)
            if not rows:
                return ""
            # Use first row as headers
            headers = rows[0]
            lines = []
            for row in rows[1:]:
                # Format each row as "Header1: Value1, Header2: Value2, ..."
                parts = []
                for i, val in enumerate(row):
                    header = headers[i] if i < len(headers) else f"Column {i+1}"
                    parts.append(f"{header}: {val}")
                lines.append(", ".join(parts))
            return "\n".join(lines)
            
        else:
            raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf, .txt, .docx, .csv, .md")
            
    def chunk_text(self, text: str) -> list[str]:
        """Split text into smaller chunks"""
        if not text.strip():
            return []
        return self.text_splitter.split_text(text)
        
    def process_document(self, file_content: bytes, filename: str) -> list[str]:
        """Extract text and return chunks"""
        text = self.extract_text(file_content, filename)
        chunks = self.chunk_text(text)
        return chunks
