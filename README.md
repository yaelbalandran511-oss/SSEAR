# SSEAR — Instalación

## Requisitos

- Windows
- Python 3.11 recomendado
- Git instalado
- Conexión a internet solo para la primera descarga del modelo

> Nota: Se recomienda usar Python 3.11 porque algunas librerías como `sentence-transformers` pueden presentar incompatibilidades con versiones más recientes de Python.

## Instalación en Windows

### 1. Clonar el repositorio

En PowerShell o CMD:

```powershell
git clone -b main https://github.com/yaelbalandran511-oss/SSEAR.git
cd SSEAR
```

Alternativa: descargar el repositorio como ZIP desde GitHub, descomprimirlo y abrir la carpeta del proyecto en la terminal.

### 2. Crear el entorno virtual

En PowerShell o CMD:

```powershell
py -3.11 -m venv venv311
```

Si `py -3.11` no funciona:

```powershell
python -m venv venv311
```

### 3. Activar el entorno virtual

En PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv311\Scripts\Activate.ps1
```

En CMD:

```cmd
venv311\Scripts\activate.bat
```

### 4. Instalar dependencias

En PowerShell o CMD dentro del proyecto:

```powershell
pip install -r requirements.txt
```

Si `requirements.txt` no funciona o falta alguna dependencia:

```powershell
pip install flask flask-cors numpy scikit-learn nltk sentence-transformers
```

### 5. Descargar datos de NLTK

En PowerShell o CMD:

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 6. Ejecutar el servidor

En PowerShell o CMD:

```powershell
python app.py
```

### 7. Abrir la aplicación

Abre el navegador en:

```text
http://localhost:5000
```

## Primera ejecución

La primera vez que ejecutes el sistema se descargará automáticamente el modelo:

`distiluse-base-multilingual-cased-v2`

Esto puede tardar entre 5 y 10 minutos según tu conexión a internet.
