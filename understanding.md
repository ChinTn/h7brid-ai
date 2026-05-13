# UNDERSTANDING.md

# Deep Understanding of the Architecture

This document explains all major concepts and architectural ideas used in the project .

---

# 1. Initial Motivation

The project started from a practical issue:

Local coding models worked well for small prompts but became very slow and unreliable for repository-level reasoning.

Simple approaches such as:
- sending the full repository to the model
- increasing context blindly
- depending only on cloud APIs

quickly became inefficient.

This led to studying:
- repository retrieval
- orchestration systems
- graph traversal
- context management
- workload routing
- multi-file reasoning

---

# 2. Hybrid AI Systems

The architecture evolved into a hybrid inference system.

Instead of using one model for every task:

```text
Simple Tasks
↓
Local Model

Complex Tasks
↓
Cloud Model
```

This improved:
- latency
- efficiency
- scalability
- responsiveness

The idea is inspired by production AI orchestration systems where smaller models handle lightweight reasoning while larger models are reserved for expensive tasks.

---

# 3. Repository Indexing

Repository indexing became one of the first core systems.

Instead of rescanning files repeatedly:
- files are indexed once
- embeddings are cached
- repository metadata is stored

The index stores:
- file content
- embeddings
- hashes
- metadata

This significantly reduces repeated computation.

---

# 4. Embeddings

Embeddings are vector representations of text.

Instead of comparing raw text directly:

```text
"authentication logic"
```

gets converted into a numerical vector.

Embeddings allow:
- semantic comparison
- similarity search
- contextual matching

The project uses embeddings for:
- semantic retrieval
- repository similarity
- contextual ranking

---

# 5. Semantic Retrieval

The first retrieval system used cosine similarity between:
- prompt embeddings
- file embeddings

Architecture:

```text
Prompt
↓
Embedding
↓
Cosine Similarity
↓
Top-K Files
```

This improved retrieval quality over keyword matching.

However pure semantic retrieval introduced problems:
- retrieval drift
- irrelevant files
- missing architectural context
- weak dependency awareness

---

# 6. Graph-Based Retrieval

To improve retrieval quality, graph traversal was introduced.

Files became connected through:
- imports
- semantic similarity
- architectural relationships
- structural proximity

Architecture:

```text
Seed Files
↓
Graph Expansion
↓
Neighbour Discovery
↓
Context Expansion
```

This allowed retrieval to include:
- dependencies
- nearby architecture
- supporting implementation context

---

# 7. Weighted DFS Traversal

Graph traversal used weighted DFS expansion.

Each graph edge contained:
- similarity weights
- relationship strength

Traversal used:
- maximum depth
- neighbour limits
- score decay
- edge filtering

Purpose:
- avoid context explosion
- prioritize strong relationships
- expand intelligently

This introduced:
- graph scoring
- traversal prioritization
- weighted expansion

---

# 8. Retrieval Reranking

Simple retrieval often returned noisy or weak results.

To improve quality, reranking concepts were introduced.

Architecture:

```text
Semantic Retrieval
+
Graph Expansion
+
Reranking
```

The reranker prioritizes:
- stronger matches
- repository-critical files
- architecturally relevant context

This improves:
- retrieval precision
- contextual quality
- reasoning consistency

---

# 9. Context Building

The project introduced structured context building pipelines.

Instead of dumping raw files directly into prompts:

```text
Retrieved Files
↓
Context Builder
↓
Structured Prompt
↓
LLM
```

This reduced:
- token waste
- irrelevant context
- context overflow

---

# 10. Workload Classification

Different tasks require different reasoning depth.

Examples:

| Task | Complexity |
|---|---|
| explain a function | simple |
| summarize repo | medium |
| architecture review | complex |
| multi-file refactor | very complex |

This introduced:
- SIMPLE vs COMPLEX classification
- local/cloud reasoning concepts
- orchestration-based workload handling

At this stage:
- there was NO semantic routing
- there was NO analysis mode
- there were NO separated orchestration flows

The system still operated through a unified conversational pipeline.

---

# 11. Multi-File Patch Generation

Initially edits were single-file only.

This failed for repository-level reasoning.

The editing pipeline evolved into:

```text
Retrieved Files
↓
Repository-Aware Prompting
↓
Multi-File JSON Patch Generation
↓
Diff Rendering
↓
File Application
```

This introduced:
- coordinated repository editing
- multi-file reasoning
- repository-aware modifications

---

# 12. Repository Memory

The project introduced repository memory systems.

Instead of recomputing everything:
- embeddings are cached
- repository state is persisted
- indexing can become incremental

This improves:
- scalability
- latency
- efficiency

---

# 13. Debug Tracing

Tracing systems were introduced to understand orchestration flow.

The system tracks:
- retrieval stages
- pipeline flow
- orchestration decisions
- graph expansion stages

This improves:
- debugging
- observability
- architecture understanding

---

# 14. Sequential Retrieval Architecture

Before parallel retrieval experimentation, the architecture used sequential retrieval.

Pipeline:

```text
User Prompt
↓
Semantic Retrieval
↓
Top-K Relevant Files
↓
Graph Expansion
↓
Weighted DFS Traversal
↓
Reranking
↓
Context Builder
↓
Local or Cloud Model
```

The retrieval pipeline worked sequentially:
- semantic retrieval first
- graph expansion second
- reranking after traversal
- context assembly before inference

This became the final stable architecture before experimenting with parallel retrieval systems.

---

# 15. Major Engineering Learnings

The project revealed several important lessons:

- retrieval quality matters more than raw model size
- orchestration is harder than prompting
- graph traversal improves repository understanding
- context management is critical
- repository-wide reasoning is difficult
- multi-file editing is fragile
- retrieval strategy affects reasoning quality heavily
- workload estimation matters
- context expansion must be controlled

---

# 16. Overall Architectural Direction

The project gradually evolved from:

```text
simple chatbot
```

into:

```text
repository-aware AI orchestration prototype
```

Core architectural themes became:
- hybrid inference
- repository reasoning
- graph-aware retrieval
- orchestration pipelines
- semantic retrieval
- reranking systems
- context expansion
- multi-file intelligence

The project remains experimental but serves as an exploration of repository-level AI orchestration systems before parallel retrieval experimentation.