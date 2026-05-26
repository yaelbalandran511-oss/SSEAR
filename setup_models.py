"""
Script to install/download lightweight NLP models and NLTK data required by the project.
Run inside the project's virtualenv: `python setup_models.py`
"""
import subprocess
import sys

def run(cmd):
    print('>',' '.join(cmd))
    subprocess.check_call(cmd)

def install_packages():
    # Ensure spacy and nltk are present
    try:
        import spacy  # noqa: F401
    except Exception:
        run([sys.executable, '-m', 'pip', 'install', 'spacy'])

    try:
        import nltk  # noqa: F401
    except Exception:
        run([sys.executable, '-m', 'pip', 'install', 'nltk'])

def download_spacy_model():
    try:
        import spacy
        # Use small Spanish model
        model = 'es_core_news_sm'
        try:
            spacy.load(model)
            print(f"spaCy model '{model}' already installed")
        except Exception:
            run([sys.executable, '-m', 'spacy', 'download', model])
    except Exception as e:
        print('spaCy not available:', e)

def download_nltk_data():
    import nltk
    to_download = ['punkt', 'stopwords']
    for pkg in to_download:
        try:
            nltk.data.find(pkg)
            print(f"NLTK data '{pkg}' already present")
        except Exception:
            print('Downloading', pkg)
            nltk.download(pkg)

if __name__ == '__main__':
    print('Installing/checking packages...')
    install_packages()
    print('Downloading spaCy model...')
    download_spacy_model()
    print('Downloading NLTK data...')
    download_nltk_data()
    print('Done.')
