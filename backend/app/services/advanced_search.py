from typing import List, Dict
from app.services.embedding_service import EmbeddingService

class AdvancedSearchService:
    """Advanced search capabilities"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    def hybrid_search(
        self,
        collection_name: str,
        query: str,
        keyword_filter: str = None,
        top_k: int = 5
    ) -> List[Dict]:
        """Hybrid search combining semantic and keyword search"""
        # Semantic search
        semantic_results = self.embedding_service.search(
            collection_name=collection_name,
            query=query,
            top_k=top_k * 2
        )
        
        # Keyword filtering
        if keyword_filter:
            semantic_results = [
                r for r in semantic_results
                if keyword_filter.lower() in r['text'].lower()
            ]
        
        return semantic_results[:top_k]
    
    def multi_query_search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """Generate multiple queries and combine results"""
        # Generate variations of the query
        queries = self._generate_query_variations(query)
        
        all_results = {}
        
        # Search with each variation
        for q in queries:
            results = self.embedding_service.search(
                collection_name=collection_name,
                query=q,
                top_k=top_k
            )
            
            for result in results:
                doc_id = result['id']
                if doc_id not in all_results:
                    all_results[doc_id] = result
                else:
                    # Update with higher similarity
                    if result['similarity'] > all_results[doc_id]['similarity']:
                        all_results[doc_id] = result
        
        # Convert to list and sort
        results_list = list(all_results.values())
        results_list.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results_list[:top_k]
    
    def _generate_query_variations(self, query: str) -> List[str]:
        """Generate variations of a query"""
        variations = [query]
        
        # Simple variations (could use more sophisticated NLP)
        if len(query.split()) > 1:
            words = query.split()
            # Add reverse order
            variations.append(" ".join(reversed(words)))
            # Add synonyms (simplified)
            variations.append(query.replace("what", "which").replace("how", "in what way"))
        
        return variations[:3]  # Limit to 3 variations
    
    def contextual_search(
        self,
        collection_name: str,
        query: str,
        context_window: int = 3,
        top_k: int = 5
    ) -> List[Dict]:
        """Search with contextual expansion"""
        # Get initial results
        results = self.embedding_service.search(
            collection_name=collection_name,
            query=query,
            top_k=top_k
        )
        
        # Expand with context from neighboring chunks
        expanded_results = []
        
        for result in results:
            expanded_text = result['text']
            
            # In real implementation, fetch neighboring chunks from DB
            # This is simplified version
            
            expanded_results.append({
                **result,
                'expanded_text': expanded_text,
                'context_window': context_window
            })
        
        return expanded_results
