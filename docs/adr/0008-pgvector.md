# 0008 — pgvector over a dedicated vector database
**Date:** 2026-05-03
**Status:** Accepted

## Context
Notes, RAG document chunks, and semantic cache all need vector similarity search. Options: Pinecone, Weaviate, Qdrant, or pgvector in the existing Postgres instance.

## Decision
Use the `pgvector` Postgres extension. IVFFlat index for ANN search on `vector(1536)` columns. The same Postgres instance already runs all service schemas.

## Consequences
- No additional service to run, monitor, or pay for.
- IVFFlat is sufficient for <10M vectors at personal-project scale.
- Query performance degrades at 10M+ vectors — revisit then.
- Semantic cache hit rate logged in `llm.runs.cache_hit`; can evaluate effectiveness over time.
- Migration path: export embeddings to Qdrant/Pinecone if scale demands it.
