"""
SSEAR - Sistema Semántico de Evaluación Automatizada de Respuestas
Backend Principal - Flask Server
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import webbrowser
import threading
import logging

import config

# Importar módulos de análisis
from concept_analyzer import ConceptAnalyzer
from lexical_analyzer import LexicalAnalyzer
from feedback_generator import FeedbackGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
# Servir archivos estáticos (index.html, client.js, styles.css) desde la raíz
app = Flask(__name__, static_folder='.', static_url_path='')
# Permitir CORS explícitamente para las rutas de la API
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@app.route('/')
def index():
    return app.send_static_file('index.html')

# Inicializar analizadores
logger.info("Cargando modelos de IA...")
concept_analyzer = ConceptAnalyzer()
lexical_analyzer = LexicalAnalyzer()
feedback_generator = FeedbackGenerator()
logger.info("Modelos cargados exitosamente")


@app.before_request
def initialize_models():
    """Inicializa los modelos en la primera solicitud"""
    pass


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': True
    })


@app.route('/api/evaluate', methods=['POST'])
def evaluate_answer():
    """
    Endpoint principal de evaluación de respuestas
    
    Recibe:
        - reference_answer: str (respuesta de referencia/correcta)
        - student_answer: str (respuesta del estudiante a evaluar)
        - question: str (pregunta original, opcional)
        - context: str (contexto adicional, opcional)
    """
    try:
        data = request.json
        
        # Validar entrada
        if not data or 'reference_answer' not in data or 'student_answer' not in data or 'question' not in data:
            return jsonify({
                'error': 'Se requieren reference_answer, student_answer y question'
            }), 400
        
        reference = data.get('reference_answer', '').strip()
        student = data.get('student_answer', '').strip()
        question = data.get('question', '')
        context = data.get('context', '')
        
        if not reference or not student or not question:
            return jsonify({
                'error': 'La pregunta, la respuesta de referencia y la respuesta del estudiante no pueden estar vacías'
            }), 400
        
        logger.info(f"Evaluando respuesta: {student[:50]}...")
        
        # ========== ANÁLISIS SEMÁNTICO ==========
        semantic_results = concept_analyzer.analyze(question, reference, student)
        
        # ========== ANÁLISIS LÉXICO ==========
        lexical_results = lexical_analyzer.analyze(reference, student)
        
        # ========== CÁLCULO DE PUNTUACIONES ==========
        semantic_score = semantic_results['similarity']
        lexical_score = lexical_results['similarity']
        
        # Promedio ponderado estándar: 70% semántica + 30% léxica
        overall_score = (semantic_score * config.SEMANTIC_WEIGHT) + (lexical_score * config.LEXICAL_WEIGHT)
        
        # ========== GENERACIÓN DE RETROALIMENTACIÓN ==========
        feedback = feedback_generator.generate(
            reference_answer=reference,
            student_answer=student,
            semantic_results=semantic_results,
            lexical_results=lexical_results,
            overall_score=overall_score,
            question=question
        )
        
        # ========== CONSTRUCCIÓN DE RESPUESTA ==========
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'scores': {
                'semantic': round(semantic_score * 100, 2),
                'lexical': round(lexical_score * 100, 2),
                'overall': round(overall_score * 100, 2),
                'grade': round(overall_score * 10, 1),
                'grade_letter': get_grade_letter(overall_score)
            },
            'analysis': {
                'semantic': semantic_results,
                'lexical': lexical_results
            },
            'feedback': feedback,
            'metadata': {
                'reference_words': semantic_results['reference_tokens'],
                'student_words': semantic_results['student_tokens'],
                'matched_terms': lexical_results['matched_terms'],
                'missing_terms': lexical_results['missing_terms'],
                'extra_terms': lexical_results['extra_terms']
            }
        }
        
        logger.info(f"Evaluación completada - Puntuación: {overall_score:.2%}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error en evaluación: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error procesando la evaluación',
            'details': str(e)
        }), 500


@app.route('/api/batch-evaluate', methods=['POST'])
def batch_evaluate():
    """
    Evalúa múltiples respuestas de una vez
    
    Recibe:
        - evaluations: list of {reference_answer, student_answer}
    """
    try:
        data = request.json
        evaluations = data.get('evaluations', [])
        
        if not evaluations:
            return jsonify({'error': 'No hay evaluaciones'}), 400
        
        results = []
        for idx, eval_item in enumerate(evaluations, start=1):
            # Llamar a la lógica de evaluación existente
            request_data = {
                'reference_answer': eval_item.get('reference_answer', ''),
                'student_answer': eval_item.get('student_answer', ''),
                'question': eval_item.get('question', '')
            }

            # Validar campos obligatorios en cada elemento
            if not request_data['reference_answer'] or not request_data['student_answer'] or not request_data['question']:
                return jsonify({'error': f'El elemento {idx} del lote debe incluir reference_answer, student_answer y question'}), 400

            semantic_results = concept_analyzer.analyze(
                request_data['question'],
                request_data['reference_answer'],
                request_data['student_answer']
            )
            lexical_results = lexical_analyzer.analyze(
                request_data['reference_answer'],
                request_data['student_answer']
            )

            semantic_score = semantic_results['similarity']
            lexical_score = lexical_results['similarity']
            overall_score = (semantic_score * config.SEMANTIC_WEIGHT) + (lexical_score * config.LEXICAL_WEIGHT)

            results.append({
                'student_answer': request_data['student_answer'],
                'scores': {
                    'semantic': round(semantic_score * 100, 2),
                    'lexical': round(lexical_score * 100, 2),
                    'overall': round(overall_score * 100, 2),
                    'grade': round(overall_score * 10, 1),
                    'grade_letter': get_grade_letter(overall_score)
                }
            })
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error en evaluación por lotes: {str(e)}")
        return jsonify({
            'error': 'Error procesando evaluaciones',
            'details': str(e)
        }), 500


@app.route('/api/models-info', methods=['GET'])
def models_info():
    """Retorna información sobre los modelos cargados"""
    return jsonify({
        'semantic_model': 'sentence-transformers (distiluse-base-multilingual)',
        'lexical_model': 'spaCy + NLTK',
        'language': 'español',
        'offline': True,
        'models_loaded': True,
        'features': [
            'Similitud semántica',
            'Similitud léxica',
            'Análisis de palabras clave',
            'Retroalimentación automática',
            'Procesamiento en lote'
        ]
    }), 200


def get_grade_letter(score):
    """Convierte puntuación en rango 0-1 a calificación letra"""
    for letter, threshold in config.GRADE_THRESHOLDS.items():
        if score >= threshold:
            return letter
    return 'F'


def get_grade(score):
    """Convierte puntuación en rango 0-1 a calificación numérica 0-10"""
    return round(score * 10, 1)


if __name__ == '__main__':
    logger.info("Iniciando SSEAR - Sistema Semántico de Evaluación")
    # Abrir navegador externo automáticamente en localhost
    url = 'http://127.0.0.1:5000'
    logger.info(f"Servidor disponible en: {url}")

    # Abrir el navegador en una hebra separada para no bloquear el servidor
    def _open_browser():
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            pass

    threading.Timer(1.0, _open_browser).start()

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False,
        threaded=True
    )
