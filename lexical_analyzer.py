"""
Analizador Léxico - SSEAR
Calcula similitud léxica, extrae palabras clave e identifica términos faltantes
"""

import re
import logging
import unicodedata
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

try:
    from nltk.stem.snowball import SnowballStemmer
    HAS_SNOWBALL = True
except Exception:
    HAS_SNOWBALL = False


class LexicalAnalyzer:
    """Analiza similitud léxica entre respuestas"""

    def __init__(self):
        self.stop_words: Set[str] = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'y', 'o', 'pero', 'que', 'de', 'del', 'al', 'en', 'por',
            'con', 'sin', 'para', 'se', 'es', 'su', 'sus', 'como',
            'más', 'muy', 'a', 'lo', 'le', 'les', 'este', 'esta',
            'estos', 'estas', 'ese', 'esa', 'esos', 'esas',
            'ser', 'estar', 'han', 'has', 'ha', 'he',
            'son', 'fue', 'era', 'hay', 'no', 'si', 'ya', 'también'
        }

        self.stemmer = None
        if HAS_SNOWBALL:
            try:
                self.stemmer = SnowballStemmer('spanish')
            except Exception as e:
                logger.warning(f"No se pudo cargar SnowballStemmer: {e}")

        logger.info("Analizador léxico inicializado")

    # ------------------------------------------------------------------ #
    # Normalización
    # ------------------------------------------------------------------ #

    def _normalize(self, text: str) -> str:
        """Normaliza texto: minúsculas, sin acentos ni puntuación"""
        text = text.lower()
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza y elimina stop words"""
        words = self._normalize(text).split()
        return [w for w in words if w not in self.stop_words and len(w) > 2]

    def _stem(self, word: str) -> str:
        """Aplica stemming"""
        if self.stemmer:
            try:
                return self.stemmer.stem(word)
            except Exception:
                pass
        return word

    def _extract_keywords(self, tokens: List[str]) -> List[str]:
        """Extrae palabras clave (tokens sin stop words)"""
        return [t for t in tokens if len(t) > 3]

    # ------------------------------------------------------------------ #
    # Cálculo de similitudes
    # ------------------------------------------------------------------ #

    def _calculate_similarity(self, ref_tokens: List[str], stu_tokens: List[str]) -> float:
        """Similitud de Jaccard sobre tokens"""
        ref_set = set(ref_tokens)
        stu_set = set(stu_tokens)
        if not ref_set and not stu_set:
            return 1.0
        if not ref_set or not stu_set:
            return 0.0
        intersection = ref_set & stu_set
        union        = ref_set | stu_set
        return len(intersection) / len(union)

    def _calculate_keyword_match(self, ref_keywords: List[str], stu_keywords: List[str]) -> float:
        """Porcentaje de palabras clave de referencia presentes en respuesta"""
        if not ref_keywords:
            return 1.0
        ref_stems = {self._stem(w) for w in ref_keywords}
        stu_stems = {self._stem(w) for w in stu_keywords}
        matched = ref_stems & stu_stems
        return len(matched) / len(ref_stems)

    # ------------------------------------------------------------------ #
    # Análisis principal
    # ------------------------------------------------------------------ #

    def analyze(self, reference_text: str, student_text: str) -> Dict:
        """
        Analiza similitud léxica entre dos textos.

        Returns:
            dict con similarity, matched_terms, missing_terms, extra_terms, etc.
        """
        try:
            ref_tokens = self._tokenize(reference_text)
            stu_tokens = self._tokenize(student_text)

            ref_keywords = self._extract_keywords(ref_tokens)
            stu_keywords = self._extract_keywords(stu_tokens)

            # Similitud general
            similarity = self._calculate_similarity(ref_tokens, stu_tokens)

            # Coincidencia de palabras clave (con stemming)
            keyword_match = self._calculate_keyword_match(ref_keywords, stu_keywords)

            # Términos matched/missing/extra (usando stems)
            ref_stems = {self._stem(w): w for w in ref_keywords}
            stu_stems = {self._stem(w): w for w in stu_keywords}

            matched_stems = set(ref_stems.keys()) & set(stu_stems.keys())
            missing_stems = set(ref_stems.keys()) - set(stu_stems.keys())
            extra_stems   = set(stu_stems.keys()) - set(ref_stems.keys())

            matched_terms = [ref_stems[s] for s in matched_stems]
            missing_terms = [ref_stems[s] for s in missing_stems]
            extra_terms   = [stu_stems[s] for s in extra_stems]

            diversity = len(set(stu_tokens)) / max(len(stu_tokens), 1)

            return {
                'similarity':          round(similarity, 4),
                'keyword_match':       round(keyword_match, 4),
                'matched_terms':       matched_terms[:20],
                'missing_terms':       missing_terms[:20],
                'extra_terms':         extra_terms[:20],
                'reference_tokens':    len(ref_tokens),
                'student_tokens':      len(stu_tokens),
                'reference_keywords':  len(ref_keywords),
                'student_keywords':    len(stu_keywords),
                'lexical_diversity':   round(diversity, 3),
                'vocabulary_coverage': round(keyword_match, 3)
            }

        except Exception as e:
            logger.error(f"Error en análisis léxico: {e}")
            return {
                'similarity':    0.5,
                'error':         str(e),
                'matched_terms': [],
                'missing_terms': [],
                'extra_terms':   []
            }