# SSEAR — Descripción técnica del modelo y del sistema

Este documento describe cómo funciona internamente SSEAR, qué algoritmos utiliza y qué clases de métricas son relevantes para este proyecto.

## Arquitectura general

SSEAR es un sistema de evaluación de respuestas abiertas que funciona como una aplicación local.

- El backend es un servidor Flask (`app.py`).
- El frontend es una UI estática (`index.html`, `styles.css`, `client.js`).
- El sistema combina dos tipos de análisis:
  1. Similitud semántica
  2. Similitud léxica
- La calificación final es una combinación ponderada de ambos resultados.

## 1. Analizador semántico

El analizador semántico se encuentra en `semantic_analyzer.py`.

### Modelo usado

- Preferentemente utiliza `sentence-transformers` con el modelo pre-entrenado:
  - `distiluse-base-multilingual-cased-v2`

### Comportamiento

- Si `sentence-transformers` está instalado, el sistema genera embeddings de ambas respuestas y calcula la similitud coseno.
- Si no está disponible, cae en un modo de respaldo basado en:
  - tokenización simple
  - similitud de Jaccard entre conjuntos de tokens
  - cobertura de tokens
  - similitud de texto con `difflib.SequenceMatcher`
  - coincidencia aproximada de tokens

### Salida

El analizador devuelve un diccionario con:
- `similarity`: puntuación entre 0.0 y 1.0
- `confidence`: estimación de confianza interna
- `reference_tokens` y `student_tokens`
- `token_overlap`
- `model`: `sentence-transformers` o `fallback`

## 2. Analizador léxico

El analizador léxico se encuentra en `lexical_analyzer.py`.

### Enfoque

- Tokeniza texto en palabras
- Normaliza cada token con un stemmer de NLTK (`SnowballStemmer` para español) si está disponible
- Filtra palabras muy cortas
- Calcula similitud léxica usando:
  - Jaccard entre conjuntos de tokens
  - cobertura relativa de tokens
  - coincidencia difusa entre tokens

### Resultados adicionales

El módulo también extrae:
- `matched_terms` — términos comunes entre referencia y estudiante
- `missing_terms` — términos de la referencia que faltan
- `extra_terms` — términos adicionales del estudiante
- `keyword_match` — porcentaje de coincidencia entre palabras clave
- `lexical_diversity`
- `vocabulary_coverage`

## 3. Combinación de puntajes

La puntuación general se calcula en `app.py` usando los pesos definidos en `config.py`:

- `SEMANTIC_WEIGHT = 0.6`
- `LEXICAL_WEIGHT = 0.4`

Esta combinación estática genera una `overall_score` en base a:

```python
overall_score = (semantic_score * SEMANTIC_WEIGHT) + (lexical_score * LEXICAL_WEIGHT)
```

## 4. Conjunto de datos

### Estado actual

Este repositorio NO incluye un conjunto de datos de entrenamiento o evaluación.

- No existe un archivo `data/` ni un conjunto de datos etiquetado dentro del proyecto.
- La aplicación funciona con pares de texto ingresados por el usuario.

### Recomendación de datos

Para validar o mejorar esta solución, se recomienda usar un conjunto de datos con ejemplos de:
- preguntas / contexto
- respuesta de referencia correcta
- respuesta de estudiante
- etiqueta de calidad o calificación esperada

Un formato recomendable sería:

```json
{
  "question": "¿Qué causó la Revolución Francesa?",
  "reference_answer": "...",
  "student_answer": "...",
  "grade": "B",
  "label": "correcta"
}
```

## 5. Algoritmo de aprendizaje implementado

### Observación importante

SSEAR no implementa un algoritmo de aprendizaje supervisado en este repositorio.

- No se entrena un clasificador con un dataset propio.
- El sistema se basa en modelos pre-entrenados y reglas heurísticas.
- El objetivo es evaluar similitud entre texto de referencia y texto del estudiante, no construir un clasificador desde cero.

### Componentes principales

1. **Embeddings semánticos** (si están disponibles)
   - Modelo pre-entrenado de sentence-transformers.
   - Compara significado general de frases.
2. **Similitud léxica**
   - Stemming y análisis de tokens.
   - Jaccard y similitud difusa.
3. **Generación de feedback**
   - Basada en umbrales de similitud.
   - Produce fortalezas, debilidades y sugerencias.

## 6. Métricas y desempeño

### Métricas incluidas en el repositorio

- El código no calcula métricas de rendimiento como exactitud, precisión, recall o F1.
- No hay evaluación de clases, porque la salida actual es una puntuación continua de similitud.

### Qué métricas serían válidas si se usa un dataset etiquetado

Si se construye un sistema de evaluación por categorías (por ejemplo: A/B/C/D/F), entonces se pueden calcular:
- Exactitud (accuracy)
- Precisión por clase
- Recall por clase
- F1-score por clase
- Reporte de clasificación usando `sklearn.metrics.classification_report`

Para datos continuos de similitud, también se podrían medir:
- Correlación con la calificación humana
- Error cuadrático medio (RMSE)
- MAE

### Estado actual del desempeño

- No hay resultados publicados de exactitud, F1, precisión o recall en este repositorio.
- El desempeño depende de:
  - calidad del modelo `sentence-transformers` instalado
  - calidad del texto de referencia
  - dominio y vocabulario del problema educativo

## 7. Cómo ampliar la evaluación cuantitativa

Para medir desempeño real, sigue estos pasos:

1. Recolecta un dataset etiquetado con respuestas de referencia y respuestas de estudiantes.
2. Define un umbral o etiquetas de calificación.
3. Ejecuta el sistema sobre el dataset.
4. Calcula:
   - `accuracy_score`
   - `precision_recall_fscore_support`
   - `classification_report`

Ejemplo con `scikit-learn`:

```python
from sklearn.metrics import classification_report

# y_true: etiquetas esperadas
# y_pred: etiquetas generadas a partir del score
print(classification_report(y_true, y_pred, digits=4))
```

## 8. Conclusión

SSEAR es una herramienta de evaluación de respuestas basada en:
- embeddings semánticos pre-entrenados
- reglas y heurísticas léxicas
- combinación de puntajes para generar una calificación general

Este proyecto actúa como una plataforma local de demostración. Para transformarlo en un sistema con métricas formales, se debe integrar un dataset anotado y un proceso de evaluación supervisada.
