from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.routers.document import get_current_user_id

router = APIRouter(prefix="/api/chat", tags=["chat"])

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    collection_name: str = "rag_collection"

class SourceChunk(BaseModel):
    id: str
    text: str
    similarity: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]

# Initialize services
embedding_service = EmbeddingService()
llm_service = LLMService()

def _search_and_format(collection_name, query, top_k):
    """Shared search logic for both streaming and non-streaming endpoints"""
    search_results = embedding_service.search(
        collection_name=collection_name,
        query=query,
        top_k=top_k
    )
    context_chunks = [res['text'] for res in search_results]
    sources = [
        SourceChunk(
            id=res.get('id', ''),
            text=res.get('text', ''),
            similarity=res.get('similarity', 0.0)
        )
        for res in search_results
    ]
    return context_chunks, sources

@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Submit a query (non-streaming). Returns full answer at once."""
    try:
        context_chunks, sources = _search_and_format(
            request.collection_name, request.query, request.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to search: " + str(e))
    
    try:
        if not context_chunks:
            answer = "I don't have any relevant information to answer your question."
        else:
            answer = llm_service.generate_rag_response(
                query=request.query,
                context_chunks=context_chunks
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate response: " + str(e))
    
    return QueryResponse(answer=answer, sources=sources)

@router.post("/query/stream")
async def query_rag_stream(
    request: QueryRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Submit a query (streaming). Returns answer word-by-word via SSE."""
    try:
        context_chunks, sources = _search_and_format(
            request.collection_name, request.query, request.top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to search: " + str(e))
    
    def event_generator():
        if not context_chunks:
            no_info = "I don't have any relevant information to answer your question."
            msg = json.dumps({"type": "text", "content": no_info})
            yield "data: " + msg + "\n\n"
        else:
            for text_chunk in llm_service.generate_rag_response_stream(
                query=request.query,
                context_chunks=context_chunks
            ):
                msg = json.dumps({"type": "text", "content": text_chunk})
                yield "data: " + msg + "\n\n"
        
        # Send sources as final event
        sources_list = []
        for s in sources:
            sources_list.append({"id": s.id, "text": s.text, "similarity": s.similarity})
        msg = json.dumps({"type": "sources", "content": sources_list})
        yield "data: " + msg + "\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
