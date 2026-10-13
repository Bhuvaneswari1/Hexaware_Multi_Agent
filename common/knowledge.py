"""Chroma retrieval: lexical demo embeddings or live semantic embeddings."""
import hashlib
import math
import os
import re
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from common.data import rows


class LocalHashEmbeddings(Embeddings):
    """Stable bag-of-words vectors, NOT a pretrained semantic embedding model."""
    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * 256
        for word in re.findall(r'\w+', text.lower()):
            index = int(hashlib.sha256(word.encode()).hexdigest()[:8], 16) % 256
            vector[index] += 1
        norm = math.sqrt(sum(v * v for v in vector)) or 1
        return [v / norm for v in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]


class KnowledgeBase:
    def __init__(self, folder):
        from langchain_chroma import Chroma
        backend = os.getenv('EMBEDDING_BACKEND', 'local_hash')
        if backend == 'openai':
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(model=os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small'))
        elif backend == 'local_hash':
            embeddings = LocalHashEmbeddings()
        else:
            raise ValueError('EMBEDDING_BACKEND must be local_hash or openai')
        self.backend = backend
        # Separate index when switching vector dimensions or embedding model.
        identity = backend + os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
        suffix = hashlib.sha256(identity.encode()).hexdigest()[:8]
        self.db = Chroma(collection_name='support_knowledge',
                         embedding_function=embeddings,
                         persist_directory=str(folder / ('chroma_' + suffix)))
        records = rows('knowledge.csv')
        self.db.add_documents([Document(page_content=r['text'],
                              metadata={'doc_id': r['doc_id'], 'topic': r['topic']}) for r in records],
                              ids=[r['doc_id'] for r in records])

    def search(self, query: str) -> list[dict]:
        return [{'doc_id': d.metadata['doc_id'], 'text': d.page_content}
                for d in self.db.as_retriever(search_kwargs={'k': 2}).invoke(query)]
