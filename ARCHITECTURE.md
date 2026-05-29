"""
ARQUITECTURA DE SSEAR - Sistema Semántico de Evaluación Automatizada de Respuestas
Documento técnico de referencia - Mayo 2026
"""

# ==============================================================
# ARQUITECTURA DEL SISTEMA
# ==============================================================

## 1. CAPAS DE LA APLICACIÓN

┌─────────────────────────────────────────────────────────────┐
│                    CAPA PRESENTACIÓN                        │
│  (index.html, client.js, styles.css - Frontend Web)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    CAPA API REST                            │
│  (app.py - Flask con endpoints JSON)                        │
│  - /api/evaluate              (POST)                        │
│  - /api/batch-evaluate        (POST)                        │
│  - /api/health                (GET)                         │
│  - /api/models-info           (GET)                         │
│  - /api/cache/*               (GET/POST)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                CAPA DE LÓGICA DE NEGOCIO                    │
│  (evaluation_engine.py - Motor de Evaluación)              │
│                                                             │
│  - Validación de entrada (utils.validate_input)            │
│  - Evaluación integrada                                    │
│  - Caché de resultados                                     │
│  - Cálculo de puntuaciones                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CAPA DE ANÁLISIS (PARALELO)                    │
│                                                             │
│  ┌──────────────────┬──────────────────┬─────────────────┐ │
│  │  Semántico       │  Léxico          │  Conceptual    │ │
│  │  (75%)           │  (25%)           │  (Referencia)  │ │
│  │                  │                  │                │ │
│  │  semantic_       │  lexical_        │  concept_      │ │
│  │  analyzer.py     │  analyzer.py     │  analyzer.py   │ │
│  │                  │                  │                │ │
│  │  - Transformers  │  - Stemming      │  - Plantillas  │ │
│  │  - Embeddings    │  - Palabras clave│  - Conceptos   │ │
│  │  - Similitud     │  - Diccionarios  │  - Matching    │ │
│  └──────────────────┴──────────────────┴─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          CAPA DE RETROALIMENTACIÓN                          │
│  (feedback_generator.py)                                    │
│                                                             │
│  - Generador de resumen                                    │
│  - Identificador de fortalezas                             │
│  - Identificador de debilidades                            │
│  - Generador de sugerencias                                │
│  - Generador de puntos de acción                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CAPA DE DATOS Y CONFIGURACIÓN                  │
│  (config.py, utils.py)                                      │
│                                                             │
│  - Parámetros del sistema                                  │
│  - Umbrales de calificación                                │
│  - Ponderaciones                                           │
│  - Funciones de utilidad                                   │
└─────────────────────────────────────────────────────────────┘


## 2. FLUJO DE DATOS DETALLADO

### 2.1 Evaluación Simple

```
Cliente HTTP
    ↓
POST /api/evaluate
    {
        "question": "¿Qué es X?",
        "reference_answer": "Respuesta modelo",
        "student_answer": "Respuesta estudiante"
    }
    ↓
app.py :: evaluate_answer()
    ↓
Validación → validate_input(reference, student, question)
    ↓ (si es válido)
EvaluationEngine.evaluate()
    ↓
┌─ Verificar caché
│   ├─ Si HIT: retornar resultado + {cached: true}
│   └─ Si MISS: continuar
└─ _run_evaluation()
    │
    ├─ Análisis Semántico
    │   └─ SemanticAnalyzer.analyze()
    │       └─ Embeddings + similitud coseno
    │
    ├─ Análisis Léxico
    │   └─ LexicalAnalyzer.analyze()
    │       └─ Tokenización + matching
    │
    ├─ Análisis de Conceptos
    │   └─ ConceptAnalyzer.analyze()
    │       └─ Template matching
    │
    ├─ Cálculo de puntuación
    │   └─ final_score = (semantic * 0.75) + (lexical * 0.25)
    │
    ├─ Determinación de grado
    │   └─ grade = thresholds[final_score]
    │
    └─ Guardar en caché
        └─ cache.set(reference, student, result)

FeedbackGenerator.generate(evaluation_result)
    ├─ Resumen
    ├─ Analysis Breakdown
    ├─ Strengths
    ├─ Weaknesses
    ├─ Suggestions
    ├─ Action Items
    └─ Detailed Analysis

Respuesta JSON
    ↓
Cliente HTTP
```

### 2.2 Evaluación en Lote

```
POST /api/batch-evaluate
    {
        "evaluations": [
            {query1},
            {query2},
            ...
            {queryN}
        ]
    }
    ↓
Para cada evaluación en paralelo:
    ├─ Validar entrada
    ├─ Ejecutar evaluate()
    ├─ Recopilar resultado
    └─ Guardar en caché
    ↓
Compilar resultados
    ├─ Total procesadas
    ├─ Errores
    └─ Resultados[N]
    ↓
Respuesta JSON con status (200 o 206)
```


## 3. COMPONENTES PRINCIPALES

### 3.1 evaluation_engine.py

**Clase: EvaluationEngine**

```python
class EvaluationEngine:
    def __init__(self):
        # Inicializar analizadores
        self.semantic_analyzer = SemanticAnalyzer()
        self.lexical_analyzer = LexicalAnalyzer()
        self.concept_analyzer = ConceptAnalyzer()
        
        # Ponderaciones
        self.semantic_weight = 0.75
        self.lexical_weight = 0.25
        
        # Caché
        self.cache = EvaluationCache()
    
    def evaluate(question, reference, student, context):
        # Pipeline principal
        
    def _run_evaluation(question, reference, student, context):
        # Ejecuta análisis paralelos
        
    def _calculate_grade(score):
        # Determina A-F basado en score 0-1
    
    def batch_evaluate(evaluations):
        # Procesa lote de evaluaciones
    
    def get_cache_stats():
        # Retorna estadísticas
    
    def clear_cache():
        # Limpia caché
```

**Clase: EvaluationCache**

```python
class EvaluationCache:
    def __init__(max_size=1000):
        # Inicializa caché FIFO
    
    def get_key(reference, student):
        # Hash MD5 de la combinación
    
    def get(reference, student):
        # Obtiene del caché si existe
    
    def set(reference, student, result):
        # Almacena resultado
    
    def clear():
        # Limpia todo el caché
```

### 3.2 semantic_analyzer.py

```python
class SemanticAnalyzer:
    def __init__(self):
        # Carga modelo: distiluse-base-multilingual-cased-v2
        self.model = SentenceTransformer(model_name)
    
    def analyze(reference_text, student_text):
        # 1. Genera embeddings de ambos textos
        # 2. Calcula similitud coseno (0-1)
        # 3. Retorna {similarity: 0.0-1.0, ...}
```

Puntuación: 0.0 a 1.0 (0-100%)

### 3.3 lexical_analyzer.py

```python
class LexicalAnalyzer:
    def analyze(reference_text, student_text):
        # 1. Tokenización y normalización
        # 2. Extrae palabras clave
        # 3. Calcula coincidencia (Jaccard/Dice)
        # 4. Identifica términos faltantes
        # 5. Retorna {
        #      similarity: 0.0-1.0,
        #      matched_terms: [...],
        #      missing_terms: [...]
        #    }
```

Puntuación: 0.0 a 1.0 (0-100%)

### 3.4 concept_analyzer.py

```python
class ConceptAnalyzer:
    def analyze(question, reference, student):
        # 1. Selecciona plantilla según pregunta
        # 2. Extrae conceptos esperados
        # 3. Verifica presencia en respuesta
        # 4. Calcula puntuación ponderada
        # 5. Aplica penalizaciones si es necesario
        # 6. Retorna {
        #      similarity: 0.0-1.0,
        #      concepts: [...],
        #      penalty: 0.0-1.0
        #    }
```

Puntuación: 0.0 a 1.0 (0-100%)

### 3.5 feedback_generator.py

```python
class FeedbackGenerator:
    def generate(evaluation_result):
        # Recibe resultado completo de evaluación
        # Retorna {
        #     summary: {...},
        #     analysis_breakdown: {...},
        #     strengths: [...],
        #     weaknesses: [...],
        #     suggestions: [...],
        #     action_items: [...],
        #     detailed_analysis: {...}
        # }
```

### 3.6 utils.py

```python
def normalize_text(text):
    # Normaliza para análisis
    
def validate_input(reference, student, question):
    # Valida entrada completa
    
class TextCleaner:
    # Limpieza de texto
    
class TextStatistics:
    # Estadísticas de texto
    
class SimilarityUtils:
    # Funciones de similitud
    
class ValidationUtils:
    # Utilidades de validación
    
class PerformanceMonitor:
    # Monitoreo de tiempo
```

### 3.7 config.py

```python
# Ponderaciones
SEMANTIC_WEIGHT = 0.75
LEXICAL_WEIGHT = 0.25

# Umbrales
MIN_REFERENCE_LENGTH = 10
MIN_STUDENT_LENGTH = 5
MAX_RESPONSE_LENGTH = 10000

# Caché
ENABLE_CACHE = True
CACHE_SIZE = 1000

# Calificaciones
GRADE_THRESHOLDS = {
    'A': 0.90,
    'B': 0.80,
    'C': 0.70,
    'D': 0.60,
    'F': 0.00
}

# Otros
SEMANTIC_MODEL = 'distiluse-base-multilingual-cased-v2'
LEXICAL_LANGUAGE = 'spanish'
API_VERSION = '1.0.0'
```


## 4. FLUJO DE PUNTUACIÓN

```
semantic_score (0-1) ──┐
                        ├─ ×0.75 ┐
                        │         ├─ SUM ─┐
lexical_score (0-1) ───┤         │        │
                        ├─ ×0.25 ┤        │
                        │         ┘        ├─→ final_score (0-1)
                        │                  │
                        └─────────────────┘
                        
                final_score × 100 = percentage (0-100%)
                percentage → GRADE_THRESHOLDS → grade (A-F)
```


## 5. ESTRUCTURA DE DATOS DE ENTRADA/SALIDA

### 5.1 Entrada (POST /api/evaluate)

```json
{
  "question": "string (requerido, min 5 chars)",
  "reference_answer": "string (requerido, min 10 chars, max 10000)",
  "student_answer": "string (requerido, min 5 chars, max 10000)",
  "context": "string (opcional)"
}
```

### 5.2 Salida (200 OK)

```json
{
  "status": "success",
  "timestamp": "ISO 8601",
  "cached": false,
  "evaluation": {
    "scores": {
      "semantic": 0.85,
      "lexical": 0.72,
      "final": 0.8215,
      "percentage": 82.15,
      "grade": "B"
    },
    "analysis": {
      "semantic": {...},
      "lexical": {...},
      "concept": {...}
    },
    "metadata": {...}
  },
  "feedback": {
    "summary": {...},
    "analysis_breakdown": {...},
    "strengths": [...],
    "weaknesses": [...],
    "suggestions": [...],
    "action_items": [...]
  }
}
```

### 5.3 Error (400/500)

```json
{
  "status": "error|validation_error",
  "error": "Descripción del error",
  "details": "Detalles técnicos (opcional)"
}
```


## 6. PIPELINE DE VALIDACIÓN

```
Input JSON
    ↓
¿question existe? ──NO→ ERROR 400
    ↓ SÍ
¿reference_answer existe? ──NO→ ERROR 400
    ↓ SÍ
¿student_answer existe? ──NO→ ERROR 400
    ↓ SÍ
validate_input(reference, student, question)
    ├─ ¿es string? ──NO→ ERROR
    ├─ len(reference) ≥ 10? ──NO→ ERROR
    ├─ len(student) ≥ 5? ──NO→ ERROR
    ├─ len(question) ≤ 10000? ──NO→ ERROR
    └─ SÍ a todos → VÁLIDO ✓
    ↓
Proceder con evaluación
```


## 7. OPTIMIZACIONES

### 7.1 Caché

- **Clave**: MD5(reference + student)
- **Valor**: Resultado completo
- **Estrategia**: FIFO (First In First Out)
- **Tamaño máximo**: 1000 entradas
- **Hit rate esperado**: 20-40% en uso típico

### 7.2 Procesamiento

- **Análisis paralelo**: Los 3 analizadores corren sin esperar
- **Lazy loading**: Modelos cargados bajo demanda
- **Normalización cacheable**: Reutiliza normalizaciones

### 7.3 Memoria

- **Batch limit**: Máximo 100 evaluaciones por solicitud
- **Garbage collection**: Limpieza automática
- **Pool de conexiones**: Reutiliza conexiones


## 8. CONFIGURACIÓN POR ESCENARIOS

### 8.1 Desarrollo

```python
DEBUG_MODE = True
CACHE_SIZE = 100
SEMANTIC_WEIGHT = 0.75
LEXICAL_WEIGHT = 0.25
```

### 8.2 Producción

```python
DEBUG_MODE = False
CACHE_SIZE = 5000
SEMANTIC_WEIGHT = 0.75
LEXICAL_WEIGHT = 0.25
LOG_LEVEL = 'WARNING'
```

### 8.3 Énfasis Semántico

```python
SEMANTIC_WEIGHT = 0.85
LEXICAL_WEIGHT = 0.15
```

### 8.4 Énfasis Léxico

```python
SEMANTIC_WEIGHT = 0.60
LEXICAL_WEIGHT = 0.40
```


## 9. CASOS DE USO

### 9.1 Evaluación Individual

```
Profesor evalúa respuesta de 1 estudiante
→ POST /api/evaluate
→ Retorna evaluación + retroalimentación
→ Profesor ve grado, sugerencias, fortalezas/debilidades
```

### 9.2 Evaluación de Clase

```
Profesor evalúa respuestas de 30 estudiantes
→ POST /api/batch-evaluate (máx 100)
→ Retorna lista de resultados
→ Profesor genera reporte
```

### 9.3 Integración LMS

```
Sistema educativo llama a SSEAR
→ Sistema envía {question, reference, student}
→ SSEAR retorna JSON
→ Sistema integra en base de datos
→ Genera reportes automáticos
```

### 9.4 Autoevaluación de Estudiante

```
Estudiante ingresa respuesta
→ Sistema evalúa contra referencia
→ Muestra retroalimentación inmediata
→ Estudiante mejora y reenvía
→ Proceso iterativo hasta mejorar
```


## 10. ESTADÍSTICAS DE PERFORMANCE

### Tiempo de Respuesta Típico

| Operación | Tiempo |
|-----------|--------|
| Evaluación simple | 200-500ms |
| Batch (10 items) | 2-5 seg |
| Batch (100 items) | 20-50 seg |
| Cache hit | <10ms |

### Utilización de Memoria

| Componente | Uso |
|-----------|-----|
| Modelos cargados | ~800MB |
| Caché (1000 items) | ~100MB |
| Proceso Flask | ~200MB |
| **Total típico** | **~1.1GB** |

### Throughput

- **Concurrencia**: Soporta ~10-50 solicitudes simultáneas
- **RPS**: ~10-20 evaluaciones por segundo
- **Bottleneck**: Modelos (no I/O)


## 11. SEGURIDAD

### 11.1 Validación

- ✓ Longitud de entrada
- ✓ Tipo de dato (string)
- ✓ Caracteres especiales
- ✓ Inyección de código

### 11.2 Rate Limiting

- Configurar en nginx si es necesario
- Por defecto: sin límite (configurable)

### 11.3 CORS

- Habilitado para desarrollo
- Editable en `app.py`


## 12. EXTENSIBILIDAD

### Agregar Nuevo Analizador

1. Crear clase `NewAnalyzer`
2. Implementar `analyze(ref, student)` → Dict
3. En `evaluation_engine.py`:
   ```python
   new_analyzer = NewAnalyzer()
   new_results = new_analyzer.analyze(...)
   # Integrar en resultado final
   ```

### Cambiar Modelo Semántico

```python
# En config.py
SEMANTIC_MODEL = 'other-model-name'

# En semantic_analyzer.py
self.model = SentenceTransformer(config.SEMANTIC_MODEL)
```

### Personalizar Ponderaciones

```python
# En config.py
SEMANTIC_WEIGHT = 0.80
LEXICAL_WEIGHT = 0.20
```

---

**Documento: ARQUITECTURA.md**  
**Última actualización**: Mayo 2026  
**Versión**: 1.0.0
