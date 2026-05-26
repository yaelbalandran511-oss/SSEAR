"""
Generador de Retroalimentación - Crea feedback personalizado automático
"""

import logging
import json

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """Genera retroalimentación automática personalizada"""
    
    def __init__(self):
        """Inicializa generador de retroalimentación"""
        self.templates = self._load_templates()
        logger.info("Generador de retroalimentación inicializado")
    
    def generate(self, reference_answer, student_answer, semantic_results, 
                 lexical_results, overall_score, question=""):
        """
        Genera retroalimentación personalizada
        
        Args:
            reference_answer (str): Respuesta de referencia
            student_answer (str): Respuesta del estudiante
            semantic_results (dict): Resultados semánticos
            lexical_results (dict): Resultados léxicos
            overall_score (float): Puntuación general (0-1)
            question (str): Pregunta original (opcional)
        
        Returns:
            dict: Retroalimentación estructurada
        """
        feedback = {
            'summary': self._generate_summary(overall_score),
            'strengths': self._identify_strengths(semantic_results, lexical_results),
            'weaknesses': self._identify_weaknesses(semantic_results, lexical_results),
            'suggestions': self._generate_suggestions(
                reference_answer, 
                student_answer,
                semantic_results,
                lexical_results,
                overall_score
            ),
            'specific_feedback': self._generate_specific_feedback(
                semantic_results,
                lexical_results
            ),
            'action_items': self._generate_action_items(
                semantic_results,
                lexical_results,
                reference_answer
            )
        }
        
        return feedback
    
    def _generate_summary(self, score):
        """Genera resumen general basado en puntuación"""
        if score >= 0.9:
            return {
                'rating': 'Excelente',
                'message': '¡Respuesta excepcional! Demuestra comprensión profunda del tema.',
                'emoji': ''
            }
        elif score >= 0.8:
            return {
                'rating': 'Muy Bien',
                'message': 'Muy buena respuesta con elementos clave correctos.',
                'emoji': ''
            }
        elif score >= 0.7:
            return {
                'rating': 'Bien',
                'message': 'Respuesta satisfactoria pero con áreas de mejora.',
                'emoji': ''
            }
        elif score >= 0.6:
            return {
                'rating': 'Aceptable',
                'message': 'Respuesta básica que necesita más detalle y precisión.',
                'emoji': ''
            }
        elif score >= 0.5:
            return {
                'rating': 'Necesita Mejora',
                'message': 'Respuesta incompleta, revisa los conceptos principales.',
                'emoji': ''
            }
        else:
            return {
                'rating': 'Insuficiente',
                'message': 'La respuesta requiere revisión significativa.',
                'emoji': ''
            }
    
    def _identify_strengths(self, semantic_results, lexical_results):
        """Identifica fortalezas de la respuesta"""
        strengths = []
        
        semantic_sim = semantic_results.get('similarity', 0)
        lexical_sim = lexical_results.get('similarity', 0)
        
        if semantic_sim >= 0.7:
            strengths.append({
                'title': 'Comprensión Conceptual',
                'description': 'Demuestra buen entendimiento semántico del tema',
                'score': round(semantic_sim * 100, 1)
            })
        
        if lexical_sim >= 0.7:
            strengths.append({
                'title': 'Vocabulario Apropiado',
                'description': 'Utiliza términos clave relevantes correctamente',
                'score': round(lexical_sim * 100, 1)
            })
        
        matched_terms = lexical_results.get('matched_terms', [])
        if matched_terms and len(matched_terms) >= 5:
            strengths.append({
                'title': 'Cobertura de Términos Clave',
                'description': f'Incluye {len(matched_terms)} términos clave importantes',
                'score': min(100, len(matched_terms) * 10)
            })
        
        if not strengths:
            strengths.append({
                'title': 'Esfuerzo Inicial',
                'description': 'Has intentado abordar la pregunta',
                'score': 50
            })
        
        return strengths
    
    def _identify_weaknesses(self, semantic_results, lexical_results):
        """Identifica debilidades de la respuesta"""
        weaknesses = []
        
        semantic_sim = semantic_results.get('similarity', 0)
        lexical_sim = lexical_results.get('similarity', 0)
        
        if semantic_sim < 0.7:
            weaknesses.append({
                'title': 'Claridad Conceptual',
                'description': 'La respuesta no captura completamente los conceptos principales',
                'score': round(semantic_sim * 100, 1),
                'severity': 'alta' if semantic_sim < 0.5 else 'media'
            })
        
        if lexical_sim < 0.7:
            weaknesses.append({
                'title': 'Precisión en Vocabulario',
                'description': 'Faltan términos clave o hay imprecisión en el lenguaje',
                'score': round(lexical_sim * 100, 1),
                'severity': 'alta' if lexical_sim < 0.5 else 'media'
            })
        
        missing_terms = lexical_results.get('missing_terms', [])
        if missing_terms:
            weaknesses.append({
                'title': 'Términos Faltantes',
                'description': f'No menciona {len(missing_terms)} términos importantes',
                'count': len(missing_terms),
                'severity': 'media' if len(missing_terms) <= 5 else 'alta'
            })
        
        if not weaknesses:
            weaknesses.append({
                'title': 'Sin Debilidades Significativas',
                'description': 'La respuesta es completa y precisa',
                'score': 100
            })
        
        return weaknesses
    
    def _generate_suggestions(self, reference, student, semantic_results, 
                            lexical_results, overall_score):
        """Genera sugerencias de mejora"""
        suggestions = []
        
        # Sugerencia 1: Términos faltantes
        missing_terms = lexical_results.get('missing_terms', [])
        if missing_terms:
            suggestions.append({
                'type': 'vocabulary',
                'title': 'Incluye Términos Clave Faltantes',
                'description': f'Considera agregar: {", ".join(missing_terms[:5])}',
                'priority': 'alta'
            })
        
        # Sugerencia 2: Ampliar explicación
        if semantic_results.get('similarity', 0) < 0.8:
            suggestions.append({
                'type': 'expansion',
                'title': 'Amplía tu Explicación',
                'description': 'La respuesta necesita más detalles y ejemplos para claridad conceptual',
                'priority': 'alta'
            })
        
        # Sugerencia 3: Precisión
        if lexical_results.get('similarity', 0) < 0.7:
            suggestions.append({
                'type': 'precision',
                'title': 'Sé más Preciso en la Terminología',
                'description': 'Revisa las palabras utilizadas para asegurar que sean técnicamente correctas',
                'priority': 'media'
            })
        
        # Sugerencia 4: Estructura
        ref_len = semantic_results.get('reference_tokens', 0)
        stu_len = semantic_results.get('student_tokens', 0)
        
        if stu_len < ref_len * 0.5:
            suggestions.append({
                'type': 'structure',
                'title': 'Desarrolla Más tu Respuesta',
                'description': f'Tu respuesta es muy corta ({stu_len} palabras vs {ref_len} esperadas)',
                'priority': 'media'
            })
        
        # Sugerencia 5: Ejemplos
        if overall_score < 0.8 and semantic_results.get('similarity', 0) < 0.75:
            suggestions.append({
                'type': 'examples',
                'title': 'Añade Ejemplos Concretos',
                'description': 'Los ejemplos específicos ayudan a clarificar conceptos complejos',
                'priority': 'media'
            })
        
        if not suggestions:
            suggestions.append({
                'type': 'excellence',
                'title': 'Mantén tu Nivel de Excelencia',
                'description': 'Tu respuesta es muy buena, continúa así',
                'priority': 'baja'
            })
        
        return suggestions
    
    def _generate_specific_feedback(self, semantic_results, lexical_results):
        """Genera feedback específico por categoría"""
        return {
            'semantic_analysis': {
                'score': round(semantic_results.get('similarity', 0) * 100, 1),
                'message': self._get_semantic_message(semantic_results.get('similarity', 0)),
                'details': f"Similitud de tokens: {semantic_results.get('token_overlap', 0) * 100:.1f}%"
            },
            'lexical_analysis': {
                'score': round(lexical_results.get('similarity', 0) * 100, 1),
                'message': self._get_lexical_message(lexical_results.get('similarity', 0)),
                'details': f"Diversidad lexical: {lexical_results.get('lexical_diversity', 0) * 100:.1f}%"
            }
        }
    
    def _get_semantic_message(self, score):
        """Mensaje según puntuación semántica"""
        if score >= 0.85:
            return "Comprensión excepcional de conceptos"
        elif score >= 0.70:
            return "Buena comprensión conceptual"
        elif score >= 0.50:
            return "Comprensión parcial de conceptos"
        else:
            return "Necesitas revisar los conceptos principales"
    
    def _get_lexical_message(self, score):
        """Mensaje según puntuación léxica"""
        if score >= 0.85:
            return "Excelente uso de vocabulario técnico"
        elif score >= 0.70:
            return "Buen uso de términos clave"
        elif score >= 0.50:
            return "Vocabulario parcialmente apropiado"
        else:
            return "Necesitas mejorar la precisión en el vocabulario"
    
    def _generate_action_items(self, semantic_results, lexical_results, reference):
        """Genera lista de acciones a tomar"""
        actions = []
        
        missing_terms = lexical_results.get('missing_terms', [])
        if missing_terms:
            actions.append({
                'priority': 1,
                'action': f'Revisa y aprende los siguientes términos: {", ".join(missing_terms[:3])}',
                'category': 'vocabulario'
            })
        
        if semantic_results.get('similarity', 0) < 0.7:
            actions.append({
                'priority': 1,
                'action': 'Relee la pregunta y el material de referencia para mejor comprensión',
                'category': 'conceptos'
            })
        
        if lexical_results.get('similarity', 0) < 0.7:
            actions.append({
                'priority': 2,
                'action': 'Reformula tu respuesta usando terminología más precisa',
                'category': 'redacción'
            })
        
        if not actions:
            actions.append({
                'priority': 3,
                'action': 'Excelente trabajo, mantén este nivel de calidad',
                'category': 'mantenimiento'
            })
        
        return sorted(actions, key=lambda x: x['priority'])
    
    def _load_templates(self):
        """Carga templates de retroalimentación"""
        return {
            'excellent': 'Tu respuesta es excepcional y demuestra comprensión profunda.',
            'good': 'Tu respuesta es buena con elementos clave correctos.',
            'satisfactory': 'Tu respuesta es satisfactoria pero puede mejorarse.',
            'needs_improvement': 'Tu respuesta necesita revisión y mejora significativa.'
        }
