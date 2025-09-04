from typing import Dict, List, Tuple
import re
import json


class ScoringEngine:
    DIMENSION_WEIGHTS = {
        "relevance_accuracy": 0.25,      # 관련성 및 정확성
        "depth_reasoning": 0.20,         # 논리적 깊이  
        "structure_clarity": 0.20,       # 구조 및 명확성
        "communication_style": 0.15,     # 의사소통 스타일
        "creativity_originality": 0.10,  # 창의성 및 독창성
        "technical_expertise": 0.10      # 전문성
    }
    
    ERROR_TYPES = {
        "relevance": "관련성_부족",
        "structure": "구조_문제", 
        "communication": "의사소통_문제",
        "depth": "깊이_부족",
        "completeness": "완성도_부족",
        "professionalism": "전문성_부족"
    }
    
    def __init__(self):
        self.dimension_scores = {}
        self.feedback_items = []
    
    def calculate_overall_score(self, dimension_scores: Dict[str, int]) -> int:
        if not dimension_scores:
            return 0
            
        total_weighted_score = 0
        total_weight = 0
        
        for dimension, score in dimension_scores.items():
            if dimension in self.DIMENSION_WEIGHTS:
                weight = self.DIMENSION_WEIGHTS[dimension]
                total_weighted_score += score * weight
                total_weight += weight
        
        if total_weight > 0:
            final_score = int(round(total_weighted_score / total_weight))
            return max(0, min(100, final_score))  # Ensure 0-100 range
        
        return 0
    
    def analyze_response_quality(self, question: str, answer: str) -> Dict[str, int]:
        scores = {}
        
        answer_length = len(answer.strip())
        word_count = len(answer.split())
        
        scores["relevance_accuracy"] = self._score_relevance(question, answer)
        
        scores["structure_clarity"] = self._score_structure(answer, word_count)
        
        scores["communication_style"] = self._score_communication(answer)
        
        scores["depth_reasoning"] = self._score_depth(answer, word_count)
        
        scores["creativity_originality"] = self._score_creativity(answer)
        
        scores["technical_expertise"] = self._score_technical_expertise(answer)
        
        return scores
    
    def _score_relevance(self, question: str, answer: str) -> int:
        if not answer.strip():
            return 0
            
        q_words = set(question.lower().split())
        a_words = set(answer.lower().split())
        overlap = len(q_words.intersection(a_words))
        
        base_score = min(70, overlap * 15 + 40)
        
        word_count = len(answer.split())
        if word_count >= 10:
            base_score += 15
        if word_count >= 30:
            base_score += 10
        
        if word_count < 5:
            base_score = int(base_score * 0.5)
        
        return max(40, min(100, base_score))
    
    def _score_structure(self, answer: str, word_count: int) -> int:
        if not answer.strip():
            return 0
            
        base_score = 60
        
        if 10 <= word_count <= 200:
            base_score += 20
        elif word_count > 200:
            base_score += 15
            
        sentence_count = len(re.findall(r'[.!?]+', answer))
        if sentence_count >= 2:
            base_score += 10
        if sentence_count >= 4:
            base_score += 10
            
        if any(word in answer.lower() for word in ['예를 들어', '예시', '경험', '사례', '첫째', '둘째', '셋째']):
            base_score += 15
            
        return min(100, base_score)
    
    def _score_communication(self, answer: str) -> int:
        if not answer.strip():
            return 0
            
        base_score = 70
        
        word_count = len(answer.split())
        if word_count < 3:
            base_score -= 40
        elif word_count < 8:
            base_score -= 20
            
        professional_indicators = ['습니다', '였습니다', '하였습니다', '생각합니다', '있습니다', '됩니다']
        if any(indicator in answer for indicator in professional_indicators):
            base_score += 15
            
        if any(word in answer for word in ['따라서', '그러므로', '또한', '하지만', '그러나']):
            base_score += 10
            
        return min(100, max(30, base_score))
    
    def _score_depth(self, answer: str, word_count: int) -> int:
        if not answer.strip():
            return 0
            
        base_score = 50
        
        if word_count >= 15:
            base_score += 15
        if word_count >= 30:
            base_score += 15
        if word_count >= 60:
            base_score += 10
            
        reasoning_words = ['왜냐하면', '때문에', '따라서', '그러므로', '결과적으로', '분석', '특징', '장점', '단점']
        reasoning_count = sum(1 for word in reasoning_words if word in answer)
        base_score += min(20, reasoning_count * 8)
        
        if any(word in answer for word in ['예를 들어', '사례', '경험', '프로젝트']):
            base_score += 15
            
        return min(100, base_score)
    
    def _score_creativity(self, answer: str) -> int:
        if not answer.strip():
            return 0
            
        base_score = 50
        
        creative_words = ['아이디어', '창의', '새로운', '혁신', '독특한', '참신한']
        if any(word in answer for word in creative_words):
            base_score += 30
            
        return min(100, base_score)
    
    def _score_technical_expertise(self, answer: str) -> int:
        if not answer.strip():
            return 0
            
        base_score = 50
        
        technical_indicators = len(re.findall(r'[A-Z]{2,}', answer))  # Acronyms
        if technical_indicators > 0:
            base_score += min(30, technical_indicators * 10)
            
        return min(100, base_score)
    
    def extract_score_from_llm_response(self, llm_response: str) -> Tuple[int, List[Dict]]:
        try:
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                parsed = json.loads(json_match.group(0))
                score = int(parsed.get("score", 50))
                analysis = parsed.get("analysis", [])
                
                score = max(0, min(100, score))
                
                validated_analysis = []
                for item in analysis:
                    if isinstance(item, dict) and all(key in item for key in ["errorText", "errorType", "feedback", "suggestion"]):
                        validated_analysis.append(item)
                
                return score, validated_analysis
                
        except (json.JSONDecodeError, ValueError, KeyError, TypeError):
            pass
        
        score_patterns = [
            r'점수[:\s]*(\d+)',
            r'score[:\s]*(\d+)',
            r'(\d+)점',
            r'(\d+)/100',
            r'(\d+)%'
        ]
        
        for pattern in score_patterns:
            score_match = re.search(pattern, llm_response, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                # Handle percentage conversion
                if '%' in score_match.group(0) and score <= 100:
                    return max(0, min(100, score)), []
                elif score <= 100:
                    return max(0, min(100, score)), []
        
        return 50, []
    
    def create_fallback_analysis(self, question: str, answer: str, score: int) -> List[Dict]:

        analysis = []
        
        if not answer.strip():
            analysis.append({
                "errorText": "답변이 없습니다",
                "errorType": "완성도_부족",
                "feedback": "질문에 대한 답변을 제공하지 않았습니다",
                "suggestion": "질문을 다시 읽고 구체적인 답변을 작성해보세요"
            })
            return analysis
        
        word_count = len(answer.split())
        
        if word_count < 10:
            analysis.append({
                "errorText": answer[:50] + "..." if len(answer) > 50 else answer,
                "errorType": "깊이_부족", 
                "feedback": "답변이 너무 짧아 충분한 설명이 부족합니다",
                "suggestion": "더 자세한 설명과 구체적인 예시를 추가해보세요"
            })
        
        if score < 60:
            analysis.append({
                "errorText": "전반적인 답변 품질",
                "errorType": "구조_문제",
                "feedback": "답변의 전반적인 구성과 내용에 개선이 필요합니다",
                "suggestion": "질문의 핵심을 파악하고 논리적으로 답변을 구성해보세요"
            })
        
        return analysis


def calculate_enhanced_score(question: str, answer: str, llm_response: str = None) -> Tuple[int, List[Dict]]:
    engine = ScoringEngine()
    
    if llm_response:
        score, analysis = engine.extract_score_from_llm_response(llm_response)
        if score != 50 or '{"score":' in llm_response or '"score"' in llm_response:
            return score, analysis
    
    dimension_scores = engine.analyze_response_quality(question, answer)
    score = engine.calculate_overall_score(dimension_scores)
    analysis = engine.create_fallback_analysis(question, answer, score)
    
    return score, analysis
