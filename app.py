"""
SSEAR - Sistema Semántico de Evaluación Automatizada de Respuestas
API Flask - Backend Principal
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import webbrowser
import threading

import config
from evaluation_engine import EvaluationEngine
from feedback_generator import FeedbackGenerator
from excel_logger import append_evaluation_to_excel

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Inicializar motor de evaluación
logger.info("Inicializando motor de evaluación...")
evaluation_engine = EvaluationEngine()
feedback_generator = FeedbackGenerator()
logger.info("Motor de evaluación cargado exitosamente")


# ============================================================
# RUTAS API
# ============================================================

@app.route('/')
def index():
    """Sirve la página principal"""
    return app.send_static_file('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica el estado del servicio"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': config.API_VERSION,
        'models_loaded': True,
        'cache_stats': evaluation_engine.get_cache_stats()
    }), 200


@app.route('/api/evaluate', methods=['POST'])
def evaluate_answer():
    """
    Endpoint principal de evaluación

    Entrada:
        {
            "question": "¿Qué es la fotosíntesis?",
            "reference_answer": "Respuesta correcta...",
            "student_answer": "Respuesta del alumno...",
            "context": "Contexto opcional"
        }
    """
    try:
        data = request.json or {}

        question  = data.get('question', '').strip()
        reference = data.get('reference_answer', '').strip()
        student   = data.get('student_answer', '').strip()
        context   = data.get('context', '').strip()

        if not all([question, reference, student]):
            return jsonify({
                'error': 'Se requieren: question, reference_answer, student_answer',
                'status': 'validation_error'
            }), 400

        logger.info(f"Evaluando respuesta: {student[:60]}...")

        evaluation_result = evaluation_engine.evaluate(
            question=question,
            reference_answer=reference,
            student_answer=student,
            context=context,
            use_cache=True
        )

        feedback = feedback_generator.generate(evaluation_result)
        append_evaluation_to_excel(
            question=question,
            reference_answer=reference,
            student_answer=student,
            evaluation_result=evaluation_result,
            feedback=feedback
        )

        # Exponer scores/analysis/metadata en top-level para el frontend
        scores   = evaluation_result.get('scores', {})
        analysis = evaluation_result.get('analysis', {})
        metadata = evaluation_result.get('metadata', {})

        response = {
            'status':    'success',
            'timestamp': datetime.now().isoformat(),
            'version':   config.API_VERSION,
            'cached':    evaluation_result.get('cached', False),
            # Top-level para compatibilidad con client.js
            'scores':    scores,
            'analysis':  analysis,
            'metadata':  metadata,
            'feedback':  feedback,
            # También incluir evaluation completo
            'evaluation': evaluation_result
        }

        logger.info(f"Evaluación completada - Score: {scores.get('percentage', 0):.1f}%")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error en evaluación: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'status': 'error',
            'details': str(e)
        }), 500


@app.route('/api/batch-evaluate', methods=['POST'])
def batch_evaluate():
    """Evalúa múltiples respuestas en lote"""
    try:
        data = request.json or {}
        evaluations = data.get('evaluations', [])

        if not evaluations:
            return jsonify({'error': 'Campo evaluations vacío', 'status': 'validation_error'}), 400

        if len(evaluations) > 100:
            return jsonify({'error': 'Máximo 100 evaluaciones por solicitud', 'status': 'validation_error'}), 400

        logger.info(f"Procesando lote de {len(evaluations)} evaluaciones...")

        results, errors = [], []

        for idx, eval_item in enumerate(evaluations, start=1):
            try:
                q = eval_item.get('question', '').strip()
                r = eval_item.get('reference_answer', '').strip()
                s = eval_item.get('student_answer', '').strip()
                c = eval_item.get('context', '').strip()

                if not all([q, r, s]):
                    errors.append({'index': idx, 'error': 'Campos requeridos faltantes'})
                    continue

                result = evaluation_engine.evaluate(
                    question=q, reference_answer=r, student_answer=s, context=c
                )
                results.append({
                    'index': idx,
                    'student_answer': s[:100],
                    'scores': result.get('scores', {}),
                    'grade': result.get('scores', {}).get('grade', 'F')
                })
            except Exception as e:
                logger.error(f"Error evaluando item {idx}: {str(e)}")
                errors.append({'index': idx, 'error': str(e)})

        return jsonify({
            'status': 'success' if not errors else 'partial_success',
            'timestamp': datetime.now().isoformat(),
            'total_processed': len(results),
            'total_errors': len(errors),
            'results': results,
            'errors': errors if errors else None
        }), 200 if not errors else 206

    except Exception as e:
        logger.error(f"Error en lote: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error procesando lote', 'status': 'error', 'details': str(e)}), 500


@app.route('/api/models-info', methods=['GET'])
def models_info():
    """Retorna información sobre los modelos y configuración"""
    return jsonify({
        'service': 'SSEAR - Sistema Semántico de Evaluación Automatizada de Respuestas',
        'version': config.API_VERSION,
        'language': 'Spanish',
        'offline_mode': True,
        'models': {
            'semantic': {
                'name': config.SEMANTIC_MODEL,
                'type': 'Transformer-based embeddings',
                'language': 'Multilingual'
            },
            'lexical': {
                'name': 'SnowballStemmer (NLTK)',
                'language': config.LEXICAL_LANGUAGE
            }
        },
        'weights': {
            'semantic': config.SEMANTIC_WEIGHT,
            'lexical':  config.LEXICAL_WEIGHT
        },
        'grade_thresholds': config.GRADE_THRESHOLDS,
        'constraints': {
            'min_reference_length': config.MIN_REFERENCE_LENGTH,
            'min_student_length':   config.MIN_STUDENT_LENGTH,
            'max_response_length':  config.MAX_RESPONSE_LENGTH,
            'cache_size':           config.CACHE_SIZE
        }
    }), 200


@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """Retorna estadísticas del caché"""
    return jsonify(evaluation_engine.get_cache_stats()), 200


@app.route('/api/cache/clear', methods=['POST'])
def cache_clear():
    """Limpia el caché"""
    evaluation_engine.clear_cache()
    return jsonify({'status': 'ok', 'message': 'Caché limpiado exitosamente'}), 200


# ============================================================
# INICIO DEL SERVIDOR
# ============================================================

def open_browser():
    """Abre el navegador automáticamente"""
    import time
    time.sleep(1.5)
    webbrowser.open(f'http://localhost:{config.SERVER_PORT}')


def run_server():
    logger.info(f"Iniciando servidor SSEAR en {config.SERVER_HOST}:{config.SERVER_PORT}")
    logger.info(f"Abre tu navegador en: http://localhost:{config.SERVER_PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    app.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=config.DEBUG_MODE,
        use_reloader=False
    )


if __name__ == '__main__':
    run_server()