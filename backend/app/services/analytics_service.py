from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.database import Query, Document, Message, User

class AnalyticsService:
    """Track and analyze system usage"""
    
    @staticmethod
    def get_user_stats(user_id: str, db: Session, days: int = 30) -> dict:
        """Get user statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Document count
        doc_count = db.query(func.count(Document.id)).filter(
            Document.user_id == user_id
        ).scalar()
        
        # Query count
        query_count = db.query(func.count(Query.id)).filter(
            Query.created_at >= start_date
        ).scalar()
        
        # Average response time
        avg_response_time = db.query(func.avg(Query.response_time)).filter(
            Query.created_at >= start_date
        ).scalar()
        
        # Message count
        message_count = db.query(func.count(Message.id)).filter(
            Message.created_at >= start_date
        ).scalar()
        
        return {
            "documents_uploaded": doc_count,
            "total_queries": query_count,
            "average_response_time_ms": float(avg_response_time) if avg_response_time else 0,
            "total_conversations": message_count,
            "period_days": days
        }
    
    @staticmethod
    def get_system_stats(db: Session) -> dict:
        """Get system-wide statistics"""
        total_users = db.query(func.count(User.id)).scalar()
        total_documents = db.query(func.count(Document.id)).scalar()
        total_queries = db.query(func.count(Query.id)).scalar()
        
        # Average response time across system
        avg_response_time = db.query(func.avg(Query.response_time)).scalar()
        
        return {
            "total_users": total_users,
            "total_documents": total_documents,
            "total_queries": total_queries,
            "average_response_time_ms": float(avg_response_time) if avg_response_time else 0
        }
    
    @staticmethod
    def log_query(db: Session, document_id: str, query_text: str, results_count: int, response_time: float):
        """Log a query for analytics"""
        query = Query(
            document_id=document_id,
            query_text=query_text,
            results_count=results_count,
            response_time=response_time
        )
        db.add(query)
        db.commit()
