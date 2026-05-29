# SSEAR — Sistema Semántico de Evaluación Automatizada de Respuestas

Sistema de evaluación automática de respuestas abiertas con retroalimentación personalizada, análisis semántico y análisis léxico.

## 📋 Requisitos

- **Windows 10 o superior**
- **Python 3.11 recomendado**
- Git instalado en el equipo
- Conexión a internet solo para la primera descarga del modelo

> ⚠️ Nota: Se recomienda usar Python 3.11 porque algunas librerías como `sentence-transformers` pueden presentar incompatibilidades con versiones más recientes de Python.

## ⚡ Instalación y ejecución en Windows

### 1. Clonar el repositorio

```powershell
git clone https://github.com/yaelbalandran511-oss/SSEAR.git
cd SSEAR
```

### 2. Crear el entorno virtual

```powershell
py -3.11 -m venv venv311
```

Si `py -3.11` no funciona, puedes probar:

```powershell
python -m venv venv311
```

### 3. Activar el entorno virtual

#### En PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv311\Scripts\Activate.ps1
```

#### En CMD

```cmd
venv311\Scripts\activate.bat
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

Si `requirements.txt` no funciona o falta alguna librería, instala manualmente:

```powershell
pip install flask flask-cors numpy scikit-learn nltk sentence-transformers
```

### 5. Descargar datos de NLTK

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 6. Ejecutar el servidor

```powershell
python app.py
```

### 7. Abrir la aplicación

Abre tu navegador en:

```text
http://localhost:5000
```
