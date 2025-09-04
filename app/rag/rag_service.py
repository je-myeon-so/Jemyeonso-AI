from __future__ import annotations

import os
import logging
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.runnables import Runnable

# HuggingFace 임베딩 관련
from langchain_huggingface import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CULTURE_URLS = [
    {
        "company": "당근마켓",
        "url": "https://medium.com/daangn/%EB%8B%B9%EA%B7%BC%EB%A7%88%EC%BC%93-it-%EA%B0%9C%EB%B0%9C-%ED%98%91%EC%97%85-%EC%9D%B4%EC%95%BC%EA%B8%B0-%EA%B0%9C%EB%B0%9C%EC%9E%90-%EB%94%94%EC%9E%90%EC%9D%B4%EB%84%88-pm-fff69de54015"
    },
    {
        "company": "우아한형제들(배달의민족)",
        "url": "https://techblog.woowahan.com/14671/"
    },
    {
        "company": "우아한형제들(배달의민족)",
        "url": "https://techblog.woowahan.com/9059/"
    },
    {
        "company": "토스",
        "url": "https://toss.im/career/article/culture-evangelist-session?utm_source=toss_careerpage&utm_medium=banner&utm_campaign=2311_cemeetup"
    },
]

def _scrape_text_from_url(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "utf-8, iso-8859-1;q=0.5"
        }
        resp = requests.get(url, timeout=10, headers=headers)
        resp.raise_for_status()

        # 인코딩 결정: Header > charset-normalizer > apparent_encoding > utf-8
        encoding = resp.encoding
        if not encoding or encoding.lower() in ("iso-8859-1", "ascii"):
            try:
                from charset_normalizer import from_bytes
                best = from_bytes(resp.content).best()
                if best and best.encoding:
                    encoding = best.encoding
                else:
                    encoding = resp.apparent_encoding or "utf-8"
            except Exception:
                encoding = resp.apparent_encoding or "utf-8"

        html = resp.content.decode(encoding, errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        # 주요 본문 추출 
        # 우선 article/main/body에서 p 태그 텍스트를 모두 합침
        candidates = soup.find_all(['article', 'main', 'body'])
        text = ""
        for c in candidates:
            ps = c.find_all('p')
            text += "\n".join([p.get_text(strip=True) for p in ps])
        if not text:
            # fallback: 모든 p 태그
            text = "\n".join([p.get_text(strip=True) for p in soup.find_all('p')])
        return text.strip()
    except Exception as e:
        logger.error(f"[스크래핑 실패] {url}: {e}")
        return ""

def _format_docs(documents: List[Document]) -> str:
    contents = [doc.page_content for doc in documents if doc.page_content]
    return "\n\n".join(contents)

class RagService:
    """
    HuggingFace 임베딩 기반 RAG 파이프라인 (임시 Chroma DB)
    """
    TEMP_DB_DIR: str = "./chroma_db_temp"
    EMBED_MODEL_NAME: str = "intfloat/multilingual-e5-small"

    def __init__(self) -> None:
        self.embedding_model: Optional[HuggingFaceEmbeddings] = None
        self.vector_store: Optional[Chroma] = None
        self.chain: Optional[Runnable] = None
        self.is_initialized: bool = False
        self.retriever = None

    def initialize(self) -> None:
        if self.is_initialized:
            logger.info("RagService is already initialized. Skipping re-initialization.")
            return
        logger.info("Initializing RagService with HuggingFace embedding and temp Chroma DB...")
        try:
            # 1. HuggingFace 임베딩 모델 로드
            self.embedding_model = HuggingFaceEmbeddings(model_name=self.EMBED_MODEL_NAME, model_kwargs={"device": "cpu"})

            # 2. 각 URL에서 본문 텍스트 스크래핑
            docs = []
            for entry in CULTURE_URLS:
                text = _scrape_text_from_url(entry["url"])
                if text:
                    docs.append(Document(page_content=text, metadata={"company": entry["company"], "url": entry["url"]}))
                else:
                    logger.warning(f"[본문 없음] {entry['company']} {entry['url']}")

            # 3. Chroma DB 임시 디렉토리 생성 및 벡터화
            if os.path.exists(self.TEMP_DB_DIR):
                import shutil
                shutil.rmtree(self.TEMP_DB_DIR)
            os.makedirs(self.TEMP_DB_DIR, exist_ok=True)
            self.vector_store = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding_model,
                persist_directory=self.TEMP_DB_DIR
            )

            # 4. Retriever 생성 (상위 k 문서)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

            self.is_initialized = True
            logger.info("RagService initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RagService: {e}", exc_info=True)
            raise

    def get_culturefit_context(self, resume_text: str) -> str:
        """
        이력서 텍스트를 임베딩하여 Chroma DB에서 가장 유사한 회사 문화 context를 반환
        """
        if not self.is_initialized:
            raise RuntimeError("RagService is not initialized. Call the 'initialize()' method at application startup.")
        if self.vector_store is None:
            raise RuntimeError("Vector store or retriever is not initialized.")
        relevant_docs = self.retriever.get_relevant_documents(resume_text)
        if not relevant_docs:
            return ""
        return _format_docs(relevant_docs)

rag_service = RagService()
