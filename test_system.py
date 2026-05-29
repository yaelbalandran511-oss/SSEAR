#!/usr/bin/env python3
"""
Script de Prueba - SSEAR
Verifica que el sistema de evaluación funciona correctamente
"""

import sys
sys.path.insert(0, '.')

from evaluation_engine import EvaluationEngine
from feedback_generator import FeedbackGenerator

# Datos de prueba
test_question = "¿Qué es la fotosíntesis?"

test_reference = """
La fotosíntesis es el proceso biológico mediante el cual las plantas, algas y algunas bacterias 
convierten la luz solar en energía química. Este proceso utiliza dióxido de carbono y agua para 
producir glucosa y oxígeno como subproductos.
"""

test_student_good = """
La fotosíntesis es el proceso donde las plantas convierten la luz del sol en energía química 
utilizando dióxido de carbono y agua para producir glucosa y oxígeno.
"""

test_student_poor = "Las plantas hacen fotosíntesis."

test_student_excellent = """
La fotosíntesis es el proceso biológico mediante el cual las plantas convierten la luz solar 
en energía química. Ocurre principalmente en las hojas a través de la clorofila. El proceso 
utiliza dióxido de carbono y agua para producir glucosa (azúcar) como fuente de energía y 
libera oxígeno como subproducto, que es esencial para la vida en la Tierra.
"""

def print_results(title, result, feedback):
    """Imprime resultados de forma legible"""
    print(f"\n{'='*70}")
    print(f"{'PRUEBA:':<15} {title}")
    print(f"{'='*70}")
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    scores = result.get('scores', {})
    print(f"\n📊 PUNTUACIONES:")
    print(f"  Semántico:  {scores.get('semantic', 0):.2f} (75%)")
    print(f"  Léxico:     {scores.get('lexical', 0):.2f} (25%)")
    print(f"  Final:      {scores.get('final', 0):.4f}")
    print(f"  Porcentaje: {scores.get('percentage', 0):.1f}%")
    print(f"  Calificación: {scores.get('grade', 'F')} ({feedback['summary']['rating']})")
    
    print(f"\n💡 RETROALIMENTACIÓN:")
    print(f"  Mensaje: {feedback['summary']['message']}")
    
    print(f"\n✓ FORTALEZAS ({len(feedback.get('strengths', []))}):")
    for strength in feedback.get('strengths', [])[:3]:
        print(f"  • {strength}")
    
    print(f"\n⚠ DEBILIDADES ({len(feedback.get('weaknesses', []))}):")
    for weakness in feedback.get('weaknesses', [])[:3]:
        print(f"  • {weakness}")
    
    print(f"\n💬 SUGERENCIAS ({len(feedback.get('suggestions', []))}):")
    for i, suggestion in enumerate(feedback.get('suggestions', [])[:2], 1):
        print(f"  {i}. {suggestion.get('area', 'N/A')}")
        print(f"     → {suggestion.get('suggestion', 'N/A')}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     PRUEBA DEL SISTEMA SSEAR v1.0.0                         ║
║  Sistema Semántico de Evaluación Automatizada de Respuestas ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Inicializar
        print("🚀 Inicializando sistema...")
        engine = EvaluationEngine()
        feedback_gen = FeedbackGenerator()
        print("   ✓ Motor de evaluación cargado")
        print("   ✓ Generador de retroalimentación cargado")
        
        # Prueba 1: Respuesta Pobre
        print("\n⏳ Ejecutando prueba 1: Respuesta Pobre...")
        result_poor = engine.evaluate(
            question=test_question,
            reference_answer=test_reference,
            student_answer=test_student_poor
        )
        feedback_poor = feedback_gen.generate(result_poor)
        print_results("Respuesta Corta/Pobre", result_poor, feedback_poor)
        
        # Prueba 2: Respuesta Buena
        print("\n⏳ Ejecutando prueba 2: Respuesta Buena...")
        result_good = engine.evaluate(
            question=test_question,
            reference_answer=test_reference,
            student_answer=test_student_good
        )
        feedback_good = feedback_gen.generate(result_good)
        print_results("Respuesta Buena", result_good, feedback_good)
        
        # Prueba 3: Respuesta Excelente
        print("\n⏳ Ejecutando prueba 3: Respuesta Excelente...")
        result_excellent = engine.evaluate(
            question=test_question,
            reference_answer=test_reference,
            student_answer=test_student_excellent
        )
        feedback_excellent = feedback_gen.generate(result_excellent)
        print_results("Respuesta Excelente", result_excellent, feedback_excellent)
        
        # Resumen
        print(f"\n{'='*70}")
        print("📈 RESUMEN DE PRUEBAS")
        print(f"{'='*70}")
        print(f"\nCalificaciones:")
        print(f"  Pobre:     {result_poor['scores']['grade']} ({result_poor['scores']['percentage']:.1f}%)")
        print(f"  Buena:     {result_good['scores']['grade']} ({result_good['scores']['percentage']:.1f}%)")
        print(f"  Excelente: {result_excellent['scores']['grade']} ({result_excellent['scores']['percentage']:.1f}%)")
        
        print(f"\n✓ Estadísticas del Caché:")
        cache_stats = engine.get_cache_stats()
        print(f"  Habilitado: {cache_stats.get('enabled', False)}")
        print(f"  Tamaño: {cache_stats.get('size', 0)} / {cache_stats.get('max_size', 0)}")
        
        print(f"\n{'='*70}")
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print(f"{'='*70}\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
