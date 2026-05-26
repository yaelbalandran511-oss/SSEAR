"""
Utilidades - Funciones auxiliares para SSEAR
"""

import re
import logging
import hashlib
import json
from typing import List, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class TextCleaner:
    """Limpia y normaliza texto"""
    
    @staticmethod
    def clean(text: str) -> str:
        """Limpia texto removiendo caracteres especiales"""
        # Convertir a minúsculas
        text = text.lower()
        # Remover caracteres especiales pero mantener espacios
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normaliza espacios en blanco"""
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """Remueve URLs del texto"""
        return re.sub(r'https?://\S+', '', text)
    
    @staticmethod
    def remove_emails(text: str) -> str:
        """Remueve emails del texto"""
        return re.sub(r'\S+@\S+', '', text)
    
    @staticmethod
    def remove_extra_punctuation(text: str) -> str:
        """Remueve puntuación extra"""
        return re.sub(r'[!?\.]{2,}', '.', text)


class TextStatistics:
    """Calcula estadísticas del texto"""
    
    @staticmethod
    def word_count(text: str) -> int:
        """Cuenta palabras"""
        return len(text.split())
    
    @staticmethod
    def char_count(text: str) -> int:
        """Cuenta caracteres"""
        return len(text)
    
    @staticmethod
    def sentence_count(text: str) -> int:
        """Cuenta oraciones"""
        return len(re.split(r'[.!?]+', text))
    
    @staticmethod
    def avg_word_length(text: str) -> float:
        """Promedio de longitud de palabras"""
        words = text.split()
        if not words:
            return 0
        return sum(len(w) for w in words) / len(words)
    
    @staticmethod
    def get_statistics(text: str) -> Dict:
        """Retorna estadísticas completas del texto"""
        return {
            'word_count': TextStatistics.word_count(text),
            'char_count': TextStatistics.char_count(text),
            'sentence_count': TextStatistics.sentence_count(text),
            'avg_word_length': round(TextStatistics.avg_word_length(text), 2),
            'unique_words': len(set(text.lower().split()))
        }


class SimilarityUtils:
    """Utilidades para cálculos de similitud"""
    
    @staticmethod
    def jaccard_similarity(set1: set, set2: set) -> float:
        """Calcula similitud de Jaccard"""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def dice_similarity(set1: set, set2: set) -> float:
        """Calcula similitud de Dice"""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        return (2 * intersection) / (len(set1) + len(set2))
    
    @staticmethod
    def overlap_coefficient(set1: set, set2: set) -> float:
        """Calcula coeficiente de solapamiento"""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        return intersection / min(len(set1), len(set2))
    
    @staticmethod
    def levenshtein_ratio(str1: str, str2: str) -> float:
        """Calcula ratio de Levenshtein (0-1)"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()


class CacheManager:
    """Gestor de caché simple"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict = {}
        self.max_size = max_size
    
    def get_key(self, reference: str, student: str) -> str:
        """Genera clave de caché"""
        combined = f"{reference}||{student}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, key: str):
        """Obtiene valor del caché"""
        return self.cache.get(key)
    
    def set(self, key: str, value):
        """Guarda valor en caché"""
        if len(self.cache) >= self.max_size:
            # Remover primer elemento (FIFO)
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear(self):
        """Limpia caché"""
        self.cache.clear()
    
    def size(self) -> int:
        """Retorna tamaño del caché"""
        return len(self.cache)


class ResultsExporter:
    """Exporta resultados en diferentes formatos"""
    
    @staticmethod
    def to_json(data: Dict) -> str:
        """Exporta a JSON"""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_csv(results: List[Dict]) -> str:
        """Exporta múltiples resultados a CSV"""
        if not results:
            return ""
        
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'student_answer',
            'semantic_score',
            'lexical_score',
            'overall_score',
            'grade'
        ])
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'student_answer': result.get('student_answer', '')[:50],
                'semantic_score': result['scores']['semantic'],
                'lexical_score': result['scores']['lexical'],
                'overall_score': result['scores']['overall'],
                'grade': result['scores']['grade']
            })
        
        return output.getvalue()
    
    @staticmethod
    def to_markdown(data: Dict) -> str:
        """Exporta a Markdown"""
        md = []
        md.append("# Resultados de Evaluación SSEAR\n")
        
        scores = data.get('scores', {})
        md.append(f"## Puntuaciones\n")
        md.append(f"- **Similitud Semántica**: {scores.get('semantic', 0):.1f}%\n")
        md.append(f"- **Similitud Léxica**: {scores.get('lexical', 0):.1f}%\n")
        md.append(f"- **Calificación General**: {scores.get('overall', 0):.1f}%\n")
        md.append(f"- **Grado**: {scores.get('grade', 'N/A')}\n")
        
        return '\n'.join(md)


class Logger:
    """Logger personalizado"""
    
    @staticmethod
    def setup_logging(name: str, level: str = 'INFO'):
        """Configura logging"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    @staticmethod
    def log_evaluation(logger, reference_len: int, student_len: int, 
                      semantic_score: float, lexical_score: float):
        """Registra evaluación"""
        logger.info(
            f"Evaluación completada - "
            f"Ref: {reference_len} palabras, "
            f"Est: {student_len} palabras, "
            f"Semántica: {semantic_score:.2%}, "
            f"Léxica: {lexical_score:.2%}"
        )


class ValidationUtils:
    """Utilidades de validación"""
    
    @staticmethod
    def is_valid_text(text: str, min_length: int = 5, max_length: int = 10000) -> Tuple[bool, str]:
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
    """Monitorea rendimiento"""
    
    def __init__(self):
        self.times = {}
    
    def start(self, operation: str):
        """Inicia cronómetro"""
        self.times[operation] = datetime.now()
    
    def end(self, operation: str) -> float:
        """Termina cronómetro y retorna tiempo en milisegundos"""
        if operation not in self.times:
            return 0
        elapsed = (datetime.now() - self.times[operation]).total_seconds() * 1000
        del self.times[operation]
        return elapsed
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas"""
        return self.times


# Instancia global de caché
cache_manager = CacheManager()

# Logger global
app_logger = Logger.setup_logging('SSEAR')
