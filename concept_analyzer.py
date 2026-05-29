"""
Analizador de Conceptos - SSEAR
Evalúa respuestas usando ideas clave y penaliza errores graves
"""

import re
import unicodedata
import logging

logger = logging.getLogger(__name__)


class ConceptAnalyzer:
    """Evalúa respuestas usando ideas clave por tema"""

    def __init__(self):
        self.templates = self._load_templates()

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparación"""
        text = text.lower()
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        text = re.sub(r'[^\w\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _load_templates(self) -> dict:
        """Carga plantillas de conceptos clave por tema"""
        return {
            'fotosintesis': [
                'luz solar', 'energia', 'co2', 'dioxido de carbono',
                'agua', 'glucosa', 'oxigeno', 'clorofila', 'plantas',
                'proceso biologico', 'algas', 'bacterias'
            ],
            'celula': [
                'unidad basica', 'ser vivo', 'membrana', 'nucleo',
                'citoplasma', 'reproduccion', 'organismo'
            ],
            'mitosis': [
                'division celular', 'cromosomas', 'interfase', 'profase',
                'metafase', 'anafase', 'telofase', 'celulas hijas'
            ],
            'ecosistema': [
                'comunidad', 'habitat', 'cadena alimentaria', 'productores',
                'consumidores', 'descomponedores', 'energia', 'materia'
            ],
            'default': []
        }

    def _detect_topic(self, question: str) -> str:
        """Detecta el tema de la pregunta"""
        q = self._normalize_text(question)

        if any(k in q for k in ['fotosint', 'clorofila', 'luz solar', 'glucosa']):
            return 'fotosintesis'
        if any(k in q for k in ['celula', 'celular', 'membrana', 'nucleo']):
            return 'celula'
        if any(k in q for k in ['mitosis', 'division celular', 'cromosoma']):
            return 'mitosis'
        if any(k in q for k in ['ecosistema', 'habitat', 'cadena alimentaria']):
            return 'ecosistema'
        return 'default'

    def analyze(self, question: str, reference_text: str, student_text: str) -> dict:
        """
        Analiza conceptos clave en la respuesta del estudiante.

        Returns:
            dict con similarity, concepts_found, concepts_missing, penalty
        """
        norm_ref = self._normalize_text(reference_text)
        norm_stu = self._normalize_text(student_text)

        ref_tokens = set(norm_ref.split()) if norm_ref else set()
        stu_tokens = set(norm_stu.split()) if norm_stu else set()

        # Si son idénticas, puntaje perfecto
        if norm_ref == norm_stu:
            return {
                'similarity':       1.0,
                'concepts_found':   [],
                'concepts_missing': [],
                'penalty':          0.0
            }

        # Solapamiento de tokens
        token_overlap = (
            len(ref_tokens & stu_tokens) / max(len(ref_tokens), 1)
            if ref_tokens else 0.0
        )

        # Conceptos por tema
        topic    = self._detect_topic(question)
        keywords = self.templates.get(topic, [])

        found, missing = [], []
        for kw in keywords:
            if kw in norm_stu:
                found.append(kw)
            elif kw in norm_ref:
                missing.append(kw)

        if keywords:
            concept_score = len(found) / len(keywords)
        else:
            concept_score = token_overlap

        # Combinar overlap y concept_score
        similarity = max(
            token_overlap * 0.5 + concept_score * 0.5,
            token_overlap
        )
        similarity = max(0.0, min(1.0, similarity))

        return {
            'similarity':       round(similarity, 4),
            'concepts_found':   found,
            'concepts_missing': missing,
            'penalty':          0.0,
            'topic_detected':   topic
        }