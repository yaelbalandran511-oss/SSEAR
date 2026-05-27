"""
Evaluador de respuestas por ideas clave para la pregunta de los pulmones.

Requisitos de instalación:
    pip install nltk
    python -m nltk.downloader stopwords

Este script:
- utiliza ideas clave explícitas para cada pregunta
- detecta presencia de ideas mediante palabras clave y sinónimos
- aplica penalización por errores graves
- calcula similitud léxica con fórmula correcta
- genera salida detallada y retroalimentación
- muestra un ejemplo con múltiples preguntas en un bucle
"""

import re
import unicodedata
from collections import Counter

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import SnowballStemmer
    NLTK_AVAILABLE = True
except Exception:
    nltk = None
    stopwords = None
    SnowballStemmer = None
    NLTK_AVAILABLE = False


SPANISH_STOPWORDS = set()
STEMMER = None


def setup_nltk():
    global SPANISH_STOPWORDS, STEMMER
    if not NLTK_AVAILABLE:
        raise ImportError('Instala nltk: pip install nltk')

    try:
        stopwords.words('spanish')
    except LookupError:
        nltk.download('stopwords', quiet=True)

    try:
        SPANISH_STOPWORDS = set(stopwords.words('spanish'))
    except Exception:
        SPANISH_STOPWORDS = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'y', 'o', 'pero', 'que', 'de', 'del', 'al', 'en', 'por',
            'con', 'sin', 'para', 'se', 'es', 'su', 'sus', 'como',
            'mas', 'muy', 'a', 'lo', 'le', 'les', 'del', 'al'
        }

    try:
        STEMMER = SnowballStemmer('spanish')
    except Exception:
        STEMMER = None


def normalize_text(text):
    if text is None:
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


def stem_tokens(tokens):
    if STEMMER is None:
        return tokens
    return [STEMMER.stem(token) for token in tokens]


def phrase_present(phrase, text):
    return normalize_text(phrase) in normalize_text(text)


ideas_pulmones = {
    'idea1': {
        'texto': 'Los pulmones son los órganos principales del sistema respiratorio',
        'peso': 25,
        'palabras_clave': ['órganos principales', 'principales órganos', 'sistema respiratorio'],
        'sinonimos': ['órganos fundamentales', 'parte principal', 'sirven para respirar']
    },
    'idea2': {
        'texto': 'Intercambian gases / toman oxígeno del aire',
        'peso': 25,
        'palabras_clave': ['intercambian gases', 'toman oxígeno', 'absorben oxígeno', 'oxígeno del aire'],
        'sinonimos': ['captan oxígeno', 'recogen oxígeno']
    },
    'idea3': {
        'texto': 'Pasan oxígeno a la sangre',
        'peso': 25,
        'palabras_clave': ['pasan a la sangre', 'llevan a la sangre', 'oxígeno a la sangre', 'sangre'],
        'sinonimos': ['transportan oxígeno', 'envían oxígeno']
    },
    'idea4': {
        'texto': 'Eliminan dióxido de carbono',
        'peso': 25,
        'palabras_clave': ['eliminan dióxido', 'sacan dióxido', 'dióxido de carbono', 'expulsan co2', 'eliminan co2'],
        'sinonimos': ['remueven dióxido', 'descartan co2']
    }
}

errores_pulmones = [
    'los pulmones no sirven para respirar',
    'los pulmones producen oxígeno',
    'los pulmones están en la cabeza'
]


def evaluate_ideas(response, ideas):
    semantic_score = 0
    idea_results = []
    for idea_id, idea in ideas.items():
        present = False
        for keyword in idea['palabras_clave'] + idea.get('sinonimos', []):
            if phrase_present(keyword, response):
                present = True
                break
        if present:
            semantic_score += idea['peso']
        idea_results.append({
            'id': idea_id,
            'texto': idea['texto'],
            'peso': idea['peso'],
            'present': present
        })
    return max(semantic_score, 0), idea_results


def detect_errors(response, error_phrases):
    penalty = 0
    detected = []
    for phrase in error_phrases:
        if phrase_present(phrase, response):
            penalty += 20
            detected.append(phrase)
    return min(penalty, 100), detected


def lexical_similarity(reference, student):
    ref_tokens = tokenize(reference)
    stu_tokens = tokenize(student)
    ref_stems = stem_tokens(ref_tokens)
    stu_stems = stem_tokens(stu_tokens)
    common = sum((Counter(ref_stems) & Counter(stu_stems)).values())
    total = len(ref_stems) + len(stu_stems)
    score = round((2 * common / total) * 100, 1) if total > 0 else 0.0
    return {
        'score': score,
        'common': common,
        'ref_count': len(ref_stems),
        'stu_count': len(stu_stems),
        'ref_stems': ref_stems,
        'stu_stems': stu_stems
    }


def calculate_final_grade(semantic_score, lexical_score):
    semantic_percent = float(semantic_score)
    overall = round(0.80 * semantic_percent + 0.20 * lexical_score, 1)
    return overall, round(overall / 10, 1)


def format_feedback(idea_results):
    lines = []
    for idx, idea in enumerate(idea_results, start=1):
        status = 'presente' if idea['present'] else 'ausente'
        mark = '✓' if idea['present'] else '✗'
        lines.append(f"{mark} Idea {idx}: {idea['texto']} ({idea['peso']}%) - {status}")
    return lines


def evaluate_response(question, reference, response, ideas, errors):
    semantic_score, idea_results = evaluate_ideas(response, ideas)
    penalty, detected_errors = detect_errors(response, errors)
    semantic_after_penalty = max(semantic_score - penalty, 0)
    lexical = lexical_similarity(reference, response)
    overall, note = calculate_final_grade(semantic_after_penalty, lexical['score'])

    result = {
        'question': question,
        'reference': reference,
        'response': response,
        'semantic_score': semantic_score,
        'penalty': penalty,
        'semantic_after_penalty': semantic_after_penalty,
        'lexical': lexical['score'],
        'overall': overall,
        'note': note,
        'idea_results': idea_results,
        'errors_detected': detected_errors,
        'lexical_detail': lexical
    }
    return result


def print_evaluation(result):
    print('=== RESULTADOS ===')
    print('Ideas encontradas:')
    for line in format_feedback(result['idea_results']):
        print(line)
    print()
    print(f"Puntaje semántico: {result['semantic_score']}/100")
    print(f"Penalizaciones: {result['penalty']}")
    print(f"Semántica final: {result['semantic_after_penalty']}%")
    print()
    lexical = result['lexical_detail']
    coin = lexical['common']
    ref = lexical['ref_count']
    est = lexical['stu_count']
    porcentaje_palabras = round((2 * coin / (ref + est)) * 100, 1) if (ref + est) > 0 else 0.0
    print(f"Coincidencia de palabras: {coin}/{ref} ref, {coin}/{est} est → {porcentaje_palabras}%")
    print(f"Similitud léxica: {result['lexical']}%")
    print()
    sem = result['semantic_after_penalty']
    lex = result['lexical']
    print(f"Calificación final (80% sem + 20% lex): (0.8×{sem}) + (0.2×{lex}) = {result['overall']}%")
    print(f"Nota (0-10): {result['note']}/10")
    print()
    print('Retroalimentación para el estudiante:')
    for idea in result['idea_results']:
        if idea['present']:
            print(f"- ✅ Bien al decir: {idea['texto']}")
        else:
            print(f"- ❌ Te faltó explicar: {idea['texto']}")
    if result['errors_detected']:
        print('\nErrores graves detectados:')
        for err in result['errors_detected']:
            print(f"- {err}")
    print('\n' + '=' * 30 + '\n')


def run_example():
    templates = [
        {
            'question': '¿Cuál es la función de los pulmones en el sistema respiratorio?',
            'reference': (
                'Los pulmones son los órganos principales del sistema respiratorio. ' 
                'Intercambian gases y toman oxígeno del aire. ' 
                'Pasan oxígeno a la sangre y eliminan dióxido de carbono.'
            ),
            'ideas': ideas_pulmones,
            'errors': errores_pulmones
        }
    ]

    casos = [
        {
            'name': 'CASO A (estudiante bueno)',
            'response': (
                'Los pulmones sirven para respirar. Toman el oxígeno del aire y lo llevan a la sangre, ' 
                'y sacan el dióxido de carbono del cuerpo.'
            )
        },
        {
            'name': 'CASO B (estudiante malo)',
            'response': 'Los pulmones son para respirar. Están en el pecho.'
        }
    ]

    for template in templates:
        print(f"=== Pregunta: {template['question']} ===\n")
        for caso in casos:
            print(caso['name'])
            result = evaluate_response(
                template['question'],
                template['reference'],
                caso['response'],
                template['ideas'],
                template['errors']
            )
            print_evaluation(result)
            caso['result'] = result

        diff = abs(casos[0]['result']['overall'] - casos[1]['result']['overall'])
        print(f"DIFERENCIA ENTRE CASO A Y CASO B: {diff:.1f} puntos porcentuales")
        print('\n')


def main():
    setup_nltk()
    run_example()


if __name__ == '__main__':
    main()
