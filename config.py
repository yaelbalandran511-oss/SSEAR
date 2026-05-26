"""
Configuración de SSEAR
"""

import os

# Configuración del servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
DEBUG_MODE = True
WORKERS = 1

# Configuración de modelos
SEMANTIC_MODEL = 'distiluse-base-multilingual-cased-v2'
LEXICAL_LANGUAGE = 'spanish'

# Ponderación de puntuaciones (deben sumar 1.0)
SEMANTIC_WEIGHT = 0.6
LEXICAL_WEIGHT = 0.4

# Configuración de validación
MIN_REFERENCE_LENGTH = 10  # Caracteres mínimos en respuesta de referencia
MIN_STUDENT_LENGTH = 5     # Caracteres mínimos en respuesta del estudiante
MAX_RESPONSE_LENGTH = 10000  # Caracteres máximos

# Configuración de feedback
GENERATE_DETAILED_FEEDBACK = True
MAX_SUGGESTIONS = 5
MAX_ACTION_ITEMS = 5

# Directorios
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')

# Crear directorios si no existen
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Caché
ENABLE_CACHE = True
CACHE_SIZE = 1000  # Máximo de evaluaciones en caché

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Calificaciones
GRADE_THRESHOLDS = {
    'A': 0.90,
    'B': 0.80,
    'C': 0.70,
    'D': 0.60,
    'F': 0.00
}

# Mensajes personalizados
FEEDBACK_TEMPLATES = {
    'excellent': 'Excelente respuesta que demuestra comprensión profunda del tema.',
    'very_good': 'Muy buena respuesta con elementos clave correctamente identificados.',
    'good': 'Buena respuesta que satisface los requisitos básicos.',
    'acceptable': 'Respuesta aceptable pero que requiere más detalle y precisión.',
    'needs_improvement': 'Respuesta incompleta que necesita mejora significativa.',
    'insufficient': 'Respuesta que requiere revisión completa.'
}

# CORS
CORS_ENABLED = True
CORS_ORIGINS = '*'

# Rate limiting (si se implementa en futuro)
RATE_LIMIT_ENABLED = False
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 3600  # segundos

# API
API_VERSION = '1.0.0'
API_TIMEOUT = 30  # segundos
