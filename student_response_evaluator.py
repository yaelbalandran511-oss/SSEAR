"""
Evaluador de respuestas de estudiantes para preguntas tipo texto libre.

Requisitos de instalación:
    pip install nltk
    python -m nltk.downloader stopwords

Uso:
    python student_response_evaluator.py

Este script calcula:
- similitud léxica exacta con fórmula estándar
- similitud semántica basada en ideas clave
- penalización por errores conceptuales graves
- calificación final 0-100 y nota 0-10
- resultados en JSON
"""

import json
import re
import unicodedata
from collections import Counter

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    NLTK_AVAILABLE = True
except Exception:
    nltk = None
    stopwords = None
    PorterStemmer = None
    NLTK_AVAILABLE = False


def ensure_stopwords():
    global SPANISH_STOPWORDS
    if NLTK_AVAILABLE:
        try:
            stopwords.words('spanish')
        except LookupError:
            nltk.download('stopwords')
        try:
            SPANISH_STOPWORDS = set(stopwords.words('spanish'))
            return
        except Exception:
            pass

    SPANISH_STOPWORDS = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'y', 'o', 'pero', 'que', 'de', 'del', 'al', 'en', 'por',
        'con', 'sin', 'para', 'se', 'es', 'su', 'sus', 'como',
        'mas', 'muy', 'a', 'lo', 'le', 'les', 'del', 'al'
    }


def get_stemmer():
    if NLTK_AVAILABLE and PorterStemmer is not None:
        return PorterStemmer()
    return None


SPANISH_STOPWORDS = set()
ensure_stopwords()
STEMMER = get_stemmer()

FALSE_ERRORS = [
    {
        'id': 'velocidad_sin_direccion',
        'penalty': 20,
        'patterns': [
            'velocidad no tiene direccion',
            'velocidad sin direccion',
            'velocidad no tiene sentido',
            'sin direccion'  # catch variants
        ]
    },
    {
        'id': 'aceleracion_sin_direccion',
        'penalty': 20,
        'patterns': [
            'aceleracion no tiene direccion',
            'aceleracion sin direccion',
            'aceleracion no tiene sentido'
        ]
    },
    {
        'id': 'aceleracion_solo_mas_rapido',
        'penalty': 10,
        'patterns': [
            'aceleracion es cuando vas mas rapido',
            'aceleracion es solo cuando vas mas rapido',
            'aceleracion es cuando vas rapido',
            'aceleracion es solo cuando vas rapido',
            'solo cuando vas mas rapido'
        ]
    }
]

IDEAS_VELOCIDAD_ACELERACION = [
    {
        'id': 'idea1',
        'label': 'Velocidad incluye dirección',
        'weight': 25,
        'keywords': [
            'direccion', 'hacia donde', 'hacia dónde', 'vectorial', 'sentido'
        ]
    },
    {
        'id': 'idea2',
        'label': 'Aceleración es cambio de velocidad',
        'weight': 25,
        'keywords': [
            'cambio', 'varia', 'varía', 'modifica', 'aumenta', 'disminuye', 'velocidad'
        ]
    },
    {
        'id': 'idea3',
        'label': 'Aceleración incluye frenar o cambiar dirección',
        'weight': 25,
        'keywords': [
            'disminuye', 'baja', 'frena', 'desacelera', 'cambia direccion', 'cambiar direccion', 'curva'
        ]
    },
    {
        'id': 'idea4',
        'label': 'Diferencia entre ambos conceptos',
        'weight': 25,
        'keywords': [
            'diferencia', 'distinto', 'mientras', 'en cambio', 'no es lo mismo'
        ]
    }
]


def normalize_text(text):
    if not text:
        return ''
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def tokenize(text, remove_stopwords=True):
    normalized = normalize_text(text)
    tokens = normalized.split()
    if remove_stopwords:
        tokens = [token for token in tokens if token not in SPANISH_STOPWORDS]
    return tokens


def stem_token(token):
    if STEMMER is None:
        return token
    return STEMMER.stem(token)


def stem_tokens(tokens):
    return [stem_token(token) for token in tokens]


def lexical_similarity(reference, student, remove_stopwords=True):
    ref_tokens = tokenize(reference, remove_stopwords=remove_stopwords)
    stu_tokens = tokenize(student, remove_stopwords=remove_stopwords)

    ref_stems = stem_tokens(ref_tokens)
    stu_stems = stem_tokens(stu_tokens)

    common = sum((Counter(ref_stems) & Counter(stu_stems)).values())
    total = len(ref_stems) + len(stu_stems)
    if total == 0:
        score = 0.0
    else:
        score = (2 * common / total) * 100

    return {
        'score': round(score, 1),
        'ref_tokens': ref_tokens,
        'stu_tokens': stu_tokens,
        'ref_stems': ref_stems,
        'stu_stems': stu_stems,
        'common_stems': common,
        'total_ref': len(ref_stems),
        'total_stu': len(stu_stems)
    }


def extract_ideas(question, reference, student):
    normalized_student = normalize_text(student)
    idea_results = []
    found = 0

    for idea in IDEAS_VELOCIDAD_ACELERACION:
        present = False
        student_stems = stem_tokens(tokenize(student, remove_stopwords=False))
        for keyword in idea['keywords']:
            keyword_norm = normalize_text(keyword)
            if keyword_norm in normalized_student:
                present = True
                break
            keyword_stems = stem_tokens(tokenize(keyword, remove_stopwords=False))
            if keyword_stems and all(stem in student_stems for stem in keyword_stems):
                present = True
                break
        if present:
            found += 1
        idea_results.append({
            'id': idea['id'],
            'label': idea['label'],
            'weight': idea['weight'],
            'present': present,
            'keywords': idea['keywords']
        })

    semantic_score = found * 25
    return {
        'score': semantic_score,
        'found': found,
        'total': len(IDEAS_VELOCIDAD_ACELERACION),
        'ideas': idea_results
    }


def detect_errors(student):
    normalized_student = normalize_text(student)
    errors = []
    penalty = 0

    for item in FALSE_ERRORS:
        for pattern in item['patterns']:
            if pattern in normalized_student:
                errors.append({
                    'id': item['id'],
                    'pattern': pattern,
                    'penalty': item['penalty']
                })
                penalty += item['penalty']
                break

    return {
        'errors': errors,
        'penalty': penalty
    }


def final_grade(semantic_ideas, lexical_score, penalty):
    sem_corrected = max(0, semantic_ideas - penalty)
    overall = 0.75 * sem_corrected + 0.25 * lexical_score
    note = overall / 10
    return {
        'semantic_corrected': round(sem_corrected, 1),
        'lexical': round(lexical_score, 1),
        'overall': round(overall, 1),
        'note_10': round(note, 1)
    }


def recalibrar_nota(puntaje_actual):
    if puntaje_actual >= 50:
        return round(min(100.0, 20 + (puntaje_actual - 20) * 1.3), 1)
    return round(puntaje_actual * 0.75, 1)


def evaluate_response(question, reference, student):
    lex = lexical_similarity(reference, student)
    ideas = extract_ideas(question, reference, student)
    errors = detect_errors(student)
    final = final_grade(ideas['score'], lex['score'], errors['penalty'])
    recalibrated_overall = recalibrar_nota(final['overall'])
    recalibrated_note = round(recalibrated_overall / 10, 1)

    return {
        'question': question,
        'reference': reference,
        'student': student,
        'semantic_raw': ideas['score'],
        'semantic_corrected': final['semantic_corrected'],
        'lexical': lex['score'],
        'overall_percent': final['overall'],
        'note_10': final['note_10'],
        'recalibrated_overall': recalibrated_overall,
        'recalibrated_note_10': recalibrated_note,
        'ideas': ideas['ideas'],
        'errors': errors['errors'],
        'penalty': errors['penalty'],
        'lexical_details': {
            'palabras_ref': lex['total_ref'],
            'palabras_est': lex['total_stu'],
            'palabras_comunes': lex['common_stems'],
            'ref_stems': lex['ref_stems'],
            'stu_stems': lex['stu_stems']
        }
    }


def print_result(result):
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    question = 'Diferencia entre velocidad y aceleración'
    reference = (
        'La velocidad es una magnitud vectorial que indica el cambio de posición de un objeto en un tiempo determinado, '
        'incluyendo dirección y sentido. La aceleración es el cambio de la velocidad en el tiempo, es decir, '
        'qué tan rápido aumenta o disminuye la velocidad.'
    )

    student_a = (
        'Velocidad es qué tan rápido se mueve algo y hacia dónde. '
        'Aceleración es qué tan rápido cambia esa velocidad, ya sea aumentando, bajando o cambiando de dirección.'
    )
    student_b = (
        'Velocidad es lo rápido que algo se mueve. '
        'Aceleración es cuando vas más rápido. No tienen dirección.'
    )

    print('=== CASO A (estudiante bueno) ===')
    result_a = evaluate_response(question, reference, student_a)
    print_result(result_a)

    print('\n=== CASO B (estudiante malo) ===')
    result_b = evaluate_response(question, reference, student_b)
    print_result(result_b)

    diff = result_a['overall_percent'] - result_b['overall_percent']
    print(f'\nDiferencia A-B: {diff:.1f} puntos porcentuales')


if __name__ == '__main__':
    main()
