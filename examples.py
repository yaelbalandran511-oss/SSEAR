"""
Ejemplos de prueba - Casos de uso para SSEAR
Ejecuta este archivo para probar la API sin la interfaz web
"""

import requests
import json
import time

API_URL = 'http://localhost:5000/api'

# Casos de prueba
TEST_CASES = [
    {
        'name': 'Biología - Fotosíntesis',
        'question': '¿Qué es la fotosíntesis?',
        'reference': 'La fotosíntesis es el proceso bioquímico mediante el cual las plantas convierten la luz solar en energía química, utilizando dióxido de carbono y agua para producir glucosa y oxígeno. Este proceso ocurre principalmente en las hojas y es esencial para la vida en la Tierra.',
        'student': 'Las plantas usan la luz del sol para hacer energía. Toman dióxido de carbono del aire y agua del suelo, y producen alimento.'
    },
    {
        'name': 'Física - Ley de Newton',
        'question': 'Explica la Primera Ley de Newton',
        'reference': 'La Primera Ley de Newton establece que un objeto en reposo permanecerá en reposo, y un objeto en movimiento continuará moviéndose a velocidad constante en línea recta, a menos que sea actuado por una fuerza externa. Esta ley describe la inercia.',
        'student': 'Un objeto que se mueve sigue moviéndose. Si está parado sigue parado. Necesitas una fuerza para cambiar esto.'
    },
    {
        'name': 'Historia - Revolución Francesa',
        'question': 'Describe las causas de la Revolución Francesa',
        'reference': 'Las causas principales fueron: 1) Crisis económica y endeudamiento de la corona, 2) Hambre y pobreza del pueblo, 3) Desigualdad de las clases sociales (Estado Llano oprimido), 4) Ideas ilustradas sobre libertad y democracia, 5) Mal gobierno de Luis XVI, 6) Poder excesivo de la nobleza y clero.',
        'student': 'La gente estaba pobre y el rey gastaba mucho dinero. Querían cambios y libertad.'
    },
    {
        'name': 'Química - Reacciones Exotérmicas',
        'question': '¿Qué es una reacción exotérmica?',
        'reference': 'Una reacción exotérmica es aquella que libera energía en forma de calor hacia el ambiente. En estas reacciones, la energía de los productos es menor que la de los reactivos. Ejemplos incluyen la combustión, la neutralización de ácidos y bases, y muchas oxidaciones.',
        'student': 'Es una reacción donde se libera calor. Por ejemplo, cuando quemas algo.'
    },
    {
        'name': 'Perfecta - Respuesta Ideal',
        'question': 'Define el ciclo del agua',
        'reference': 'El ciclo del agua es el proceso continuo de circulación del agua en la Tierra, que incluye: evaporación (agua se convierte en vapor desde océanos y lagos), condensación (vapor se convierte en gotitas de agua), precipitación (gotitas caen como lluvia o nieve), y escorrentía (agua regresa a océanos). Este ciclo es esencial para mantener el equilibrio ambiental.',
        'student': 'El ciclo del agua es un proceso continuo de circulación que incluye evaporación, condensación, precipitación y escorrentía. El agua se evapora desde océanos y lagos, se convierte en vapor, luego se condensa en gotitas que caen como lluvia o nieve, y finalmente regresa a los océanos a través de la escorrentía. Este proceso es esencial para mantener el equilibrio ambiental y sustenta toda la vida en la Tierra.'
    },
    {
        'name': 'Pobre - Respuesta Incompleta',
        'question': 'Explica la fotosíntesis',
        'reference': 'La fotosíntesis es el proceso mediante el cual las plantas convierten la luz solar en energía química, utilizando dióxido de carbono y agua para producir glucosa y oxígeno. Ocurre en las hojas y es esencial para la vida en la Tierra.',
        'student': 'Las plantas hacen comida con la luz.'
    }
]


def print_header(text):
    """Imprime encabezado formateado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_result(result):
    """Imprime resultado formateado"""
    scores = result['scores']
    
    print(f"  Similitud Semántica: {scores['semantic']:.1f}%")
    print(f"  Similitud Léxica:    {scores['lexical']:.1f}%")
    print(f"  Calificación:        {scores['overall']:.1f}% - Grado: {scores['grade']}")
    
    if result.get('feedback'):
        feedback = result['feedback']
        summary = feedback.get('summary', {})
        print(f"  {summary.get('rating', '')}: {summary.get('message', '')}")


def test_single_evaluation(test_case):
    """Prueba evaluación individual"""
    print_header(f"Prueba: {test_case['name']}")
    
    print(f"Pregunta: {test_case['question']}\n")
    
    payload = {
        'reference_answer': test_case['reference'],
        'student_answer': test_case['student'],
        'question': test_case['question']
    }
    
    try:
        response = requests.post(f"{API_URL}/evaluate", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print_result(result)
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
            print(f"Error de conexión: {e}")
        return False


def test_batch_evaluation():
    """Prueba evaluación por lotes"""
    print_header("Prueba: Evaluación por Lotes")
    
    evaluations = [
        {
            'reference_answer': case['reference'],
            'student_answer': case['student'],
            'question': case['question']
        }
        for case in TEST_CASES[:3]  # Primeros 3 casos
    ]
    
    payload = {'evaluations': evaluations}
    
    try:
        response = requests.post(f"{API_URL}/batch-evaluate", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Evaluaciones procesadas: {result['count']}")
            print(f"Resultados obtenidos\n")
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
    
    except Exception as e:
            print(f"Error de conexión: {e}")
        return False


def test_health_check():
    """Verifica salud del servidor"""
    print_header("Verificando Servidor")
    
    try:
        response = requests.get(f"{API_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Estado: {data['status']}")
            print(f"Modelos cargados: {data['models_loaded']}")
            print(f"Timestamp: {data['timestamp']}\n")
            return True
        else:
            print(f"Servidor no responde correctamente")
            return False
    
    except Exception as e:
        print(f"No se puede conectar al servidor")
        print(f"   Asegúrate de que está corriendo: python app.py")
        print(f"   Error: {e}\n")
        return False


def test_models_info():
    """Obtiene información de modelos"""
    print_header("Información de Modelos")
    
    try:
        response = requests.get(f"{API_URL}/models-info")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Modelo Semántico: {data['semantic_model']}")
            print(f"Modelo Léxico: {data['lexical_model']}")
            print(f"Idioma: {data['language']}")
            print(f"Offline: {data['offline']}")
            print(f"Características:")
            for feature in data['features']:
                print(f"    - {feature}")
            print()
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  SSEAR - Suite de Pruebas".center(68) + "█")
    print("█" + "  Sistema Semántico de Evaluación Automatizada".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    # Verificar conexión
    if not test_health_check():
        print("\nNo se puede conectar al servidor.")
        print("   Asegúrate de ejecutar primero: python app.py")
        return
    
    # Información de modelos
    test_models_info()
    
    # Pruebas individuales
    passed = 0
    failed = 0
    
    for test_case in TEST_CASES:
        if test_single_evaluation(test_case):
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)  # Pequeña pausa entre pruebas
    
    # Prueba de lotes
    if test_batch_evaluation():
        passed += 1
    else:
        failed += 1
    
    # Resumen
    print_header("Resumen de Pruebas")
    total = passed + failed
    print(f"Pruebas exitosas: {passed}/{total}")
    print(f"Pruebas fallidas: {failed}/{total}")
    print(f"Tasa de éxito: {(passed/total)*100:.1f}%\n")
    
    if failed == 0:
        print("¡TODAS LAS PRUEBAS PASARON!\n")
    else:
        print(f"{failed} prueba(s) fallaron. Revisa los logs.\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\nError inesperado: {e}")
