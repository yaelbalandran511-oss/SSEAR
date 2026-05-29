"""
SSEAR - Configuración Central
"""

import os

# ============================================================
# SERVIDOR
# ============================================================
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
DEBUG_MODE = True
WORKERS = 1

# ============================================================
# MODELOS
# ============================================================
SEMANTIC_MODEL = 'distiluse-base-multilingual-cased-v2'
LEXICAL_LANGUAGE = 'spanish'

# ============================================================
# PONDERACIONES (deben sumar 1.0)
# ============================================================
SEMANTIC_WEIGHT = 0.85   # 85% análisis semántico (menos estricto)
LEXICAL_WEIGHT  = 0.15   # 15% análisis léxico

# ============================================================
# VALIDACIÓN
# ============================================================
MIN_REFERENCE_LENGTH = 5    # Caracteres mínimos en respuesta de referencia
MIN_STUDENT_LENGTH   = 3    # Caracteres mínimos en respuesta del estudiante
MAX_RESPONSE_LENGTH  = 10000

# ============================================================
# CACHÉ
# ============================================================
ENABLE_CACHE = True
CACHE_SIZE   = 1000

# ============================================================
# CALIFICACIONES
# ============================================================
GRADE_THRESHOLDS = {
    'A': 0.85,   # 85-100%
    'B': 0.70,   # 70-84%
    'C': 0.55,   # 55-69%
    'D': 0.40,   # 40-54%
    'F': 0.00    # 0-39%
}

GRADE_LABELS = {
    'A': 'Excelente',
    'B': 'Muy Bien',
    'C': 'Suficiente',
    'D': 'Necesita Mejora',
    'F': 'Insuficiente'
}

# ============================================================
# FEEDBACK
# ============================================================
GENERATE_DETAILED_FEEDBACK = True
MAX_SUGGESTIONS  = 5
MAX_ACTION_ITEMS = 5

# ============================================================
# DIRECTORIOS
# ============================================================
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
LOGS_DIR   = os.path.join(os.path.dirname(__file__), 'logs')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR,   exist_ok=True)

# ============================================================
# RATE LIMITING (futuro)
# ============================================================
RATE_LIMIT_ENABLED  = False
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD   = 3600  # segundos

# ============================================================
# API
# ============================================================
API_VERSION = '2.0.0'
API_TIMEOUT = 30

# ============================================================
# LOGGING
# ============================================================
LOG_LEVEL  = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================
# MENSAJES DE RETROALIMENTACIÓN
# ============================================================

GRADE_LABELS = {
    'A': 'Excelente',
    'B': 'Bueno',
    'C': 'Suficiente',
    'D': 'Deficiente',
    'F': 'Insuficiente'
}

FEEDBACK_MESSAGES = {
    'excellent':        'Tu respuesta demuestra un dominio sobresaliente del tema.',
    'very_good':        'Tu respuesta es muy buena y cubre los aspectos principales.',
    'good':             'Tu respuesta es correcta pero puede mejorar con más detalle.',
    'acceptable':       'Tu respuesta cubre algunos aspectos, pero le faltan elementos clave.',
    'needs_improvement':'Tu respuesta necesita mayor desarrollo y precisión.',
    'insufficient':     'Tu respuesta no cubre los aspectos fundamentales del tema.'
}