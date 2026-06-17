from pathlib import Path

from app.domain.document_context import DocumentContext
from app.domain.document_metadata import infer_document_type
from app.services.semantic_search_service import SemanticSearchService

class DocumentContextService:

    def __init__(self, semantic_search_service: SemanticSearchService):
        self._semantic_search = semantic_search_service

    def build_context(self, query: str, top_k: int | None = None) -> DocumentContext:
        search_result = self._semantic_search.search(query, top_k=top_k)
        metadata_entries = self._semantic_search.get_metadata_entries()
        documents: list[dict[str, object]] = []
        for hit in search_result.results:
            metadata = metadata_entries.get(hit.document)
            documents.append({
                'document_name': hit.document,
                'document_type': metadata.document_type if metadata else infer_document_type(hit.document),
                'file_extension': metadata.file_extension if metadata else Path(hit.document).suffix.lower(),
                'score': hit.score,
                'content': hit.content,
            })
        sources = list(dict.fromkeys(hit.document for hit in search_result.results))
        top_document = search_result.results[0].document if search_result.results else None
        total_matches = len(search_result.results)
        average_score = round(
            sum(hit.score for hit in search_result.results) / total_matches,
            2,
        ) if total_matches else 0.0
        context = self._build_context_text(documents)
        return DocumentContext(
            documents=documents,
            sources=sources,
            top_document=top_document,
            total_matches=total_matches,
            average_score=average_score,
            context=context,
        )

    @staticmethod
    def _build_context_text(documents: list[dict[str, object]]) -> str:
        sections: list[str] = []
        for item in documents:
            document_name = str(item['document_name'])
            score = item['score']
            content = str(item['content']).strip()
            sections.append(f'[{document_name}] (relevancia: {score})\n{content}')
        return '\n\n'.join(sections)
