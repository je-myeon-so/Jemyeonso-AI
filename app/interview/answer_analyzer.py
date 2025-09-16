import json
import re
from app.interview.prompt_loader import load_prompt
from app.core.llm_utils import call_llm
from app.core.wikipedia_service import WikipediaService
from app.interview.scoring_engine import calculate_enhanced_score

MAX_CONCEPTS_TO_PROCESS = 3
WIKIPEDIA_EXTRACT_TRUNCATE_LENGTH = 300


def extract_technical_concepts(answer: str, jobtype: str) -> list:
    try:
        prompt_template = load_prompt("concept_extraction.txt")
        prompt = prompt_template.format(answer=answer, job_type=jobtype)
    except FileNotFoundError:
        return []
    except (AttributeError, KeyError, TypeError):
        return []

    try:
        response = call_llm(
            prompt=prompt,
            temperature=0.1,
            max_tokens=200,
            system_role="당신은 기술 면접 전문가입니다. 답변에서 검증 가능한 기술 개념을 정확히 추출합니다."
        )
        concepts = json.loads(response.strip())
        return concepts if isinstance(concepts, list) else []
    except (json.JSONDecodeError, ValueError, TypeError, Exception):
        return []


def get_wikipedia_context(concepts: list) -> str:
    if not concepts:
        return ""

    wikipedia_service = WikipediaService()
    fact_context = "\n\n**기술적 정확성 검증을 위한 참고 정보:**\n"

    for concept in concepts[:MAX_CONCEPTS_TO_PROCESS]:
        wiki_data = wikipedia_service.get_concept_summary(concept)
        if not wiki_data:
            search_title = wikipedia_service.search_concept(concept)
            if search_title:
                wiki_data = wikipedia_service.get_concept_summary(search_title)

        if wiki_data and wiki_data.get("extract"):
            extract = wiki_data["extract"][:WIKIPEDIA_EXTRACT_TRUNCATE_LENGTH]
            fact_context += f"- **{concept}**: {extract}...\n"

    fact_context += "\n위 정보를 참고하여 답변의 기술적 정확성도 함께 평가해주세요. 잘못된 설명이 있다면 '전문성 부족' 유형으로 분류하고 정확한 정보를 제공해주세요.\n"
    return fact_context


def analyze_answer(question: str, answer: str, jobtype: str, level: str, category: str) -> dict:
    """
    Enhanced answer analysis with comprehensive scoring
    
    Returns:
        dict: {
            "score": int (0-100),
            "analysis": [{"errorText": str, "errorType": str, "feedback": str, "suggestion": str}]
        }
    """
    # Extract technical concepts and get Wikipedia context (existing functionality)
    technical_concepts = extract_technical_concepts(answer, jobtype)
    wikipedia_context = get_wikipedia_context(technical_concepts)

    # Load enhanced analysis prompt
    try:
        prompt_template = load_prompt("analysis.txt")
        formatted_prompt = prompt_template.format(
            question=question.strip(),
            text=answer.strip(),
            jobtype=jobtype,
            level=level,
            category=category
        )
        prompt = formatted_prompt + wikipedia_context
        
        # Call LLM for enhanced analysis with scoring
        llm_response = call_llm(
            prompt=prompt,
            temperature=0.3,
            max_tokens=800,  # Increased for more detailed analysis
            system_role="당신은 경험이 풍부한 면접관입니다. 지원자의 답변을 종합적으로 평가하고 0-100점 사이의 점수와 구체적인 피드백을 제공합니다."
        )
        
        # Parse LLM response for score and analysis
        full_response = llm_response.strip()
        json_match = re.search(r'\{[\s\S]*\}', full_response)
        
        if json_match:
            try:
                parsed_result = json.loads(json_match.group(0))
                
                # Validate and extract score
                score = parsed_result.get("score", 50)
                if not isinstance(score, int):
                    score = int(score) if str(score).isdigit() else 50
                score = max(0, min(100, score))  # Ensure 0-100 range
                
                # Validate and extract analysis
                analysis = parsed_result.get("analysis", [])
                if not isinstance(analysis, list):
                    analysis = []
                
                # Validate each analysis item
                validated_analysis = []
                for item in analysis:
                    if (isinstance(item, dict) and 
                        all(key in item for key in ["errorText", "errorType", "feedback", "suggestion"])):
                        validated_analysis.append(item)
                
                return {
                    "score": score,
                    "analysis": validated_analysis
                }
                
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
                print(f"❌ JSON 파싱 오류: {e}")
                # Fall back to enhanced scoring engine
                score, analysis = calculate_enhanced_score(question, answer, full_response)
                return {"score": score, "analysis": analysis}
        
        else:
            print("❌ JSON 형식 응답 없음")
            # Fall back to enhanced scoring engine
            score, analysis = calculate_enhanced_score(question, answer, full_response)
            return {"score": score, "analysis": analysis}
            
    except (ConnectionError, TimeoutError, ValueError) as e:
        print(f"❌ LLM 호출 실패: {e}")
        # Fall back to enhanced scoring engine for resilience
        score, analysis = calculate_enhanced_score(question, answer)
        return {"score": score, "analysis": analysis}
    
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        # Final fallback
        score, analysis = calculate_enhanced_score(question, answer)
        return {"score": score, "analysis": analysis}
