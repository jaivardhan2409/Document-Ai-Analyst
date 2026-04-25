from typing import List, Dict
import chromadb
import google.generativeai as genai
from app.config import settings

class EmbeddingService:
    """Service for handling embeddings and vector search using Google Gemini"""
    
    def __init__(self):
        # Initialize ChromaDB persistent client
        self.chroma_client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        # Configure Gemini for embeddings
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        
    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Gemini's embedding model"""
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=texts,
        )
        return result['embedding']
        
    def get_or_create_collection(self, collection_name: str):
        """Get or create a ChromaDB collection"""
        return self.chroma_client.get_or_create_collection(name=collection_name)
    
    def add_chunks_to_collection(self, collection_name: str, document_id: str, chunks: List[str]):
        """Convert chunks to embeddings and store them in ChromaDB"""
        if not chunks:
            return
            
        collection = self.get_or_create_collection(collection_name)
        
        # Generate embeddings via Gemini API (batch in groups of 100 to avoid limits)
        all_embeddings = []
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_embeddings = self._embed(batch)
            all_embeddings.extend(batch_embeddings)
        
        # Create IDs and Metadata
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        
        # Add to collection
        collection.add(
            embeddings=all_embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, collection_name: str, query: str, top_k: int) -> List[Dict]:
        """Search ChromaDB using semantic vector search"""
        collection = self.get_or_create_collection(collection_name)
        
        # Check if collection has any documents
        if collection.count() == 0:
            return []
        
        # Convert query to embedding via Gemini
        query_embedding = self._embed([query])[0]
        
        # Search collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )
        
        # Format results
        formatted_results = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                })
                
        return formatted_results
    
    def delete_collection(self, collection_name: str):
        """Delete a ChromaDB collection entirely"""
        try:
            self.chroma_client.delete_collection(collection_name)
        except ValueError:
            pass  # Collection doesn't exist, that's fine
    
    def list_collections(self) -> List[str]:
        """List all ChromaDB collection names"""
        collections = self.chroma_client.list_collections()
        return [c.name for c in collections]
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of chunks in a collection"""
        try:
            collection = self.chroma_client.get_collection(collection_name)
            return collection.count()
        except Exception:
            return 0
