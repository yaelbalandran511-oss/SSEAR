"""
Demo ejecutable de evaluación por ideas clave y cálculo léxico exacto.
"""

import json
import re
import unicodedata
from collections import Counter


STOPWORDS = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'y', 'o', 'pero', 'que', 'de', 'del', 'al', 'en', 'por',
    'con', 'sin', 'para', 'se', 'es', 'su', 'sus', 'como',
    'más', 'muy', 'a', 'lo', 'le', 'les', 'del', 'al'
}

TEMPLATES = {
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

SEMANTIC_WEIGHT = 0.75
LEXICAL_WEIGHT = 0.25


def normalize_text(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def tokenize(text, remove_stopwords=True):
    normalized = normalize_text(text)
    tokens = normalized.split()
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


def simple_stem(token):
    suffixes = ['aciones', 'acion', 'ciones', 'cion', 'mente', 'ancias', 'ancia', 'encias', 'encia',
                'idades', 'idad', 'amiento', 'imiento', 'ador', 'adora', 'ante', 'ancia', 'encia',
                'able', 'ible', 'iva', 'ivo', 'ivos', 'ivas', 'ar', 'er', 'ir', 's']
    for suf in suffixes:
        if token.endswith(suf) and len(token) > len(suf) + 2:
            return token[:-len(suf)]
    return token


def stem_keyword(keyword):
    return ' '.join(simple_stem(token) for token in keyword.split())


def stem_text(text):
    return ' '.join(simple_stem(token) for token in text.split())


def lexical_similarity(reference, student, ignore_stopwords=True):
    ref_tokens = [simple_stem(t) for t in tokenize(reference, remove_stopwords=ignore_stopwords)]
    stu_tokens = [simple_stem(t) for t in tokenize(student, remove_stopwords=ignore_stopwords)]

    common = sum((Counter(ref_tokens) & Counter(stu_tokens)).values())
    if len(ref_tokens) + len(stu_tokens) == 0:
        return 0.0, ref_tokens, stu_tokens, common

    similarity = (2 * common) / (len(ref_tokens) + len(stu_tokens))
    return similarity * 100, ref_tokens, stu_tokens, common


def evaluate_concepts(question, reference, student):
    normalized = normalize_text(question + ' ' + reference)
    template = None
    for key, value in TEMPLATES.items():
        if key in normalized:
            template = value
            break

    if not template:
        return {
            'semantic': 0.0,
            'concepts': [],
            'penalty': 0.0,
            'template_name': 'fallback'
        }

    normalized_student = normalize_text(student)
    stemmed_student = stem_text(normalized_student)
    semantic_score = 0.0
    concept_details = []
    presence_map = {}

    for concept in template['concepts']:
        present = any(all(stem_keyword(keyword) in stemmed_student for keyword in group)
                      for group in concept['keywords'])
        presence_map[concept['id']] = present
        if present:
            semantic_score += concept['weight']
        concept_details.append({
            'id': concept['id'],
            'weight': concept['weight'],
            'present': present,
            'keywords': concept['keywords']
        })

    if not presence_map.get('conceptos_distintos'):
        if presence_map.get('velocidad_direccion') and presence_map.get('aceleracion_cambio_velocidad'):
            semantic_score += next(c['weight'] for c in template['concepts'] if c['id'] == 'conceptos_distintos')
            for detail in concept_details:
                if detail['id'] == 'conceptos_distintos':
                    detail['present'] = True
                    break

    penalty = 0.0
    for false_item in template['false_statements']:
        if any(keyword in normalized_student for keyword in false_item['keywords']):
            penalty += false_item['penalty']
    penalty = min(penalty, 0.20)
    corrected = max(0.0, semantic_score - penalty)

    return {
        'semantic': corrected * 100,
        'concept_score': semantic_score * 100,
        'penalty': penalty * 100,
        'concepts': concept_details,
        'template_name': template['name']
    }


def final_score(semantic, lexical):
    corrected_sem = semantic
    overall = SEMANTIC_WEIGHT * corrected_sem + LEXICAL_WEIGHT * lexical
    grade_10 = overall / 10
    return round(overall, 1), round(grade_10, 1)


def grade_label(score_100):
    if score_100 >= 90:
        return 'Sobresaliente'
    if score_100 >= 75:
        return 'Notable'
    if score_100 >= 60:
        return 'Aprobado'
    if score_100 >= 40:
        return 'Insuficiente'
    return 'Muy deficiente'


def evaluate(question, reference, student):
    concept_result = evaluate_concepts(question, reference, student)
    lexical, ref_tokens, stu_tokens, common = lexical_similarity(reference, student, ignore_stopwords=True)
    overall, grade_10 = final_score(concept_result['semantic'], lexical)

    return {
        'question': question,
        'reference': reference,
        'student': student,
        'semantic': round(concept_result['semantic'], 1),
        'lexical': round(lexical, 1),
        'overall_percent': overall,
        'grade_10': grade_10,
        'grade_label': grade_label(overall),
        'details': {
            'concepts': concept_result['concepts'],
            'penalty': concept_result['penalty'],
            'lexical': {
                'reference_tokens': len(ref_tokens),
                'student_tokens': len(stu_tokens),
                'common_tokens': common,
                'ref_tokens': ref_tokens,
                'stu_tokens': stu_tokens
            }
        }
    }


def main():
    question = 'Diferencia entre velocidad y aceleración'
    reference = 'Velocidad es rapidez con dirección. Aceleración es el cambio de velocidad en el tiempo. La aceleración incluye aumentar, disminuir o cambiar dirección. Son conceptos distintos.'
    student_a = 'Velocidad es qué tan rápido se mueve algo y hacia dónde. Aceleración es qué tan rápido cambia esa velocidad, ya sea aumentando, bajando o cambiando de dirección.'
    student_b = 'Velocidad es lo rápido que algo se mueve. Aceleración es cuando vas más rápido. No tienen dirección.'

    result_a = evaluate(question, reference, student_a)
    result_b = evaluate(question, reference, student_b)

    print('Estudiante A:', json.dumps(result_a, indent=2, ensure_ascii=False))
    print('\nEstudiante B:', json.dumps(result_b, indent=2, ensure_ascii=False))
    print('\nDiferencia entre A y B:', round(result_a['overall_percent'] - result_b['overall_percent'], 1), 'puntos')


if __name__ == '__main__':
    main()
