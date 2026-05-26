# SSEAR — Sistema Semántico de Evaluación Automatizada de Respuestas

Proyecto que incluye un backend Flask que sirve la UI estática y las rutas de evaluación (`/api/*`).

Objetivo: que cualquier persona pueda clonar y ejecutar el proyecto localmente de forma reproducible.

## Requisitos
- Python 3.10+ (recomendado 3.11)
- Git

## Pasos (local, Windows PowerShell)

1. Clonar el repo:
```powershell
git clone <TU_REPO_URL>
cd "Proyecto Final TPA Balandrán"
```

2. Crear y activar un entorno virtual:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instalar dependencias:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Descargar modelos y recursos NLP (script automático):
```powershell
python setup_models.py
```

5. Ejecutar el servidor:
```powershell
python app.py
```
Abre el navegador en `http://127.0.0.1:5000`.

## Docker (opcional — reproduce sin preocuparte por Python/venv)

1. Construir y ejecutar con Docker Compose:
```bash
docker compose up --build
```
2. Abrir `http://127.0.0.1:5000`.

## Notas

## Solución de problemas

Si quieres, puedo añadir CI/CD básico o un instalador más sencillo. Dime qué prefieres.

1. Inicializa el repositorio (si aún no lo has hecho):
```bash
git init
git add .
git commit -m "Initial commit: SSEAR project prepared for sharing"
```

2. Crea un nuevo repositorio en GitHub (a través de la web) y añádelo como remoto:
```bash
git remote add origin https://github.com/<tu-usuario>/<repo>.git
git branch -M main
git push -u origin main
```

Alternativamente, usa GitHub CLI (`gh repo create`) para crear y subir en un solo comando.

Asegúrate de no comprometer archivos de modelo grandes o tu directorio `venv`; `.gitignore` ya excluye elementos comunes.


## Qu� es SSEAR

SSEAR es un sistema offline que eval�a respuestas abiertas comparando:
- la **similitud sem�ntica** entre respuesta de referencia y respuesta del estudiante
- la **similitud l�xica** mediante an�lisis de vocabulario y palabras clave

El objetivo es ofrecer una evaluaci�n educativa m�s justa y una retroalimentaci�n �til.

## Qu� incluye este proyecto

- `app.py` - servidor Flask con endpoints REST
- `semantic_analyzer.py` - an�lisis sem�ntico con transformers
- `lexical_analyzer.py` - an�lisis l�xico con NLTK y tokenizaci�n
- `feedback_generator.py` - genera retroalimentaci�n automatizada
- `index.html`, `styles.css`, `client.js` - interfaz web
- `requirements.txt` - dependencias de Python

## Requisitos

- Python 3.8 o superior
- `pip`
- Espacio libre: al menos 1 GB para descargar modelos

## Instalaci�n y ejecuci�n

1. Abre una terminal en la carpeta del proyecto.
2. Crea y activa un entorno virtual (recomendado):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

3. Instala las dependencias:

```powershell
pip install -r requirements.txt
```

4. Ejecuta el servidor:

```powershell
python app.py
```

5. Abre el navegador en:

```text
http://localhost:5000
```

## Uso

1. Completa el campo **Pregunta**.
2. Pega la **Respuesta de Referencia**.
3. Pega la **Respuesta del Estudiante**.
4. Haz clic en **Evaluar Respuesta**.

El sistema mostrar�:
- puntuaciones sem�ntica y l�xica
- calificaci�n general
- retroalimentaci�n detallada
- t�rminos encontrados y faltantes

## API

### POST `/api/evaluate`

Request JSON:

```json
{
  "reference_answer": "...",
  "student_answer": "...",
  "question": "...",
  "context": "..."
}
```

Response JSON incluye:
- `scores` con `semantic`, `lexical`, `overall` y `grade`
- `feedback` con sugerencias y fortalezas
- `metadata` con t�rminos coincidentes y faltantes

### POST `/api/batch-evaluate`

Request JSON:

```json
{
  "evaluations": [
    {
      "reference_answer": "...",
      "student_answer": "...",
      "question": "..."
    }
  ]
}
```

### GET `/api/health`

Devuelve estado del servidor.

### GET `/api/models-info`

Devuelve informaci�n de los modelos.

## Buenas pr�cticas

- Mant�n la referencia clara y completa.
- Evita respuestas demasiado cortas.
- Usa `question` para dar contexto.

## Archivos simples y �tiles

Este proyecto se mantiene con los archivos necesarios para ejecutar SSEAR y la documentaci�n principal en `README.md`.
