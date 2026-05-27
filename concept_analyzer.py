"""
Analizador de conceptos por ideas clave.
"""

import re
import unicodedata


class ConceptAnalyzer:
    """Evalúa respuestas usando ideas clave y penaliza errores graves."""

    def __init__(self):
        self.templates = self._load_templates()

    def analyze(self, question, reference_text, student_text):
        template = self._select_template(question, reference_text)
        if template is None:
            return self._fallback()
        return self._evaluate_template(student_text, template)

    def _select_template(self, question, reference_text):
        normalized = self._normalize_text(question + ' ' + reference_text)
        for key, template in self.templates.items():
            if key in normalized:
                return template
        return None

    def _evaluate_template(self, student_text, template):
        normalized_student = self._normalize_text(student_text)
        stemmed_student = self._stem_text(normalized_student)
        score = 0.0
        details = []

        concept_presence = {}
        for concept in template['concepts']:
            present = self._concept_present(stemmed_student, concept['keywords'])
            concept_presence[concept['id']] = present
            if present:
                score += concept['weight']
            details.append({
                'id': concept['id'],
                'weight': concept['weight'],
                'present': present,
                'keywords': concept['keywords']
            })

        if not concept_presence.get('conceptos_distintos'):
            if concept_presence.get('velocidad_direccion') and concept_presence.get('aceleracion_cambio_velocidad'):
                score += next(c['weight'] for c in template['concepts'] if c['id'] == 'conceptos_distintos')
                for detail in details:
                    if detail['id'] == 'conceptos_distintos':
                        detail['present'] = True
                        break

        penalty = self._calculate_penalty(normalized_student, template)
        corrected_score = max(0.0, score - penalty)

        return {
            'similarity': round(corrected_score, 4),
            'concept_score': round(score, 4),
            'penalty': round(penalty, 4),
            'concepts': details,
            'template_name': template['name'],
            'model': 'concept-based'
        }

    def _concept_present(self, stemmed_student, keyword_groups):
        for keyword_group in keyword_groups:
            if all(self._stem_token(keyword) in stemmed_student for keyword in keyword_group):
                return True
        return False

    def _stem_text(self, text):
        return ' '.join(self._stem_token(token) for token in text.split())

    def _stem_token(self, token):
        suffixes = ['aciones', 'acion', 'mente', 'idades', 'idad', 'amiento', 'imiento',
                    'imiento', 'adora', 'ador', 'ante', 'ancia', 'encia', 'ente', 'ible', 'able',
                    'iva', 'ivo', 'ivos', 'ivas', 'mente', 'idad', 'ismos', 'ismo', 'ismo', 'ista', 'ar', 'er', 'ir', 's']
        for suf in suffixes:
            if token.endswith(suf) and len(token) > len(suf) + 2:
                return token[:-len(suf)]
        return token

    def _calculate_penalty(self, normalized_student, template):
        penalty = 0.0
        for false_item in template['false_statements']:
            if any(keyword in normalized_student for keyword in false_item['keywords']):
                penalty += false_item['penalty']
        return min(penalty, 0.20)

    def _fallback(self):
        return {
            'similarity': 0.0,
            'concept_score': 0.0,
            'penalty': 0.0,
            'concepts': [],
            'template_name': 'fallback',
            'model': 'concept-fallback'
        }

    def _normalize_text(self, text):
        if not text:
            return ''
        text = text.lower()
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _load_templates(self):
        return {
            'diferencia entre velocidad y aceleracion': {
                'name': 'Velocidad vs Aceleración',
                'concepts': [
                    {
                        'id': 'velocidad_direccion',
                        'weight': 0.25,
                        'keywords': [
                            ['velocidad', 'direccion'],
                            ['rapidez', 'direccion'],
                            ['velocidad', 'sentido'],
                            ['vectorial']
                        ]
                    },
                    {
                        'id': 'aceleracion_cambio_velocidad',
                        'weight': 0.25,
                        'keywords': [
                            ['aceleracion', 'cambio', 'velocidad'],
                            ['aceleracion', 'cambia', 'velocidad'],
                            ['aceleracion', 'variacion', 'velocidad'],
                            ['aceleracion', 'modific', 'velocidad']
                        ]
                    },
                    {
                        'id': 'aceleracion_cambio_direccion',
                        'weight': 0.25,
                        'keywords': [
                            ['aceleracion', 'aument'],
                            ['aceleracion', 'disminu'],
                            ['aceleracion', 'cambi', 'direccion'],
                            ['aumentando'],
                            ['disminuyendo'],
                            ['cambiando', 'direccion']
                        ]
                    },
                    {
                        'id': 'conceptos_distintos',
                        'weight': 0.25,
                        'keywords': [
                            ['velocidad', 'aceleracion', 'distinto'],
                            ['velocidad', 'aceleracion', 'diferente'],
                            ['no es lo mismo']
                        ]
                    }
                ],
                'false_statements': [
                    {
                        'id': 'velocidad_sin_direccion',
                        'penalty': 0.20,
                        'keywords': [
                            'velocidad no tiene direccion',
                            'velocidad sin direccion',
                            'velocidad no tiene sentido'
                        ]
                    },
                    {
                        'id': 'aceleracion_solo_mas_rapido',
                        'penalty': 0.10,
                        'keywords': [
                            'aceleracion es cuando vas mas rapido',
                            'aceleracion es solo cuando vas mas rapido',
                            'aceleracion es cuando vas rapido'
                        ]
                    },
                    {
                        'id': 'aceleracion_sin_direccion',
                        'penalty': 0.20,
                        'keywords': [
                            'aceleracion no tiene direccion',
                            'aceleracion sin direccion'
                        ]
                    }
                ]
            }
        }
