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
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CULTURE_URLS = [
    {
        "company": "당근마켓",
        "url": "https://medium.com/daangn/%EB%8B%B9%EA%B7%BC%EB%A7%88%EC%BC%93-it-%EA%B0%9C%EB%B0%9C-%ED%98%91%EC%97%85-%EC%9D%B4%EC%95%BC%EA%B8%B0-%EA%B0%9C%EB%B0%9C%EC%9E%90-%EB%94%94%EC%9E%90%EC%9D%B4%EB%84%88-pm-fff69de54015"
    },
    {
        "company": "뱅크샐러드",
        "url": "https://blog.banksalad.com/pnc/team-interview-engineer/"
    },
    {
        "company": "카카오뱅크",
        "url": "https://brunch.co.kr/@kakaobankplus/89"
    },
    {
        "company": "쿠팡",
        "url": "https://particleseoul.tistory.com/1315"
    },
    {
        "company": "배달의 민족",
        "url": "https://story.baemin.com/6444/"
    }
]

def direct_scraping(url: str) -> str:
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
        logger.warning(f"[직접 스크래핑 실패] {url}: {e}")
        return ""

def jina_reader_scraping(url: str) -> str:
    """Jina Reader API를 사용한 폴백 스크래핑"""
    try:
        jina_api_key = os.getenv('JINA_API_KEY')
        if not jina_api_key:
            logger.warning("JINA_API_KEY가 설정되지 않았습니다.")
            return ""

        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            "Authorization": f"Bearer {jina_api_key}",
            "Accept": "application/json"
        }

        resp = requests.get(jina_url, headers=headers, timeout=15)
        resp.raise_for_status()

        response_data = resp.json()

        # API 응답 구조에 맞게 data 객체 내부의 content를 추출
        data_object = response_data.get("data", {})
        content = data_object.get("content", "").strip()
        
        if content:
            logger.info(f"[Jina Reader 성공] {url}: {len(content)}자 추출")
            return content
        else:
            logger.warning(f"[Jina Reader 빈 응답] {url}")
            return ""
            
    except Exception as e:
        logger.error(f"[Jina Reader 실패] {url}: {e}")
        return ""

def scrape_text_from_url(url: str) -> str:
    """
    두 단계 스크래핑: 1차 직접 스크래핑 → 2차 Jina Reader 사용
    """
    # 1차: beautifulsoup4 사용
    text = direct_scraping(url)
    if len(text) > 100:  # 충분한 텍스트가 있으면
        logger.info(f"[직접 스크래핑 성공] {url}: {len(text)}자 추출")
        return text
    
    # 2차: Jina Reader 사용 (JS 렌더링, 봇 차단 우회)
    logger.info(f"[Jina Reader 폴백 시도] {url}")
    return jina_reader_scraping(url)

def format_docs(documents: List[Document]) -> str:
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
                text = scrape_text_from_url(entry["url"])
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
        return format_docs(relevant_docs)

rag_service = RagService()
