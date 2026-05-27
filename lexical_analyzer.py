"""
Analizador Léxico - Compara palabras clave y vocabulario
"""

import difflib
import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Intentar usar SnowballStemmer de NLTK; si falla, usar stemmer de reserva
try:
    from nltk.stem.snowball import SnowballStemmer
    HAS_SNOWBALL = True
except Exception:
    HAS_SNOWBALL = False


class LexicalAnalyzer:
    """Analiza similitud léxica entre respuestas"""
    
    def __init__(self):
        """Inicializa analizador léxico"""
        self.stop_words = set()
        if HAS_SNOWBALL:
            try:
                self.stemmer = SnowballStemmer('spanish')
            except Exception:
                self.stemmer = None
        else:
            self.stemmer = None

        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('spanish'))
        except Exception:
            # Lista de stopwords españolas básica como fallback
            self.stop_words = {
                'la', 'el', 'los', 'las', 'un', 'una', 'unos', 'unas',
                'y', 'o', 'pero', 'que', 'de', 'del', 'al', 'en', 'por',
                'con', 'sin', 'para', 'se', 'es', 'su', 'sus', 'como',
                'más', 'muy', 'a', 'al', 'lo', 'le', 'les'
            }

        logger.info("Analizador léxico inicializado")
    
    def analyze(self, reference_text, student_text):
        """
        Analiza similitud léxica entre dos textos
        
        Args:
            reference_text (str): Respuesta de referencia
            student_text (str): Respuesta del estudiante
        
        Returns:
            dict: Resultados del análisis léxico
        """
        try:
            # Tokenizar
            ref_tokens = self._tokenize(reference_text)
            stu_tokens = self._tokenize(student_text)
            
            # Extraer palabras clave (sin stopwords)
            ref_keywords = self._extract_keywords(reference_text)
            stu_keywords = self._extract_keywords(student_text)
            
            # Calcular similitud léxica
            similarity = self._calculate_similarity(ref_tokens, stu_tokens)
            
            # Coincidencia de palabras clave
            keyword_match = self._calculate_keyword_match(ref_keywords, stu_keywords)
            
            # Análisis de términos
            matched_terms = list(set(ref_keywords) & set(stu_keywords))
            missing_terms = list(set(ref_keywords) - set(stu_keywords))
            extra_terms = list(set(stu_keywords) - set(ref_keywords))
            
            # Diversidad lexical
            diversity = len(set(stu_tokens)) / max(len(stu_tokens), 1)
            
            return {
                'similarity': similarity,
                'keyword_match': keyword_match,
                'matched_terms': matched_terms[:20],  # Top 20
                'missing_terms': missing_terms[:20],   # Top 20
                'extra_terms': extra_terms[:20],       # Top 20
                'reference_tokens': len(ref_tokens),
                'student_tokens': len(stu_tokens),
                'reference_keywords': len(ref_keywords),
                'student_keywords': len(stu_keywords),
                'lexical_diversity': round(diversity, 3),
                'vocabulary_coverage': round(keyword_match, 3)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis léxico: {e}")
            return {
                'similarity': 0.5,
                'error': str(e),
                'matched_terms': [],
                'missing_terms': [],
                'extra_terms': []
            }
    
    def _tokenize(self, text):
        """Tokeniza texto en palabras"""
        text = text.lower()
        # Remover puntuación especial pero mantener guiones y apóstrofos
        text = re.sub(r'[^\w\s\-\']', ' ', text)
        tokens = text.split()
        # Filtrar tokens muy cortos y normalizar por raíz
        tokens = [self._stem_token(t) for t in tokens if len(t) > 1]
        return [t for t in tokens if t]
    
    def _stem_token(self, token):
        """Normaliza un token usando stemmer"""
        t = token.lower()
        if self.stemmer:
            try:
                return self.stemmer.stem(t)
            except Exception:
                return t
        # Fallback simple: eliminar sufijos comunes en español
        for suf in ('mente', 'ciones', 'ción', 'antes', 'ancia', 'encias', 'ancia', 'idades', 'idad', 'mente', 'mente', 'amiento', 'imiento', 'ado', 'ada', 'idos', 'idas', 'iva', 'ivo', 'ivas', 'ivos', 'ar', 'er', 'ir', 'es', 's'):
            if t.endswith(suf) and len(t) - len(suf) > 2:
                return t[:-len(suf)]
        return t
    
    def _extract_keywords(self, text):
        """Extrae palabras clave (sin stopwords)"""
        tokens = self._tokenize(text)
        keywords = [t for t in tokens if t not in self.stop_words and len(t) > 2]
        return keywords
    
    def _calculate_similarity(self, tokens1, tokens2):
        """Calcula similitud léxica usando la fórmula estándar de cobertura de palabras.

        similitud = (2 * palabras_comunes) / (total_tokens_ref + total_tokens_est)
        """
        if not tokens1 or not tokens2:
            return 0.0

        common = sum((Counter(tokens1) & Counter(tokens2)).values())
        return (2 * common) / (len(tokens1) + len(tokens2))
    
    def _fuzzy_token_similarity(self, tokens1, tokens2):
        """Calcula similaridad aproximada entre tokens"""
        if not tokens1 or not tokens2:
            return 0.0

        ratios = []
        for token1 in tokens1:
            best_ratio = 0.0
            for token2 in tokens2:
                ratio = difflib.SequenceMatcher(None, token1, token2).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
            ratios.append(best_ratio)
        return sum(ratios) / len(ratios) if ratios else 0.0
    
    def _calculate_keyword_match(self, keywords1, keywords2):
        """Calcula porcentaje de coincidencia de palabras clave"""
        if not keywords1:
            return 0.0
        
        matched = len(set(keywords1) & set(keywords2))
        return matched / len(keywords1)
    
    def get_similarity_details(self, text1, text2):
        """Retorna detalles detallados de similitud"""
        tokens1 = self._tokenize(text1)
        tokens2 = self._tokenize(text2)
        
        common = set(tokens1) & set(tokens2)
        unique1 = set(tokens1) - set(tokens2)
        unique2 = set(tokens2) - set(tokens1)
        
        return {
            'common_tokens': list(common),
            'unique_in_reference': list(unique1),
            'unique_in_student': list(unique2),
            'token_frequency_ref': dict(Counter(tokens1).most_common(10)),
            'token_frequency_stu': dict(Counter(tokens2).most_common(10))
        }


class KeywordExtractor:
    """Extrae palabras clave importantes de un texto"""
    
    def __init__(self):
        self.analyzer = LexicalAnalyzer()
    
    def extract(self, text, top_n=10):
        """Extrae palabras clave más relevantes"""
        keywords = self.analyzer._extract_keywords(text)
        counter = Counter(keywords)
        return [kw for kw, count in counter.most_common(top_n)]
    
    def extract_with_frequency(self, text, top_n=10):
        """Extrae palabras clave con frecuencia"""
        keywords = self.analyzer._extract_keywords(text)
        counter = Counter(keywords)
        return dict(counter.most_common(top_n))
