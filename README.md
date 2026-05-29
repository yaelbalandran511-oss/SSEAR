# SSEAR — Sistema Semántico de Evaluación Automatizada de Respuestas

Sistema de evaluación automática de respuestas abiertas con retroalimentación personalizada.

## 🚀 Inicio Rápido

### Requisitos
- **Python 3.11** (requerido — versiones superiores no son compatibles)
- Windows / Linux / Mac
- Descarga Python 3.11: https://www.python.org/downloads/release/python-3119/

### Instalación

```powershell
# 1. Verificar que tienes Python 3.11
py -3.11 --version

# 2. Crear entorno virtual con Python 3.11
py -3.11 -m venv venv311

# 3. Activar entorno (Windows PowerShell)
venv311\Scripts\activate

# Si PowerShell bloquea la activación, ejecuta primero:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# 4. Instalar dependencias
pip install flask flask-cors numpy scikit-learn nltk sentence-transformers

# 5. Descargar datos de NLTK (solo la primera vez)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# 6. Ejecutar servidor
python app.py