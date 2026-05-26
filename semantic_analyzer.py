"""
Analizador Semántico - Compara significados usando modelos transformers
"""

import difflib
import numpy as np
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers no disponible, usando fallback")


class SemanticAnalyzer:
    """Analiza similitud semántica entre respuestas"""
    
    def __init__(self):
        """Inicializa el modelo de transformers para embeddings"""
        self.model_name = 'distiluse-base-multilingual-cased-v2'
        
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.info(f"Cargando modelo: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                self.available = True
                logger.info("Modelo semántico cargado")
            else:
                raise ImportError("sentence-transformers no disponible")
        except Exception as e:
            logger.error(f"Error cargando modelo semántico: {e}")
            self.available = False
            self.model = None
    
    def analyze(self, reference_text, student_text):
        """
        Analiza similitud semántica entre dos textos
        
        Args:
            reference_text (str): Respuesta de referencia
            student_text (str): Respuesta del estudiante
        
        Returns:
            dict: Resultados del análisis
        """
        try:
            # Tokenizar y limpiar
            reference_tokens = self._tokenize(reference_text)
            student_tokens = self._tokenize(student_text)
            
            # Calcular embeddings
            if self.available and self.model:
                reference_embedding = self.model.encode(reference_text, convert_to_tensor=True, normalize_embeddings=True)
                student_embedding = self.model.encode(student_text, convert_to_tensor=True, normalize_embeddings=True)
                
                # Similitud coseno durable
                similarity = float(util.cos_sim(reference_embedding, student_embedding)[0][0])
            else:
                # Fallback: similitud basada en texto y tokens
                similarity = self._fallback_similarity(reference_text, student_text, reference_tokens, student_tokens)
            
            # Asegurar que está entre 0 y 1
            similarity = max(0.0, min(1.0, similarity))
            
            # Análisis adicional
            overlap_ratio = len(set(reference_tokens) & set(student_tokens)) / max(len(set(reference_tokens)), 1)
            
            return {
                'similarity': similarity,
                'confidence': 0.95 if self.available else 0.70,
                'reference_tokens': len(reference_tokens),
                'student_tokens': len(student_tokens),
                'token_overlap': round(overlap_ratio, 3),
                'model': 'sentence-transformers' if self.available else 'fallback'
            }
            
        except Exception as e:
            logger.error(f"Error en análisis semántico: {e}")
            return {
                'similarity': 0.5,
                'confidence': 0.0,
                'error': str(e),
                'reference_tokens': 0,
                'student_tokens': 0
            }
    
    def _tokenize(self, text):
        """Tokeniza un texto de manera simple"""
        import re
        text = text.lower()
        # Remover puntuación
        text = re.sub(r'[^\w\s]', ' ', text)
        # Dividir en palabras
        tokens = text.split()
        # Filtrar palabras muy cortas
        tokens = [t for t in tokens if len(t) > 2]
        return tokens
    
    def _fallback_similarity(self, reference_text, student_text, tokens1, tokens2):
        """Fallback: similitud basada en texto y tokens para respuestas similares"""
        set1 = set(tokens1)
        set2 = set(tokens2)

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        jaccard = intersection / union if union > 0 else 0

        coverage = intersection / min(len(set1), len(set2)) if min(len(set1), len(set2)) > 0 else 0
        text_ratio = difflib.SequenceMatcher(None, reference_text.lower(), student_text.lower()).ratio()
        fuzzy_ratio = self._token_fuzzy_similarity(tokens1, tokens2)

        # Elevar la puntuación cuando la respuesta es conceptualmente similar
        score = max(jaccard, coverage, fuzzy_ratio * 0.9, text_ratio * 0.9)
        return min(1.0, score)

    def _token_fuzzy_similarity(self, tokens1, tokens2):
        """Calcula similitud flexible entre tokens"""
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


class SentenceEmbedder:
    """Genera embeddings para análisis más profundo"""
    
    def __init__(self):
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
        except:
            self.model = None
    
    def get_embedding(self, text):
        """Obtiene embedding de un texto"""
        if self.model:
            return self.model.encode(text, convert_to_tensor=False)
        return np.array([])
    
    def similarity(self, text1, text2):
        """Calcula similitud entre dos textos"""
        if self.model:
            embeddings = self.model.encode([text1, text2], convert_to_tensor=False)
            a = np.array(embeddings[0], dtype=float)
            b = np.array(embeddings[1], dtype=float)
            # calcular similitud coseno segura
            denom = (np.linalg.norm(a) * np.linalg.norm(b))
            if denom == 0:
                return 0.0
            return float(np.dot(a, b) / denom)
        return 0.0
