"""
Motor de Evaluación Principal - SSEAR
Integra análisis semántico, léxico y conceptual con ponderaciones configurables
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
import json

import config
from semantic_analyzer import SemanticAnalyzer
from lexical_analyzer import LexicalAnalyzer
from concept_analyzer import ConceptAnalyzer
from utils import normalize_text, validate_input

logger = logging.getLogger(__name__)


class EvaluationCache:
    """Caché simple en memoria para evaluaciones"""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []

    def get_key(self, reference: str, student: str) -> str:
        """Genera clave única para una evaluación"""
        combined = f"{reference.lower().strip()}||{student.lower().strip()}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, reference: str, student: str) -> Optional[Dict]:
        """Obtiene resultado del caché"""
        key = self.get_key(reference, student)
        return self.cache.get(key)

    def set(self, reference: str, student: str, result: Dict) -> None:
        """Guarda resultado en caché"""
        key = self.get_key(reference, student)
        if len(self.cache) >= self.max_size and key not in self.cache:
            if self.access_order:
                oldest = self.access_order.pop(0)
                self.cache.pop(oldest, None)
        self.cache[key] = result
        if key not in self.access_order:
            self.access_order.append(key)

    def clear(self):
        """Limpia el caché"""
        self.cache.clear()
        self.access_order.clear()

    def stats(self) -> Dict:
        return {'size': len(self.cache), 'max_size': self.max_size}


class EvaluationEngine:
    """Motor principal de evaluación integrado"""

    def __init__(self):
        logger.info("Inicializando motor de evaluación...")

        self.semantic_analyzer = SemanticAnalyzer()
        self.lexical_analyzer  = LexicalAnalyzer()
        self.concept_analyzer  = ConceptAnalyzer()

        # Leer ponderaciones desde config
        self.semantic_weight = config.SEMANTIC_WEIGHT
        self.lexical_weight  = config.LEXICAL_WEIGHT

        self.cache = EvaluationCache(max_size=config.CACHE_SIZE) if config.ENABLE_CACHE else None

        logger.info(f"Motor iniciado - Ponderaciones: Semántico {self.semantic_weight}, Léxico {self.lexical_weight}")

    def evaluate(self, question: str, reference_answer: str, student_answer: str,
                 context: str = "", use_cache: bool = True) -> Dict:
        """Ejecuta el pipeline completo de evaluación"""

        timestamp = datetime.now().isoformat()
        logger.info("Iniciando evaluación...")

        # Validar entrada
        error_msg = validate_input(reference_answer, student_answer, question)
        if error_msg:
            return self._error_result(error_msg, timestamp)

        # Revisar caché
        if use_cache and self.cache:
            cached = self.cache.get(reference_answer, student_answer)
            if cached:
                cached['cached'] = True
                logger.info("Resultado obtenido del caché")
                return cached

        # 1. Análisis Semántico
        logger.debug("Ejecutando análisis semántico...")
        semantic_results = self.semantic_analyzer.analyze(reference_answer, student_answer)
        semantic_score   = semantic_results.get('similarity', 0.0)

        # 2. Análisis Léxico
        logger.debug("Ejecutando análisis léxico...")
        lexical_results = self.lexical_analyzer.analyze(reference_answer, student_answer)
        lexical_score   = lexical_results.get('similarity', 0.0)

        # 3. Análisis de Conceptos
        logger.debug("Ejecutando análisis de conceptos...")
        concept_results = self.concept_analyzer.analyze(question, reference_answer, student_answer)
        concept_score   = concept_results.get('similarity', 0.0)

        # 4. Puntuación final
        final_score = (semantic_score * self.semantic_weight) + (lexical_score * self.lexical_weight)
        final_score = max(0.0, min(1.0, final_score))

        # 5. Calificación
        grade      = self._calculate_grade(final_score)
        percentage = round(final_score * 100, 2)

        # 6. Extraer términos léxicos para metadata
        matched_terms = lexical_results.get('matched_terms', [])
        missing_terms = lexical_results.get('missing_terms', [])
        extra_terms   = lexical_results.get('extra_terms', [])

        ref_words = len(reference_answer.split())
        stu_words = len(student_answer.split())

        scores = {
            'semantic':   round(semantic_score, 4),
            'lexical':    round(lexical_score, 4),
            'concept':    round(concept_score, 4),
            'final':      round(final_score, 4),
            'overall':    percentage,         # Alias para compatibilidad
            'percentage': percentage,
            'grade':      grade
        }

        result = {
            'cached':    False,
            'timestamp': timestamp,
            'scores':    scores,
            'analysis': {
                'semantic': semantic_results,
                'lexical':  lexical_results,
                'concept':  concept_results
            },
            'metadata': {
                'reference_words': ref_words,
                'student_words':   stu_words,
                'reference_length': len(reference_answer),
                'student_length':   len(student_answer),
                'question_length':  len(question),
                'has_context':      bool(context.strip()),
                'matched_terms':    matched_terms[:20],
                'missing_terms':    missing_terms[:20],
                'extra_terms':      extra_terms[:20],
                'term_coverage':    f"{len(matched_terms)}/{len(matched_terms) + len(missing_terms)}"
            },
            'weights': {
                'semantic': self.semantic_weight,
                'lexical':  self.lexical_weight
            }
        }

        logger.info(f"Evaluación completada - Score: {final_score:.4f}, Grado: {grade}")

        if use_cache and self.cache:
            self.cache.set(reference_answer, student_answer, result)

        return result

    def _calculate_grade(self, score: float) -> str:
        """Calcula la calificación basada en el puntaje"""
        thresholds = config.GRADE_THRESHOLDS
        if score >= thresholds.get('A', 0.85): return 'A'
        if score >= thresholds.get('B', 0.70): return 'B'
        if score >= thresholds.get('C', 0.55): return 'C'
        if score >= thresholds.get('D', 0.40): return 'D'
        return 'F'

    def _error_result(self, message: str, timestamp: str) -> Dict:
        return {
            'error':     message,
            'timestamp': timestamp,
            'cached':    False,
            'scores': {
                'semantic': 0, 'lexical': 0, 'concept': 0,
                'final': 0, 'overall': 0, 'percentage': 0, 'grade': 'F'
            },
            'analysis': {},
            'metadata': {
                'reference_words': 0, 'student_words': 0,
                'matched_terms': [], 'missing_terms': [], 'extra_terms': [],
                'term_coverage': '0/0'
            }
        }

    def get_cache_stats(self) -> Dict:
        return self.cache.stats() if self.cache else {'size': 0, 'max_size': 0}

    def clear_cache(self):
        if self.cache:
            self.cache.clear()
            logger.info("Caché limpiado")