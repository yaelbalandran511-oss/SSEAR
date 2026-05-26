#!/bin/bash

# Script de instalación y ejecución para SSEAR en Linux/Mac
# Este script automatiza la instalación y descarga de modelos

echo ""
echo "===================================================="
echo "   SSEAR - Sistema Semántico de Evaluación"
echo "   Asistente de Instalación y Ejecución"
echo "===================================================="
echo ""

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Instálalo con:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3"
    exit 1
fi

echo "[OK] Python detectado"
python3 --version
echo ""

# Crear virtual environment
echo "[*] Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[OK] Entorno virtual creado"
else
    echo "[OK] Entorno virtual ya existe"
fi
echo ""

# Activar virtual environment
echo "[*] Activando entorno virtual..."
source venv/bin/activate
echo "[OK] Entorno virtual activado"
echo ""

# Upgrade pip
echo "[*] Actualizando pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
echo "[OK] pip actualizado"
echo ""

# Instalar dependencias
echo "[*] Instalando dependencias (esto puede tardar varios minutos)..."
echo "    - Flask y extensiones"
echo "    - Modelos de transformers"
echo "    - NLTK y herramientas NLP"
echo ""

pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Hubo un problema instalando las dependencias"
    exit 1
fi
echo "[OK] Dependencias instaladas"
echo ""

# Descargar modelos NLTK
echo "[*] Descargando modelos NLTK..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" > /dev/null 2>&1
echo "[OK] Modelos NLTK descargados"
echo ""

# Descargar modelo de transformers
echo "[*] Descargando modelo de transformers..."
echo "    Esto puede tardar 5-10 minutos en primera ejecución"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('distiluse-base-multilingual-cased-v2')" 2>&1 | grep -v "sentence_transformers"
echo "[OK] Modelo de transformers listo"
echo ""

# Crear carpeta para caché de modelos
mkdir -p models
echo "[OK] Carpeta de modelos creada"
echo ""

# Ejecutar servidor
echo "===================================================="
echo "   Iniciando servidor SSEAR..."
echo "===================================================="
echo ""
echo "Servidor ejecutándose en: http://localhost:5000"
echo ""
echo "Para detener el servidor: Presiona Ctrl+C"
echo ""
echo "[IMPORTANTE]"
echo "- Abre tu navegador en http://localhost:5000"
echo "- No cierres esta ventana mientras uses la aplicación"
echo "- Para cerrar: Presiona Ctrl+C"
echo ""

python app.py
