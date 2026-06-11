"""RAG (Retrieval-Augmented Generation) service for project"""

import re
import streamlit as st
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import requests
from typing import List, Dict, Any, Optional, Tuple
from services.ai_service import call_ollama
from config import CHROMA_DIR, ensure_dirs, OLLAMA_EMBEDDING_MODEL, OLLAMA_HOST, RAG_SEARCH_RESULTS


def trim_ai_response(text):
    """Trim AI response - keep only content after ...done thinking."""
    if not text:
        return text

    # Find ...done thinking. and return everything after it
    match = re.search(r'\.\.\.done thinking\.?\s*', text, re.IGNORECASE)
    if match:
        result = text[match.end():].strip()
        # If result is empty, try to find the actual answer line by line
        if not result:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.lower().startswith('thinking'):
                    return line
        return result

    # If no ...done thinking found, try to find the first non-thinking line
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.lower().startswith('thinking'):
            return line

    return text


class OllamaEmbeddingFunction(EmbeddingFunction):
    """Class for getting embeddings via Ollama API"""

    def __init__(
        self,
        model_name: str = None,
        host: str = None
    ):
        super().__init__()
        self.model_name = model_name or OLLAMA_EMBEDDING_MODEL
        self.host = host or OLLAMA_HOST

    def __call__(self, input: Documents) -> Embeddings:
        """Gets embeddings for a list of documents"""
        embeddings = []

        for text in input:
            if not text.startswith(("query:", "passage:")):
                text = f"passage: {text}"

            url = f"{self.host}/api/embeddings"
            payload = {"model": self.model_name, "prompt": text}

            try:
                response = requests.post(url, json=payload, timeout=60)
                if response.status_code == 200:
                    embedding = response.json().get('embedding', [])
                    if embedding:
                        embeddings.append(embedding)
                    else:
                        embeddings.append([0.0] * 1024)
                else:
                    embeddings.append([0.0] * 1024)
            except Exception as e:
                print(f"Error requesting Ollama: {e}")
                embeddings.append([0.0] * 1024)

        return embeddings


class ProjectRAG:
    """RAG system for project"""

    def __init__(self, project_id: int, project_name: str):
        """
        Initialize RAG system for project

        Args:
            project_id: Project ID
            project_name: Project name
        """
        self.project_id = project_id
        self.project_name = project_name
        self.client = None
        self.collection = None
        self.embedding_func = None
        self._initialized = False

    def init_chromadb(self) -> bool:
        """Initializes ChromaDB with Ollama embeddings"""
        try:
            ensure_dirs()
            self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))

            self.embedding_func = OllamaEmbeddingFunction()

            collection_name = f"project_{self.project_id}"

            try:
                self.collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_func
                )
                # Clear old data
                existing_ids = self.collection.get()['ids']
                if existing_ids:
                    self.collection.delete(ids=existing_ids)
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_func,
                    metadata={"project_name": self.project_name}
                )

            self._initialized = True
            return True

        except Exception as e:
            st.error(f"Error initializing ChromaDB: {e}")
            return False

    def collect_project_data(self, project: Dict[str, Any]) -> Tuple[List[str], List[Dict], List[str]]:
        """
        Collects ALL text project data for indexing

        Args:
            project: dictionary with project data

        Returns:
            tuple of (documents, metadata, ids)
        """
        documents = []
        metadatas = []
        ids = []
        doc_id = 0

        # ========== 1. PROJECT PASSPORT ==========
        passport_fields = [
            ('name', 'Project name'),
            ('goals', 'Project goals'),
            ('key_results', 'Key results'),
            ('problem', 'Project problem'),
            ('hypothesis', 'Project hypothesis'),
            ('success_criteria', 'Success criteria'),
            ('replaning', 'Replanning')
        ]

        for field, label in passport_fields:
            value = project.get(field)
            if value:
                documents.append(f"{label}: {value}")
                metadatas.append({"type": "passport", "field": field})
                ids.append(f"doc_{doc_id}")
                doc_id += 1

        # ========== 2. PROJECT SCOPE ==========
        scope_fields = [
            ('must_have', 'Must-have requirements'),
            ('nice_to_have', 'Nice-to-have requirements'),
            ('not_in_scope', 'What is not included in the project')
        ]

        for field, label in scope_fields:
            items = project.get(field, [])
            if items:
                documents.append(f"{label}: {', '.join(items)}")
                metadatas.append({"type": "scope", "field": field})
                ids.append(f"doc_{doc_id}")
                doc_id += 1

        # ========== 3. RISKS ==========
        risks = project.get('risks', [])
        for i, risk in enumerate(risks):
            text = (
                f"Risk {risk.get('impact', 'MEDIUM')}: {risk.get('description', '')}. "
                f"Impact on result: {risk.get('impact_on_result', '')}. "
                f"Impact on timeline: {risk.get('impact_on_timeline', '')}. "
                f"Mitigation plan: {risk.get('mitigation_plan', '')}"
            )
            documents.append(text)
            metadatas.append({
                "type": "risk",
                "index": i,
                "impact": risk.get('impact', 'MEDIUM')
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1

        # ========== 4. STAGES ==========
        stages = project.get('stages', [])
        for i, stage in enumerate(stages):
            text = (
                f"Stage: {stage.get('name', '')}. "
                f"Description: {stage.get('description', '')}. "
                f"Expected date: {stage.get('expected_date', '')}. "
                f"Status: {stage.get('status', '')}"
            )
            documents.append(text)
            metadatas.append({
                "type": "stage",
                "index": i,
                "status": stage.get('status', '')
            })
            ids.append(f"doc_{doc_id}")
            doc_id += 1

        # ========== 5. RACI MATRIX ==========
        raci = project.get('raci', [])
        for i, item in enumerate(raci):
            text = (
                f"RACI: Artifact '{item.get('artifact_name', '')}' - "
                f"Role '{item.get('role_name', '')}' - "
                f"Code '{item.get('raci_code', '')}'"
            )
            documents.append(text)
            metadatas.append({"type": "raci", "index": i})
            ids.append(f"doc_{doc_id}")
            doc_id += 1

        # ========== 6. TEAM ==========
        team = project.get('team', [])
        for i, member in enumerate(team):
            text = f"Team member: {member.get('name', '')} - Role: {member.get('role', '')}"
            documents.append(text)
            metadatas.append({"type": "team", "index": i})
            ids.append(f"doc_{doc_id}")
            doc_id += 1

        # ========== 7. COMMUNICATIONS ==========
        communications = project.get('communications', [])
        for i, comm in enumerate(communications):
            text = (
                f"Meeting: {comm.get('name', '')}. "
                f"Frequency: {comm.get('frequency', '')}. "
                f"Time: {comm.get('time', '')}. "
                f"Duration: {comm.get('duration', '')} min. "
                f"Location: {comm.get('location', '')}. "
                f"Link: {comm.get('link', '')}. "
                f"Description: {comm.get('description', '')}"
            )
            documents.append(text)
            metadatas.append({"type": "communication", "index": i})
            ids.append(f"doc_{doc_id}")
            doc_id += 1

        # ========== 8. ARTICLES ==========
        articles = project.get('articles', [])
        for i, article in enumerate(articles):
            text = f"Article: {article.get('title', '')}. Link: {article.get('url', '')}"
            documents.append(text)
            metadatas.append({"type": "article", "index": i})
            ids.append(f"doc_{doc_id}")
            doc_id += 1

        # ========== 9. TASKS ==========
        tasks = project.get('tasks', [])
        for i, task in enumerate(tasks):
            text = f"Task: {task.get('title', '')}. Description: {task.get('description', '')}. Status: {task.get('status', '')}"
            documents.append(text)
            metadatas.append({"type": "task", "index": i})
            ids.append(f"doc_{doc_id}")
            doc_id += 1

        # ========== 10. MEETINGS (AUDIO RECORDINGS) ==========
        recordings = project.get('audio_recordings', [])
        for i, recording in enumerate(recordings):
            transcript = recording.get('transcript', '')
            if transcript and len(transcript) > 100:
                documents.append(transcript)
                metadatas.append({
                    "type": "meeting",
                    "index": i,
                    "date": recording.get('recorded_date', ''),
                    "filename": recording.get('filename', '')
                })
                ids.append(f"doc_{doc_id}")
                doc_id += 1

        return documents, metadatas, ids

    def index_project(self, project: Dict[str, Any]) -> bool:
        """
        Indexes project in ChromaDB

        Args:
            project: dictionary with project data

        Returns:
            True if successful, False on error
        """
        if not self.init_chromadb():
            return False

        documents, metadatas, ids = self.collect_project_data(project)

        if not documents:
            st.warning("No data to index")
            return False

        try:
            # Add in batches of 100 for performance
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
            return True
        except Exception as e:
            st.error(f"Indexing error: {e}")
            return False

    def search(self, query: str, n_results: int = None) -> Optional[Dict]:
        """
        Search for relevant fragments

        Args:
            query: search query
            n_results: number of results

        Returns:
            search results or None
        """
        if not self.collection:
            return None

        if n_results is None:
            n_results = RAG_SEARCH_RESULTS

        query_with_prefix = f"query: {query}"

        results = self.collection.query(
            query_texts=[query_with_prefix],
            n_results=n_results
        )

        return results

    def ask_question(self, question: str) -> str:
        """
        Asks a question about the project using RAG

        Args:
            question: user question

        Returns:
            AI answer
        """
        results = self.search(question, n_results=RAG_SEARCH_RESULTS)

        if not results or not results['documents'] or not results['documents'][0]:
            prompt = f"""Answer the question about the project.

Question: {question}

If there is no information, say: "There is no information about this in the project data."

Answer:"""
            answer = call_ollama(prompt)
            return trim_ai_response(answer)

        # Build context with source references
        context_parts = self._build_context(results)
        context = "\n\n".join(context_parts)

        prompt = self._build_prompt(context, question)
        answer = call_ollama(prompt)
        return trim_ai_response(answer)

    def _build_context(self, results: Dict) -> List[str]:
        """
        Builds context from search results

        Args:
            results: search results

        Returns:
            list of context strings
        """
        context_parts = []

        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            source_type = meta.get('type', 'unknown')

            source_templates = {
                'meeting': lambda m: f"[Meeting {m.get('filename', '')} from {m.get('date', 'date unknown')}]: {doc}",
                'risk': lambda m: f"[Risk {m.get('impact', 'MEDIUM')}]: {doc}",
                'stage': lambda m: f"[Stage {m.get('status', '')}]: {doc}",
                'passport': lambda m: f"[Project passport - {m.get('field', '')}]: {doc}",
                'scope': lambda m: f"[Project scope - {m.get('field', '')}]: {doc}",
                'team': lambda: f"[Project team]: {doc}",
                'raci': lambda: f"[RACI matrix]: {doc}",
                'communication': lambda: f"[Communications]: {doc}",
                'article': lambda: f"[Article]: {doc}",
                'task': lambda: f"[Task]: {doc}"
            }

            if source_type in source_templates:
                if source_type in ['meeting', 'risk', 'stage', 'passport', 'scope']:
                    context_parts.append(source_templates[source_type](meta))
                else:
                    context_parts.append(source_templates[source_type]())
            else:
                context_parts.append(f"[Source]: {doc}")

        return context_parts

    def _build_prompt(self, context: str, question: str) -> str:
        """
        Builds prompt for AI

        Args:
            context: context
            question: user question

        Returns:
            ready prompt
        """
        return f"""You are a project manager assistant. Answer the question using only the information from the context.

CRITICAL INSTRUCTION: Do not include any thinking process, reasoning, or explanation. Do not use words like "Thinking...", "We need to...", "Let me...", "I will...". Start your answer directly with the answer.

CONTEXT:
{context}

QUESTION: {question}

RULES:
1. Answer only based on the provided context
2. If there is no information, say "There is no information about this in the provided data"
3. Indicate the source of information (Meeting, Passport, Risk, Stage, etc.)
4. Answer briefly and to the point

ANSWER:"""

    @property
    def is_initialized(self) -> bool:
        """Checks if RAG system is initialized"""
        return self._initialized


def render_rag_chat(project: Dict[str, Any]):
    """
    Displays RAG chat interface in Streamlit

    Args:
        project: dictionary with project data
    """
    st.markdown("## Project Q&A")
    st.caption(
        "Ask any question about the project. I will find the answer in documents, meetings and notes.")
    st.info("Tip: For best results, click 'Reindex project' first")

    # Initialize RAG
    if 'rag' not in st.session_state:
        st.session_state.rag = ProjectRAG(
            project.get('id'), project.get('name'))

    if not st.session_state.rag.is_initialized:
        with st.spinner("Indexing project (may take a while)..."):
            if st.session_state.rag.index_project(project):
                st.success("Project indexed!")
            else:
                st.error("Indexing error")

    # Chat history
    if 'rag_messages' not in st.session_state:
        st.session_state.rag_messages = []

    # Display history
    for msg in st.session_state.rag_messages:
        if msg['role'] == 'user':
            st.chat_message("user").write(msg['content'])
        else:
            st.chat_message("assistant").write(msg['content'])

    # Question input field
    question = st.chat_input("Ask a question about the project...")

    if question:
        st.session_state.rag_messages.append(
            {"role": "user", "content": question})
        st.chat_message("user").write(question)

        with st.spinner("Analyzing project..."):
            answer = st.session_state.rag.ask_question(question)

        st.session_state.rag_messages.append(
            {"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)

        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear history", width='stretch'):
            st.session_state.rag_messages = []
            st.rerun()
    with col2:
        if st.button("Reindex project", width='stretch'):
            with st.spinner("Reindexing project..."):
                st.session_state.rag.index_project(project)
            st.success("Project reindexed!")


def reset_rag_for_project(project_id: int) -> bool:
    """
    Resets RAG for project (deletes index)

    Args:
        project_id: Project ID

    Returns:
        True if successful, False on error
    """
    try:
        ensure_dirs()
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection_name = f"project_{project_id}"

        try:
            client.delete_collection(collection_name)
            return True
        except:
            # Collection doesn't exist - that's fine
            return True
    except Exception as e:
        print(f"Error resetting RAG: {e}")
        return False
