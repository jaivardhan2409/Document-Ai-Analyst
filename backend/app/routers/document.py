from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
from app.dependencies import get_db
from app.models.database import Document, Collection
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.auth_service import decode_access_token

router = APIRouter(prefix="/api/documents", tags=["documents"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id

# Initialize services
document_service = DocumentService()
embedding_service = EmbeddingService()

# ==========================================
# Collection Endpoints
# ==========================================

class CreateCollectionRequest(BaseModel):
    name: str
    description: str = ""

class CollectionResponse(BaseModel):
    id: str
    name: str
    description: str
    chunk_count: int
    doc_count: int

@router.post("/collections")
async def create_collection(
    request: CreateCollectionRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new knowledge base collection"""
    # Check if collection name already exists for this user
    existing = db.query(Collection).filter(
        Collection.user_id == user_id,
        Collection.name == request.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Collection with this name already exists")
    
    new_collection = Collection(
        user_id=user_id,
        name=request.name,
        description=request.description
    )
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    
    return {
        "id": new_collection.id,
        "name": new_collection.name,
        "description": new_collection.description,
        "message": "Collection created successfully"
    }

@router.get("/collections", response_model=List[CollectionResponse])
async def list_collections(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List all collections for the current user"""
    collections = db.query(Collection).filter(Collection.user_id == user_id).all()
    
    result = []
    for col in collections:
        # Use a safe collection name for ChromaDB (replace spaces, lowercase)
        chroma_name = f"col_{col.id[:8]}"
        chunk_count = embedding_service.get_collection_count(chroma_name)
        doc_count = db.query(Document).filter(Document.collection_id == col.id).count()
        result.append(CollectionResponse(
            id=col.id,
            name=col.name,
            description=col.description,
            chunk_count=chunk_count,
            doc_count=doc_count
        ))
    
    return result

@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a collection and all its data"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == user_id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Delete from ChromaDB
    chroma_name = f"col_{collection.id[:8]}"
    embedding_service.delete_collection(chroma_name)
    
    # Delete documents from DB
    db.query(Document).filter(Document.collection_id == collection_id).delete()
    
    # Delete collection from DB
    db.delete(collection)
    db.commit()
    
    return {"message": f"Collection '{collection.name}' deleted successfully"}

# ==========================================
# Document Upload Endpoint
# ==========================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    collection_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Upload a document, process text, chunk it, and save embeddings"""
    
    # Determine ChromaDB collection name
    if collection_id:
        # Verify collection belongs to user
        collection = db.query(Collection).filter(
            Collection.id == collection_id,
            Collection.user_id == user_id
        ).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        chroma_collection_name = f"col_{collection.id[:8]}"
    else:
        chroma_collection_name = "rag_collection"
    
    # 1. Read file
    content = await file.read()
    
    # 2. Save document metadata to Postgres
    new_doc = Document(
        user_id=user_id,
        filename=file.filename,
        collection_id=collection_id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # 3. Process document (extract text and chunk)
    try:
        chunks = document_service.process_document(content, file.filename)
    except Exception as e:
        # If processing fails, delete the DB record and return error
        db.delete(new_doc)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
        
    # 4. Generate embeddings and save to ChromaDB
    try:
        embedding_service.add_chunks_to_collection(
            collection_name=chroma_collection_name,
            document_id=new_doc.id,
            chunks=chunks
        )
    except Exception as e:
        db.delete(new_doc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {str(e)}")
        
    return {
        "message": "Document processed successfully",
        "document_id": new_doc.id,
        "filename": file.filename,
        "chunks_created": len(chunks),
        "collection": chroma_collection_name
    }

@router.delete("/clear-default")
async def clear_default_collection(
    user_id: str = Depends(get_current_user_id)
):
    """Clear all documents from the default collection"""
    embedding_service.delete_collection("rag_collection")
    return {"message": "Default collection cleared"}
