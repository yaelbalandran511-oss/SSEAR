# SSEAR — Documentación Técnica

Este archivo describe cómo funciona el proyecto, su arquitectura y los componentes principales.

## Objetivo del proyecto
SSEAR es un sistema de evaluación de respuestas abiertas diseñado para comparar la respuesta del estudiante contra una referencia usando:
- evaluación por ideas clave (semántica explícita)
- similitud léxica con fórmula exacta
- detección de errores graves

El enfoque principal es evitar la evaluación basada en similitud difusa o embeddings cuando se quiere juzgar ideas concretas.

## Arquitectura general

### Backend
- `app.py`: servidor Flask que expone la UI y la API de evaluación.
- `semantic_analyzer.py`: módulo de análisis semántico y extracción de ideas conceptuales.
- `lexical_analyzer.py`: módulo de similitud léxica y cálculo de coincidencia de vocabulario.
- `feedback_generator.py`: genera retroalimentación detallada para el estudiante.

### Interfaz web
- `index.html`: página principal de la aplicación.
- `styles.css`: estilos visuales.
- `client.js`: lógica de cliente para enviar solicitudes a la API.

### Evaluador independiente
- `evaluador_respuestas_universal.py`: script autónomo que implementa una evaluación por ideas clave sin depender de librerías externas.

### Configuración de modelos
- `setup_models.py`: descarga modelos y recursos necesarios para el backend.

## Lógica de evaluación

### Evaluación por ideas clave
1. El evaluador recibe una lista de ideas, cada una con un nombre, peso y palabras clave.
2. Para cada idea, comprueba si alguna de sus palabras clave aparece en la respuesta del estudiante.
3. Si la idea está presente, suma su peso al puntaje semántico.
4. Si falta, se registra como idea faltante.

Este enfoque garantiza que la evaluación se base en conceptos explícitos, no en distancia semántica implícita.

### Penalización por errores graves
- Se define una lista de frases falsas o incorrectas.
- Si la respuesta contiene alguna de esas frases, se resta una penalización del puntaje semántico.
- El puntaje semántico final nunca cae por debajo de 0.

### Similitud léxica correcta
Se utiliza la fórmula exacta:

```
(2 × palabras_comunes) / (total_ref + total_est) × 100
```

Esto mide la superposición de vocabulario normalizado entre la referencia y la respuesta, sin embeddings.

### Calificación final
La nota se calcula como:

```
calificación = 0.80 × semántica_final + 0.20 × léxica
nota = calificación / 10
```

De esta forma, la evaluación prioriza las ideas clave, pero también valora la coherencia léxica.

## Ejemplo precargado
El ejemplo incluido en `evaluador_respuestas_universal.py` usa la pregunta:

- "¿Por qué la Tierra es un planeta habitable?"

Ideas clave:
- Agua líquida
- Atmósfera/oxígeno
- Temperatura adecuada
- Distancia al Sol

Respuestas del ejemplo:
- Caso A: respuesta correcta con varias ideas presentes.
- Caso B: respuesta incorrecta con afirmaciones erróneas.
- Caso C: copia exacta de la referencia.

## Cómo ejecutar

### Ejecución rápida
```powershell
python evaluador_respuestas_universal.py
```

### Ejecutar servidor Flask
```powershell
python app.py
```

## Archivos clave
- `README.md`: guía de descarga y uso rápido.
- `README_TECHNICAL.md`: cómo funciona el sistema.
- `requirements.txt`: dependencias Python.
- `evaluador_respuestas_universal.py`: evaluador offline por ideas clave.

## Recomendaciones
- Usa `evaluador_respuestas_universal.py` para pruebas offline y para mostrar el criterio de evaluación por ideas.
- Usa `app.py` y la UI para demostraciones con interfaz web.
- Mantén `requirements.txt` actualizado si agregas nuevas dependencias.
