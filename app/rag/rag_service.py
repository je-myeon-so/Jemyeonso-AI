from __future__ import annotations

import os
import logging
from typing import List, Optional

from app.config import OPENAI_API_KEY, MODEL_NAME

# LangChain 구성 요소 임포트
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# --- 로거 설정 ---
# 애플리케이션 전반의 로깅 설정을 위해 기본 로거를 사용합니다.
# 실제 프로덕션 환경에서는 main.py 등에서 포맷과 레벨을 중앙 관리하는 것이 좋습니다.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _format_docs(documents: List[Document]) -> str:
    """
    Retrieved 문서 리스트를 하나의 컨텍스트 문자열로 포맷팅합니다.
    
    """
    contents = [doc.page_content for doc in documents if doc.page_content]
    return "\n\n".join(contents)


class RagService:
    """
    CultureFit 질문 생성 대상 RAG 파이프라인을 관리하는 싱글톤 서비스 클래스.

    """
    DEFAULT_PERSIST_DIR: str = "./chroma_db"

    def __init__(self) -> None:
        """RagService의 속성을 초기화합니다."""
        self.embedding_model: Optional[OpenAIEmbeddings] = None
        self.vector_store: Optional[Chroma] = None
        self.llm: Optional[ChatOpenAI] = None
        self.chain: Optional[Runnable] = None
        self.is_initialized: bool = False

    def initialize(self) -> None:
        """
        RAG 파이프라인에 필요한 모든 구성 요소를 초기화하고 체인을 구성합니다.
        이 메서드는 애플리케이션 시작 시(lifespan) 단 한 번만 호출되어야 합니다.
        """
        if self.is_initialized:
            logger.info("RagService is already initialized. Skipping re-initialization.")
            return

        logger.info("Initializing RagService...")
        try:
            # 1. OpenAI 임베딩 모델 초기화
            self.embedding_model = OpenAIEmbeddings(
                api_key=OPENAI_API_KEY,
                model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
            )

            # 2. Chroma Vector DB 로드
            persist_directory = os.getenv("CHROMA_PERSIST_DIR", self.DEFAULT_PERSIST_DIR)
            if not os.path.isdir(persist_directory):
                raise FileNotFoundError(
                    f"Chroma DB directory not found at '{persist_directory}'. "
                    "Please run 'scripts/build_vector_db.py' first."
                )
            
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embedding_model,
            )

            # 3. Retriever 생성 (상위 3개 문서 검색)
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

            # 4. ChatOpenAI LLM 초기화
            self.llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model=MODEL_NAME,
                temperature=0.3,
            )

            # 5. 프롬프트 템플릿 정의
            template = """당신은 지원자의 이력서와 회사의 문화 정보를 바탕으로, Culture Fit 면접 질문을 만드는 전문 면접관입니다.
제시된 '회사의 문화 정보'를 반드시 활용하여, 지원자의 경험이 해당 문화에 어떻게 적응할 수 있을지 연결 짓는 질문을 생성해야 합니다.

[회사의 문화 정보]
{context}

[지원자 이력서 내용]
{resume_text}

[질문]
위 정보를 바탕으로, 지원자의 경험과 회사 문화의 연관성을 파고드는 날카로운 질문 하나만 생성해주세요."""
            prompt = ChatPromptTemplate.from_template(template)

            # 6. LCEL을 사용한 RAG 체인 구성
            self.chain = (
                {
                    "context": retriever | _format_docs,
                    "resume_text": RunnablePassthrough(),
                }
                | prompt
                | self.llm
                | StrOutputParser()
            )

            self.is_initialized = True
            logger.info("RagService initialized successfully.")

        except Exception as e:
            logger.error(f"Failed to initialize RagService: {e}", exc_info=True)
            # 초기화 실패 시 애플리케이션이 시작되지 않도록 예외를 다시 발생시킵니다.
            raise

    def generate_culture_fit_question(self, resume_text: str) -> str:
        """
        초기화된 RAG 체인을 사용하여 Culture Fit 질문을 생성합니다.

        """
        if not self.is_initialized or not self.chain:
            raise RuntimeError(
                "RagService is not initialized. Call the 'initialize()' method at application startup."
            )
        
        logger.info("Generating culture fit question...")
        # 체인의 입력 타입은 'resume_text' 문자열 하나입니다.
        result = self.chain.invoke(resume_text)
        return result.strip()


# 싱글톤 인스턴스
rag_service = RagService()
