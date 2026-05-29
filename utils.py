"""
Utilidades - SSEAR
Funciones auxiliares para normalización, validación y monitoreo
"""

import re
import logging
import unicodedata
from typing import Optional, Dict, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================
# FUNCIONES GLOBALES
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normaliza texto para análisis.

    Args:
        text: Texto a normalizar

    Returns:
        Texto normalizado (minúsculas, sin acentos ni puntuación especial)
    """
    if not text:
        return ""

    text = text.lower()

    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def validate_input(reference: str, student: str, question: str = "") -> Optional[str]:
    """
    Valida entrada para evaluación.

    Args:
        reference: Respuesta de referencia
        student:   Respuesta del estudiante
        question:  Pregunta (opcional)

    Returns:
        None si es válido, mensaje de error si no
    """
    import config

    if not reference or not isinstance(reference, str):
        return "Respuesta de referencia inválida"

    reference = reference.strip()
    if len(reference) < config.MIN_REFERENCE_LENGTH:
        return f"Respuesta de referencia debe tener al menos {config.MIN_REFERENCE_LENGTH} caracteres"

    if len(reference) > config.MAX_RESPONSE_LENGTH:
        return f"Respuesta de referencia no debe exceder {config.MAX_RESPONSE_LENGTH} caracteres"

    if not student or not isinstance(student, str):
        return "Respuesta del estudiante inválida"

    student = student.strip()
    if len(student) < config.MIN_STUDENT_LENGTH:
        return f"Respuesta del estudiante debe tener al menos {config.MIN_STUDENT_LENGTH} caracteres"

    if len(student) > config.MAX_RESPONSE_LENGTH:
        return f"Respuesta del estudiante no debe exceder {config.MAX_RESPONSE_LENGTH} caracteres"

    if question and isinstance(question, str):
        if len(question.strip()) > config.MAX_RESPONSE_LENGTH:
            return "Pregunta es demasiado larga"

    return None


# ============================================================
# CLASES DE UTILIDAD
# ============================================================

class CacheManager:
    """Maneja caché en memoria"""

    def __init__(self, max_size: int = 1000):
        self._cache: Dict = {}
        self.max_size = max_size
        self.hits   = 0
        self.misses = 0

    def get(self, key: str):
        val = self._cache.get(key)
        if val is not None:
            self.hits += 1
        else:
            self.misses += 1
        return val

    def set(self, key: str, value) -> None:
        if len(self._cache) >= self.max_size:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = value

    def clear(self):
        self._cache.clear()
        self.hits   = 0
        self.misses = 0

    def stats(self) -> Dict:
        total = self.hits + self.misses
        return {
            'size':      len(self._cache),
            'max_size':  self.max_size,
            'hits':      self.hits,
            'misses':    self.misses,
            'hit_rate':  round(self.hits / max(total, 1), 3)
        }


class Logger:
    """Logger personalizado"""

    @staticmethod
    def setup_logging(name: str, level: str = 'INFO') -> logging.Logger:
        """Configura logging"""
        lgr = logging.getLogger(name)
        lgr.setLevel(getattr(logging, level))

        if not lgr.handlers:
            handler   = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            lgr.addHandler(handler)

        return lgr

    @staticmethod
    def log_evaluation(lgr: logging.Logger, reference_len: int, student_len: int,
                       semantic_score: float, lexical_score: float):
        """Registra una evaluación"""
        lgr.info(
            f"Evaluación - "
            f"Ref: {reference_len} palabras, "
            f"Est: {student_len} palabras, "
            f"Semántica: {semantic_score:.2%}, "
            f"Léxica: {lexical_score:.2%}"
        )


class ValidationUtils:
    """Utilidades de validación"""

    @staticmethod
    def is_valid_text(text: str, min_length: int = 5,
                      max_length: int = 10000) -> Tuple[bool, str]:
        """Valida si el texto es válido"""
        if not text or not isinstance(text, str):
            return False, "El texto debe ser una cadena no vacía"

        text = text.strip()

        if len(text) < min_length:
            return False, f"El texto debe tener al menos {min_length} caracteres"

        if len(text) > max_length:
            return False, f"El texto no debe exceder {max_length} caracteres"

        return True, "OK"

    @staticmethod
    def is_valid_request(reference: str, student: str) -> Tuple[bool, str]:
        """Valida si la solicitud es válida"""
        valid_ref, msg_ref = ValidationUtils.is_valid_text(reference, min_length=10)
        if not valid_ref:
            return False, f"Respuesta de referencia: {msg_ref}"

        valid_stu, msg_stu = ValidationUtils.is_valid_text(student, min_length=5)
        if not valid_stu:
            return False, f"Respuesta de estudiante: {msg_stu}"

        return True, "OK"


class PerformanceMonitor:
    """Monitorea rendimiento del sistema"""

    def __init__(self):
        self.times: Dict = {}
        self.history: List = []

    def start(self, operation: str):
        """Inicia cronómetro"""
        self.times[operation] = datetime.now()

    def end(self, operation: str) -> float:
        """Termina cronómetro y retorna tiempo en milisegundos"""
        if operation not in self.times:
            return 0.0
        elapsed = (datetime.now() - self.times[operation]).total_seconds() * 1000
        del self.times[operation]
        self.history.append({'operation': operation, 'ms': elapsed})
        return elapsed

    def get_stats(self) -> Dict:
        return {
            'active':  list(self.times.keys()),
            'history': self.history[-10:]
        }


# ============================================================
# INSTANCIAS GLOBALES
# ============================================================

cache_manager = CacheManager()
app_logger    = Logger.setup_logging('SSEAR')