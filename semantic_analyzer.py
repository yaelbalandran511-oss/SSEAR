"""
Analizador Semántico - SSEAR
Compara significados usando modelos Sentence Transformers
"""

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
        self.model_name = 'distiluse-base-multilingual-cased-v2'

        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.info(f"Cargando modelo: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                self.available = True
                logger.info("Modelo semántico cargado exitosamente")
            else:
                raise ImportError("sentence-transformers no disponible")
        except Exception as e:
            logger.error(f"Error cargando modelo semántico: {e}")
            self.available = False
            self.model = None

    def analyze(self, reference_text: str, student_text: str) -> dict:
        """
        Analiza similitud semántica entre dos textos.

        Args:
            reference_text: Respuesta de referencia
            student_text: Respuesta del estudiante

        Returns:
            dict con similarity (0.0-1.0), method y available
        """
        if not reference_text or not student_text:
            return {
                'similarity': 0.0,
                'method': 'none',
                'available': False,
                'error': 'Texto vacío'
            }

        if self.available and self.model:
            try:
                embeddings = self.model.encode(
                    [reference_text, student_text],
                    convert_to_tensor=True
                )
                similarity = float(util.cos_sim(embeddings[0], embeddings[1]))
                similarity = max(0.0, min(1.0, similarity))

                return {
                    'similarity': round(similarity, 4),
                    'method':     'sentence_transformers',
                    'available':  True,
                    'model':      self.model_name
                }
            except Exception as e:
                logger.error(f"Error en análisis semántico: {e}")

        # Fallback: similitud de Jaccard sobre palabras
        ref_words = set(reference_text.lower().split())
        stu_words = set(student_text.lower().split())

        if not ref_words:
            return {'similarity': 0.0, 'method': 'fallback', 'available': False}

        union        = ref_words | stu_words
        intersection = ref_words & stu_words
        similarity   = len(intersection) / len(union) if union else 0.0

        return {
            'similarity': round(similarity, 4),
            'method':     'fallback_jaccard',
            'available':  False
        }


class SentenceEmbedder:
    """Genera embeddings para análisis más profundo"""

    def __init__(self):
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
            else:
                self.model = None
        except Exception:
            self.model = None

    def get_embedding(self, text: str):
        """Obtiene embedding de un texto"""
        if self.model:
            return self.model.encode(text, convert_to_tensor=False)
        return None