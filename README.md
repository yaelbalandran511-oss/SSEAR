# SSEAR — Sistema de Evaluación de Respuestas por Ideas Clave

Este proyecto ofrece un sistema que evalúa respuestas de estudiantes en base a ideas clave y similitud léxica.

## Qué incluye
- `app.py` — servidor Flask y API de evaluación
- `index.html`, `styles.css`, `client.js` — interfaz web estática
- `semantic_analyzer.py` — análisis semántico
- `lexical_analyzer.py` — análisis léxico
- `evaluador_respuestas_universal.py` — evaluador offline por ideas clave
- `setup_models.py` — descarga y preparación de modelos
- `requirements.txt` — dependencias de Python

## Requisitos
- Python 3.10 o superior
- Git
- Windows / Linux / macOS

## Instalación rápida
1. Clona el repositorio:
```powershell
git clone <TU_REPO_URL>
cd "Proyecto Final TPA Balandrán"
```
2. Crea y activa un entorno virtual:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
3. Instala las dependencias:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecución
### Ejecutar el servidor web
```powershell
python app.py
```
Luego abre `http://127.0.0.1:5000`.

### Ejecutar el evaluador universal por ideas clave
```powershell
python evaluador_respuestas_universal.py
```
Este script ofrece ejemplo precargado, modo interactivo y modo múltiple.

## Uso básico
- Opción 1: ejemplo precargado con la pregunta de "Tierra habitable"
- Opción 2: ingresar pregunta, referencia, ideas clave y respuesta manualmente
- Opción 3: evaluar varias respuestas de estudiantes para la misma pregunta

## Resultado esperado
Cada evaluación muestra:
- Semántica (ideas clave) en %
- Léxica en % con fórmula correcta
- Calificación final en %
- Nota sobre 10
- Ideas encontradas ✅
- Ideas faltantes ❌
- Errores detectados ⚠️
- Coincidencia de palabras

## Notas
- El evaluador universal es autocontenido y no requiere librerías externas adicionales.
- El sistema Flask requiere instalación de dependencias desde `requirements.txt`.
- Para una copia rápida, usa `git clone` y ejecuta `python evaluador_respuestas_universal.py`.
