# SSEAR — Descargar y usar el proyecto

Este documento explica cómo descargar el proyecto completo y ejecutarlo localmente en Windows.

## 1. Descargar el proyecto

1. Clona el repositorio desde GitHub o copia la carpeta completa del proyecto.
2. Abre una terminal en la carpeta raíz del proyecto.

```powershell
cd "c:\Users\Yaelb\Documents\Proyecto Final TPA Balandrán"
```

## 2. Preparar el entorno Python

1. Crea un entorno virtual:

```powershell
python -m venv venv
```

2. Activa el entorno virtual en PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

3. Actualiza pip y instala dependencias:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

> Nota: el paquete `sentence-transformers` no está listado como obligatorio en `requirements.txt`, por lo que la funcionalidad semántica completa solo estará disponible si lo instalas manualmente. Si no lo instalas, el proyecto usa un modo de respaldo basado en similitud de texto.

## 3. Ejecutar el proyecto

### Opción recomendada: usar `run.bat`

Desde la carpeta del proyecto en PowerShell:

```powershell
.\run.bat
```

`run.bat` intenta ejecutar `app.py` usando `venv\Scripts\python.exe`.

### Opción alternativa: ejecutar directamente con Python

```powershell
& "c:\Users\Yaelb\Documents\Proyecto Final TPA Balandrán\venv\Scripts\python.exe" app.py
```

O si ya tienes el entorno activado:

```powershell
python app.py
```

## 4. Abrir la aplicación

Abre un navegador y visita:

```text
http://127.0.0.1:5000
```

## 5. Uso básico

1. Escribe una pregunta de contexto en el campo "Pregunta".
2. Introduce la respuesta de referencia en el campo "Respuesta de Referencia".
3. Introduce la respuesta del estudiante en el campo "Respuesta del Estudiante".
4. Haz clic en "Evaluar Respuesta".

El sistema mostrará:
- Similitud semántica
- Similitud léxica
- Calificación general
- Retroalimentación personalizada
- Términos encontrados y faltantes

## 6. API disponibles

El backend expone los siguientes endpoints:

- `GET /api/health` — Comprueba que el servidor esté vivo.
- `POST /api/evaluate` — Evalúa una sola respuesta.
- `POST /api/batch-evaluate` — Evalúa varias respuestas en lote.
- `GET /api/models-info` — Devuelve información de los modelos cargados.

### Ejemplo de uso de `/api/evaluate`

```json
{
  "reference_answer": "Texto de referencia...",
  "student_answer": "Texto del estudiante...",
  "question": "Pregunta de contexto...",
  "context": "Información adicional opcional..."
}
```

## 7. Archivos principales

- `app.py` — Servidor Flask y rutas principales.
- `semantic_analyzer.py` — Módulo de similitud semántica.
- `lexical_analyzer.py` — Módulo de similitud léxica.
- `feedback_generator.py` — Generador de retroalimentación.
- `index.html`, `styles.css`, `client.js` — Interfaz web.
- `requirements.txt` — Dependencias de Python.
- `run.bat` — Atajo Windows para ejecutar el servidor.

## 8. Solución de problemas comunes

- Si `python app.py` falla, asegúrate de usar el Python del entorno virtual.
- Si `sentence-transformers` no está instalado, el sistema seguirá funcionando, pero con semántica simplificada.
- Si el navegador no carga, verifica que el servidor esté en `http://127.0.0.1:5000` y que no haya otro servicio en ese puerto.

## 9. Nota sobre datos y versiones

El proyecto está diseñado como una herramienta de evaluación local y no incluye un conjunto de datos de entrenamiento dentro del repositorio. Para usarlo en un contexto real, importa tus propios pares de respuestas de referencia y respuestas estudiantiles.
