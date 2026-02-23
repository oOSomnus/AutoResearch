"""
QA Mode Module - Interactive Q&A mode using RAG for analyzed papers.
"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings


@dataclass
class QAResult:
    """Result of a Q&A query."""
    question: str
    answer: str
    source_sections: List[str]
    confidence: float


class QAMode:
    """Interactive Q&A mode for analyzed papers."""

    def __init__(self, persist_directory: str = ".chroma_db"):
        """
        Initialize the Q&A mode.

        Args:
            persist_directory: Directory for ChromaDB persistence
        """
        self.persist_directory = persist_directory
        self._client: Optional[chromadb.ClientAPI] = None
        self._embeddings: Optional[OpenAIEmbeddings] = None
        self._collection_name = "paper_analysis"
        self._current_paper_id: Optional[str] = None

    def _get_client(self) -> chromadb.ClientAPI:
        """Get or create ChromaDB client."""
        if self._client is None:
            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        return self._client

    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Get or create embeddings instance."""
        if self._embeddings is None:
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.getenv("OPENAI_API_KEY")
            api_base = os.getenv("OPENAI_API_BASE")

            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")

            self._embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                openai_api_base=api_base
            )
        return self._embeddings

    def index_paper(self, state: Dict[str, Any]) -> str:
        """
        Index an analyzed paper for Q&A.

        Args:
            state: Analysis state with all sections

        Returns:
            Paper ID for the indexed paper
        """
        client = self._get_client()
        embeddings = self._get_embeddings()

        # Generate paper ID
        paper_id = state.get("source", "")
        if paper_id.startswith(("http://", "https://")):
            import hashlib
            paper_id = hashlib.md5(paper_id.encode()).hexdigest()

        self._current_paper_id = paper_id

        # Get or create collection
        try:
            collection = client.get_collection(
                name=self._collection_name,
                embedding_function=embeddings
            )
        except chromadb.errors.InvalidCollectionException:
            collection = client.create_collection(
                name=self._collection_name,
                embedding_function=embeddings
            )

        # Prepare documents for indexing
        sections = []

        # Background
        if state.get("background"):
            sections.append({
                "id": f"{paper_id}_background",
                "document": state["background"],
                "metadata": {
                    "paper_id": paper_id,
                    "section": "background",
                    "title": state.get("title", "")
                }
            })

        # Innovation
        if state.get("innovation"):
            sections.append({
                "id": f"{paper_id}_innovation",
                "document": state["innovation"],
                "metadata": {
                    "paper_id": paper_id,
                    "section": "innovation",
                    "title": state.get("title", "")
                }
            })

        # Results
        if state.get("results"):
            sections.append({
                "id": f"{paper_id}_results",
                "document": state["results"],
                "metadata": {
                    "paper_id": paper_id,
                    "section": "results",
                    "title": state.get("title", "")
                }
            })

        # Methodology
        if state.get("methodology"):
            sections.append({
                "id": f"{paper_id}_methodology",
                "document": state["methodology"],
                "metadata": {
                    "paper_id": paper_id,
                    "section": "methodology",
                    "title": state.get("title", "")
                }
            })

        # Related Work
        if state.get("related_work"):
            sections.append({
                "id": f"{paper_id}_related_work",
                "document": state["related_work"],
                "metadata": {
                    "paper_id": paper_id,
                    "section": "related_work",
                    "title": state.get("title", "")
                }
            })

        # Limitations
        if state.get("limitations"):
            sections.append({
                "id": f"{paper_id}_limitations",
                "document": state["limitations"],
                "metadata": {
                    "paper_id": paper_id,
                    "section": "limitations",
                    "title": state.get("title", "")
                }
            })

        # Add documents to collection
        if sections:
            ids = [s["id"] for s in sections]
            documents = [s["document"] for s in sections]
            metadatas = [s["metadata"] for s in sections]

            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

        return paper_id

    def query(self, question: str, paper_id: Optional[str] = None,
             n_results: int = 3) -> QAResult:
        """
        Query the indexed paper with a question.

        Args:
            question: The question to ask
            paper_id: Paper ID to query (uses current if None)
            n_results: Number of relevant sections to retrieve

        Returns:
            QAResult with answer and source sections
        """
        client = self._get_client()
        embeddings = self._get_embeddings()

        target_paper_id = paper_id or self._current_paper_id
        if not target_paper_id:
            raise ValueError("No paper indexed. Please index a paper first.")

        # Get collection
        collection = client.get_collection(
            name=self._collection_name,
            embedding_function=embeddings
        )

        # Query collection
        results = collection.query(
            query_texts=[question],
            where={"paper_id": target_paper_id},
            n_results=n_results
        )

        if not results or not results["documents"] or not results["documents"][0]:
            return QAResult(
                question=question,
                answer="未找到相关内容。请确保论文已正确索引。",
                source_sections=[],
                confidence=0.0
            )

        # Get relevant documents
        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []

        # Generate answer using LLM
        context = "\n\n".join(documents)
        answer = self._generate_answer(question, context)

        # Extract section names
        source_sections = [m.get("section", "unknown") for m in metadatas] if metadatas else []

        # Calculate confidence (inverse of distance)
        confidence = 1.0 - min(distances[0], 1.0) if distances else 0.5

        return QAResult(
            question=question,
            answer=answer,
            source_sections=source_sections,
            confidence=confidence
        )

    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using LLM.

        Args:
            question: The user's question
            context: Relevant context from the paper

        Returns:
            Generated answer
        """
        from langchain_openai import ChatOpenAI
        from dotenv import load_dotenv

        load_dotenv()

        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("MODEL_NAME", "gpt-4")

        llm = ChatOpenAI(
            openai_api_base=api_base,
            openai_api_key=api_key,
            model=model_name,
            temperature=0.3
        )

        prompt = f"""你是一个论文阅读助手。请根据以下论文分析内容回答用户的问题。

论文分析内容：
{context}

用户问题：{question}

要求：
1. 基于提供的论文内容回答问题
2. 如果内容中没有相关信息，如实说明
3. 用简单易懂的语言解释
4. 如果问题涉及具体数据或细节，尽量准确引用

请直接回答问题，不要输出其他内容。
"""

        response = llm.invoke(prompt)
        return response.content.strip()

    def clear_paper(self, paper_id: Optional[str] = None) -> None:
        """
        Clear indexed data for a paper.

        Args:
            paper_id: Paper ID to clear (uses current if None)
        """
        client = self._get_client()
        embeddings = self._get_embeddings()

        target_paper_id = paper_id or self._current_paper_id
        if not target_paper_id:
            return

        try:
            collection = client.get_collection(
                name=self._collection_name,
                embedding_function=embeddings
            )

            # Delete all documents for this paper
            collection.delete(
                where={"paper_id": target_paper_id}
            )
        except chromadb.errors.InvalidCollectionException:
            pass

    def list_indexed_papers(self) -> List[Dict[str, Any]]:
        """
        List all indexed papers.

        Returns:
            List of paper information dictionaries
        """
        client = self._get_client()
        embeddings = self._get_embeddings()

        try:
            collection = client.get_collection(
                name=self._collection_name,
                embedding_function=embeddings
            )

            # Get all documents and group by paper_id
            results = collection.get()
            papers = {}

            for metadata in results.get("metadatas", []):
                paper_id = metadata.get("paper_id")
                title = metadata.get("title", "未知")

                if paper_id and paper_id not in papers:
                    papers[paper_id] = {
                        "paper_id": paper_id,
                        "title": title,
                        "sections": []
                    }

                if paper_id:
                    section = metadata.get("section")
                    if section and section not in papers[paper_id]["sections"]:
                        papers[paper_id]["sections"].append(section)

            return list(papers.values())

        except chromadb.errors.InvalidCollectionException:
            return []


def interactive_qa_loop(paper_id: str) -> None:
    """
    Run interactive Q&A loop for a paper.

    Args:
        paper_id: ID of the indexed paper
    """
    qa = QAMode()
    qa._current_paper_id = paper_id

    print("\n" + "=" * 60)
    print("💬 问答模式 (输入 'q' 退出)")
    print("=" * 60)

    while True:
        question = input("\n请输入问题: ").strip()

        if question.lower() in ['q', 'quit', 'exit']:
            print("👋 退出问答模式")
            break

        if not question:
            continue

        try:
            result = qa.query(question, paper_id)
            print(f"\n回答: {result.answer}")
            if result.source_sections:
                print(f"来源: {', '.join(result.source_sections)}")
        except Exception as e:
            print(f"\n❌ 查询失败: {e}")