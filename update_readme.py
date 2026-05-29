from pathlib import Path

content = '''# SSEAR — Sistema Semántico de Evaluación Automatizada de Respuestas

Sistema de evaluación automática de respuestas abiertas con retroalimentación personalizada, análisis semántico y análisis léxico.

## Requisitos

- Windows 10 o superior
- Python 3.11 recomendado
- Git instalado en el equipo donde se va a clonar el proyecto
- Conexión a internet sólo para la primera descarga del modelo

> Nota: Se recomienda usar Python 3.11 porque algunas librerías como `sentence-transformers` pueden presentar incompatibilidades con versiones más recientes de Python.

## Descarga e instalación

### 1. Instalar Python 3.11

Si tu computadora no tiene Python 3.11 instalado, primero debes instalarlo antes de ejecutar el proyecto.

#### Pasos

1. Entra a la página oficial de Python: https://www.python.org/downloads/windows/
2. Descarga la versión Python 3.11.x para Windows.
3. Ejecuta el instalador descargado.
4. Marca la opción `Add Python to PATH`.
5. Haz clic en `Install Now`.
6. Espera a que termine la instalación.

#### Verificar la instalación

Abre PowerShell o CMD y ejecuta:

```powershell
python --version
```

o:

```powershell
py --version
```

Si todo salió bien, deberías ver algo como:

```text
Python 3.11.x
```

### 2. Clonar el repositorio

Clona el proyecto desde la rama main:

```powershell
git clone -b main https://github.com/yaelbalandran511-oss/SSEAR.git
cd SSEAR
```

### 3. Alternativa: descargar el proyecto en ZIP

Si no puedes clonar el repositorio con Git, entra al repositorio desde tu navegador y descárgalo como ZIP:

https://github.com/yaelbalandran511-oss/SSEAR/tree/main

Después:

- Haz clic en Code
- Selecciona Download ZIP
- Descomprime el archivo
- Entra a la carpeta del proyecto
- Abre una terminal ahí y continúa con la instalación

### 4. Crear el entorno virtual

```powershell
py -3.11 -m venv venv
```

Si `py -3.11` no funciona, puedes usar:

```powershell
python -m venv venv
```

### 5. Activar el entorno virtual

En PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

En CMD:

```cmd
venv\Scripts\activate.bat
```

### 6. Instalar dependencias

Si existe `requirements.txt`, instala todo con:

```powershell
pip install -r requirements.txt
```

Si prefieres instalar manualmente o falta alguna dependencia, usa:

```powershell
pip install flask flask-cors numpy scikit-learn nltk sentence-transformers openpyxl torch torchvision torchaudio
```

### 7. Descargar recursos de NLTK

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 8. Ejecutar la aplicación

```powershell
python app.py
```

### 9. Abrir la aplicación

Abre tu navegador y entra a:

```text
http://localhost:5000
```

## Guardado automático de resultados en Excel

Cada vez que se evalúa una respuesta, el sistema guarda automáticamente un registro en:

```text
logs/evaluation_results.xlsx
```

Información que se guarda por cada evaluación:

- Fecha y hora
- Pregunta
- Respuesta de referencia
- Respuesta del estudiante
- Similitud semántica
- Similitud léxica
- Calificación general
- Términos encontrados
- Términos faltantes
- Términos extra
- Retroalimentación generada

## Comportamiento

- Si el archivo no existe, se crea automáticamente.
- Si ya existe, se agrega una nueva fila al final.
- El archivo queda guardado dentro de la carpeta `logs/`.

## Primera ejecución

La primera vez que ejecutes el sistema, se descargará automáticamente el modelo de lenguaje:

```text
distiluse-base-multilingual-cased-v2
```

Esto puede tardar entre 5 y 10 minutos, dependiendo de tu conexión a internet.

## Posibles errores y soluciones

### Error: `python` no se reconoce como comando
Significa que Python no está instalado o no se agregó al PATH.

**Solución:**

- Reinstala Python 3.11
- Marca la opción `Add Python to PATH`

### Error: `ModuleNotFoundError: No module named 'flask'`
Falta instalar Flask.

**Solución:**

```powershell
pip install flask
```

### Error: `ModuleNotFoundError: No module named 'flask_cors'`
Falta instalar Flask-Cors.

**Solución:**

```powershell
pip install flask-cors
```

### Error: No module named `openpyxl`
Falta la librería para guardar archivos Excel.

**Solución:**

```powershell
pip install openpyxl
```

### Error: `ModuleNotFoundError: No module named 'torch'`
Falta instalar PyTorch.

**Solución:**

```powershell
pip install torch torchvision torchaudio
```

### Error: can't open file 'main.py'
Ese archivo no existe en el proyecto.

**Solución:**

Ejecuta el archivo correcto:

```powershell
python app.py
```

### Error: can't open file 'app.py'
Estás en una carpeta incorrecta.

**Solución:**

Verifica que estés dentro de la carpeta del proyecto con:

```powershell
dir
```

y asegúrate de que `app.py` esté ahí.

### Error al activar el entorno virtual
Si PowerShell bloquea la activación, usa:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

y luego:

```powershell
.\venv\Scripts\Activate.ps1
```

### Error: la carpeta `logs/` está vacía
Es normal si todavía no has hecho ninguna evaluación.

**Solución:**

Ejecuta la aplicación y evalúa una respuesta para que se cree el archivo Excel.

### Error: el Excel no se crea
Puede pasar si la funcionalidad de guardado no se ejecutó correctamente o si falta `openpyxl`.

**Solución:**

- Verifica que la evaluación se complete
- Revisa que `openpyxl` esté instalado
- Confirma que el sistema tenga permisos para escribir en `logs/`

### Error: PyTorch tarda mucho en instalarse
Es normal, porque PyTorch es pesado.

**Solución:**

- Espera unos minutos
- No cierres la terminal
- Si se instaló bien, continúa con la app

## Casos de prueba para evaluar respuestas

A continuación se muestran ejemplos de preguntas con su respuesta de referencia y una respuesta del alumno. Estos casos sirven para probar el sistema con respuestas muy parecidas y también con respuestas no relacionadas.

### Caso 1: Respuesta muy parecida

**Pregunta:**
Explica qué es la fotosíntesis y menciona dos elementos esenciales.

**Respuesta de referencia:**
La fotosíntesis es el proceso mediante el cual las plantas convierten la energía lumínica en energía química, produciendo glucosa y oxígeno a partir de dióxido de carbono y agua. Dos elementos esenciales para que ocurra son la luz solar y el agua.

**Respuesta del alumno:**
La fotosíntesis es el proceso mediante el cual las plantas convierten la energía de la luz en energía química, produciendo glucosa y oxígeno a partir de dióxido de carbono y agua. Dos elementos esenciales son la luz solar y el agua.

### Caso 2: Respuesta muy parecida

**Pregunta:**
¿Qué es la migración en animales?

**Respuesta de referencia:**
La migración es el desplazamiento estacional que realizan algunos animales para buscar alimento, reproducirse o sobrevivir a cambios climáticos.

**Respuesta del alumno:**
La migración es el desplazamiento estacional que hacen algunos animales para buscar alimento, reproducirse o adaptarse a cambios climáticos.

### Caso 3: Respuesta muy parecida

**Pregunta:**
¿Qué es la energía renovable?

**Respuesta de referencia:**
La energía renovable proviene de fuentes naturales que se regeneran de manera continua, como el sol, el viento o el agua.

**Respuesta del alumno:**
La energía renovable proviene de fuentes naturales que se regeneran continuamente, como el sol, el viento y el agua.

### Caso 4: Respuesta nada parecida

**Pregunta:**
¿Qué es la mitosis?

**Respuesta de referencia:**
La mitosis es el proceso de división celular mediante el cual una célula origina dos células hijas genéticamente idénticas.

**Respuesta del alumno:**
La mitosis es una herramienta que se usa para construir muebles y cortar madera con precisión.

### Caso 5: Respuesta nada parecida

**Pregunta:**
¿Qué es el sistema digestivo?

**Respuesta de referencia:**
El sistema digestivo es el conjunto de órganos que transforman los alimentos en nutrientes que el cuerpo puede absorber y utilizar.

**Respuesta del alumno:**
Es una red de cables y circuitos que permite que las computadoras funcionen y se conecten a internet.
'''

Path('README.md').write_text(content, encoding='utf-8')
print('README updated')
