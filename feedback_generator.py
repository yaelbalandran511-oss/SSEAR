"""
Generador de Retroalimentación - SSEAR
"""

import logging
import config

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    def __init__(self):
        logger.info("Generador de retroalimentación inicializado")

    def generate(self, evaluation_result: dict) -> dict:
        scores   = evaluation_result.get('scores', {})
        metadata = evaluation_result.get('metadata', {})
        analysis = evaluation_result.get('analysis', {})

        percentage     = scores.get('percentage', 0)
        grade          = scores.get('grade', 'F')
        semantic_score = scores.get('semantic', 0)
        lexical_score  = scores.get('lexical', 0)

        # ✅ CORREGIDO: leer directamente de metadata
        matched_terms = metadata.get('matched_terms', [])
        missing_terms = metadata.get('missing_terms', [])
        extra_terms   = metadata.get('extra_terms', [])
        term_coverage = metadata.get('term_coverage', 'N/A')

        # Resumen
        label         = config.GRADE_LABELS.get(grade, 'Insuficiente')
        message       = self._get_message(percentage)
        encouragement = self._get_encouragement(percentage)

        # Fortalezas
        strengths = []
        if semantic_score >= 0.7:
            strengths.append("Buena comprensión conceptual del tema.")
        if lexical_score >= 0.5:
            strengths.append("Vocabulario técnico adecuado.")
        if matched_terms:
            strengths.append(f"Términos clave identificados: {', '.join(matched_terms[:5])}.")
        if not strengths:
            strengths.append("La respuesta aborda el tema solicitado.")

        # Debilidades
        weaknesses = []
        if semantic_score < 0.5:
            weaknesses.append("La comprensión semántica del tema es baja.")
        if lexical_score < 0.4:
            weaknesses.append("Falta vocabulario técnico específico.")
        if missing_terms:
            weaknesses.append(f"Términos importantes no mencionados: {', '.join(missing_terms[:5])}.")
        if not weaknesses:
            weaknesses.append("Continúa profundizando en los conceptos avanzados.")

        # Desglose
        sem_pct = round(semantic_score * 100, 1)
        lex_pct = round(lexical_score * 100, 1)
        analysis_breakdown = {
            'semantic': {
                'score':          sem_pct,
                'weight':         f"{int(config.SEMANTIC_WEIGHT * 100)}%",
                'interpretation': self._interpret_score(sem_pct)
            },
            'lexical': {
                'score':          lex_pct,
                'weight':         f"{int(config.LEXICAL_WEIGHT * 100)}%",
                'interpretation': self._interpret_score(lex_pct)
            }
        }

        # Acciones
        action_items = self._get_action_items(percentage, missing_terms)

        # ✅ CORREGIDO: análisis detallado con scores reales
        detailed_analysis = {
            'matched_terms':  matched_terms,
            'missing_terms':  missing_terms,
            'extra_terms':    extra_terms,
            'term_coverage':  term_coverage,
            'semantic_score': sem_pct,
            'lexical_score':  lex_pct
        }

        return {
            'summary': {
                'grade':         grade,
                'label':         label,
                'percentage':    round(percentage, 2),
                'message':       message,
                'encouragement': encouragement
            },
            'strengths':          strengths,
            'weaknesses':         weaknesses,
            'analysis_breakdown': analysis_breakdown,
            'action_items':       action_items,
            'detailed_analysis':  detailed_analysis,
            'specific_feedback':  self._specific_feedback(percentage, matched_terms, missing_terms)
        }

    def _get_message(self, pct: float) -> str:
        if pct >= 85: return config.FEEDBACK_MESSAGES['excellent']
        if pct >= 70: return config.FEEDBACK_MESSAGES['very_good']
        if pct >= 55: return config.FEEDBACK_MESSAGES['good']
        if pct >= 40: return config.FEEDBACK_MESSAGES['acceptable']
        if pct >= 20: return config.FEEDBACK_MESSAGES['needs_improvement']
        return config.FEEDBACK_MESSAGES['insufficient']

    def _get_encouragement(self, pct: float) -> str:
        if pct >= 85: return "¡Excelente trabajo! Sigue así."
        if pct >= 70: return "¡Buen trabajo! Con un poco más de detalle llegarás al nivel excelente."
        if pct >= 55: return "Vas por buen camino. Profundiza en los conceptos clave."
        if pct >= 40: return "Tienes la base. Trabaja en completar tu respuesta con más detalle."
        return "No te desanimes. Revisa el material y vuelve a intentarlo."

    def _interpret_score(self, pct: float) -> str:
        if pct >= 80: return "Muy bueno"
        if pct >= 60: return "Aceptable"
        if pct >= 40: return "Regular"
        return "Bajo"

    def _get_action_items(self, pct: float, missing_terms: list) -> list:
        actions = []
        if missing_terms:
            actions.append({
                'priority': 'alta',
                'action':   f"Incluye los conceptos: {', '.join(missing_terms[:4])}.",
                'resource': 'Notas de clase o libro de texto'
            })
        if pct < 55:
            actions.append({
                'priority': 'alta',
                'action':   'Revisa el tema completo antes de la evaluación.',
                'resource': 'Material del curso'
            })
        if pct < 70:
            actions.append({
                'priority': 'media',
                'action':   'Elabora más tus respuestas con ejemplos y detalles.',
                'resource': ''
            })
        if not actions:
            actions.append({
                'priority': 'baja',
                'action':   'Continúa practicando para mantener el nivel.',
                'resource': ''
            })
        return actions

    def _specific_feedback(self, pct: float, matched: list, missing: list) -> list:
        fb = []
        if matched:
            fb.append(f"✅ Conceptos correctos: {', '.join(matched[:5])}.")
        if missing:
            fb.append(f"❌ Conceptos faltantes: {', '.join(missing[:5])}.")
        if pct >= 70:
            fb.append("📚 Respuesta que demuestra comprensión del tema.")
        else:
            fb.append("📖 Se recomienda repasar el tema para completar la respuesta.")
        return fb