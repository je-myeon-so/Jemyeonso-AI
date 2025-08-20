"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from pathlib import Path

# Load .env file automatically
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"⚠️ No .env file found at {env_file}")

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def app():
    """Create FastAPI app instance for testing"""
    from app.main import app
    return app


@pytest.fixture(scope="session")
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_wikipedia_service():
    """Mock Wikipedia service for testing"""
    with patch('app.core.wikipedia_service.WikipediaService') as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        
        # Default successful responses
        service_instance.get_concept_summary.return_value = {
            "title": "Test Concept",
            "extract": "This is a test concept for testing purposes",
            "url": "https://ko.wikipedia.org/wiki/Test_Concept"
        }
        service_instance.search_concept.return_value = "Test Concept"
        service_instance.clear_cache.return_value = None
        service_instance.get_cache_stats.return_value = {
            "concept_cache_size": 0,
            "search_cache_size": 0
        }
        
        yield service_instance


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    with patch('app.core.llm_utils.call_llm') as mock:
        mock.return_value = '{"score": 80, "feedback": "Good answer", "strengths": ["Clear"], "improvements": ["Detail"]}'
        yield mock


@pytest.fixture
def mock_database():
    """Mock database connections"""
    with patch('app.core.mysql_database.get_connection') as mock_db:
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        yield mock_connection


@pytest.fixture
def mock_s3_service():
    """Mock S3 service for testing"""
    with patch('app.core.s3_utils.boto3') as mock_boto3:
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.upload_fileobj.return_value = None
        yield mock_s3_client


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """
    김철수 (Kim Chul-su)
    소프트웨어 엔지니어
    
    연락처:
    - 이메일: kim.cs@example.com
    - 전화: 010-1234-5678
    - 주소: 서울시 강남구 테헤란로 123
    
    경력:
    - ABC 회사 (2020-2023): Python 백엔드 개발
    - XYZ 스타트업 (2018-2020): 풀스택 개발
    
    기술 스택:
    - Python, Django, FastAPI
    - PostgreSQL, Redis
    - Docker, AWS
    """


@pytest.fixture
def sample_pii_items():
    """Sample PII items for testing"""
    try:
        from app.resume.pii_detector import PIIItem, PIIType
        return [
            PIIItem(type=PIIType.EMAIL, value="kim.cs@example.com", start=30, end=48),
            PIIItem(type=PIIType.PHONE, value="010-1234-5678", start=55, end=68),
            PIIItem(type=PIIType.NAME, value="김철수", start=0, end=3)
        ]
    except ImportError:
        return []


@pytest.fixture
def sample_questions():
    """Sample interview questions for testing"""
    return [
        {
            "id": 1,
            "question": "Python의 GIL(Global Interpreter Lock)에 대해 설명해주세요.",
            "category": "기술",
            "level": "고급"
        },
        {
            "id": 2,
            "question": "Django와 FastAPI의 차이점은 무엇인가요?",
            "category": "기술",
            "level": "중급"
        },
        {
            "id": 3,
            "question": "팀에서 갈등이 생겼을 때 어떻게 해결하시겠습니까?",
            "category": "인성",
            "level": "초급"
        }
    ]


@pytest.fixture
def sample_analysis_result():
    """Sample answer analysis result for testing"""
    return {
        "score": 85,
        "feedback": "기술적 이해도가 높고 설명이 명확합니다. 구체적인 예시가 좋았습니다.",
        "strengths": [
            "정확한 기술적 설명",
            "구체적인 예시 제공",
            "명확한 논리 구조"
        ],
        "improvements": [
            "실무 경험 사례 추가",
            "성능 최적화 관점 언급"
        ],
        "category": "우수"
    }


@pytest.fixture
def mock_prompt_loader():
    """Mock prompt loader for testing"""
    with patch('app.interview.prompt_loader.load_prompt') as mock:
        mock.return_value = "Test prompt template with {variable}"
        yield mock


@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing"""
    from io import BytesIO
    return {
        "pdf_file": BytesIO(b"Mock PDF content"),
        "txt_file": BytesIO(b"Mock text content"),
        "invalid_file": BytesIO(b"Mock invalid content")
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    
    # Preserve real OpenAI key from .env
    real_openai_key = os.getenv("OPENAI_API_KEY")
    
    test_env = {
        "OPENAI_API_KEY": real_openai_key or "test_api_key_fallback",  # Use real key
        "MYSQL_HOST": "test_host",
        "MYSQL_USER": "test_user", 
        "MYSQL_PASSWORD": "test_password",
        "MYSQL_DATABASE": "test_db",
        "AWS_ACCESS_KEY_ID": "test_access_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret_key",
        "S3_BUCKET_NAME": "test_bucket"
    }
    
    # Set environment variables for testing
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)  # Backup original
        os.environ[key] = value
    
    yield
    
    # Restore original environment variables
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_session_id():
    """Generate mock session ID for testing"""
    import uuid
    return str(uuid.uuid4())


# Pytest hooks and configurations
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests") 
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add 'unit' marker to test files starting with 'test_'
        if "test_" in item.nodeid:
            if "api" not in item.nodeid and not any(mark.name == "integration" for mark in item.iter_markers()):
                item.add_marker(pytest.mark.unit)


# Mock external services globally
@pytest.fixture(autouse=True, scope="session")
def mock_external_services():
    """Mock external services to avoid real API calls during testing"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Mock successful HTTP responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": "mock_data"}
        mock_response.text = "mock response text"
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        yield {
            "get": mock_get,
            "post": mock_post
        }
