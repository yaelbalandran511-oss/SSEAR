import re
import json
from datetime import datetime


class EvaluadorRespuestas:
    def __init__(self):
        self.historial = []

    def normalizar(self, texto):
        texto = (texto or '').lower()
        texto = re.sub(r'[áàä]', 'a', texto)
        texto = re.sub(r'[éèë]', 'e', texto)
        texto = re.sub(r'[íìï]', 'i', texto)
        texto = re.sub(r'[óòö]', 'o', texto)
        texto = re.sub(r'[úùü]', 'u', texto)
        texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    def similitud_lexica_correcta(self, referencia, est):
        ref_norm = self.normalizar(referencia)
        est_norm = self.normalizar(est)
        palabras_ref = set(ref_norm.split())
        palabras_est = set(est_norm.split())
        comunes = palabras_ref & palabras_est
        if not palabras_ref or not palabras_est:
            return 0.0
        return (2 * len(comunes)) / (len(palabras_ref) + len(palabras_est)) * 100

    def coincidencia_palabras(self, referencia, est):
        ref_norm = self.normalizar(referencia)
        est_norm = self.normalizar(est)
        palabras_ref = set(ref_norm.split())
        palabras_est = set(est_norm.split())
        if not palabras_ref:
            return 0.0
        comunes = palabras_ref & palabras_est
        return (len(comunes) / len(palabras_ref)) * 100

    def evaluar_por_ideas(self, respuesta, ideas):
        respuesta_norm = self.normalizar(respuesta)
        puntaje = 0
        ideas_encontradas = []
        ideas_faltantes = []
        for idea in ideas:
            encontrada = False
            for palabra_clave in idea.get('palabras_clave', []):
                if self.normalizar(palabra_clave) in respuesta_norm:
                    encontrada = True
                    break
            registro = {
                'nombre': idea.get('nombre', 'Idea'),
                'peso': idea.get('peso', 0),
                'palabras_clave': idea.get('palabras_clave', [])
            }
            if encontrada:
                puntaje += idea.get('peso', 0)
                ideas_encontradas.append(registro)
            else:
                ideas_faltantes.append(registro)
        return puntaje, ideas_encontradas, ideas_faltantes

    def penalizar_errores(self, respuesta, errores_graves):
        respuesta_norm = self.normalizar(respuesta)
        penalizacion = 0
        errores_detectados = []
        for error in errores_graves or []:
            texto_error = self.normalizar(error.get('texto', ''))
            if texto_error and texto_error in respuesta_norm:
                penal = error.get('penalizacion', 20)
                penalizacion += penal
                errores_detectados.append(error.get('texto', texto_error))
        return min(penalizacion, 100), errores_detectados

    def evaluar(self, pregunta, referencia, respuesta, ideas, errores_graves=None):
        semantica_bruta, ideas_ok, ideas_missing = self.evaluar_por_ideas(respuesta, ideas)
        penalizacion, errores = self.penalizar_errores(respuesta, errores_graves)
        semantica_final = max(0, semantica_bruta - penalizacion)
        lexica = self.similitud_lexica_correcta(referencia, respuesta)
        coincidencia = self.coincidencia_palabras(referencia, respuesta)
        calificacion = (0.80 * semantica_final) + (0.20 * lexica)
        nota = calificacion / 10
        resultado = {
            'fecha': datetime.now().isoformat(),
            'pregunta': pregunta,
            'referencia': referencia,
            'respuesta': respuesta,
            'semantica': {
                'bruta': round(semantica_bruta, 1),
                'penalizacion': round(penalizacion, 1),
                'final': round(semantica_final, 1),
                'ideas_encontradas': ideas_ok,
                'ideas_faltantes': ideas_missing
            },
            'lexica': {
                'similitud': round(lexica, 1),
                'coincidencia_palabras': round(coincidencia, 1)
            },
            'calificacion': {
                'porcentaje': round(calificacion, 1),
                'nota_sobre_10': round(nota, 1)
            },
            'errores_detectados': errores
        }
        self.historial.append(resultado)
        return resultado

    def imprimir_resultados(self, resultados):
        print('\n' + '=' * 60)
        print(f"📋 PREGUNTA: {resultados['pregunta']}")
        print('=' * 60)
        print(f"\n📝 Respuesta del estudiante:\n   {resultados['respuesta']}")
        print('\n🎯 PUNTAJES:')
        print(f"   Semántica (ideas clave): {resultados['semantica']['final']:.1f}%")
        if resultados['semantica']['penalizacion'] > 0:
            print(f"   Penalización: -{resultados['semantica']['penalizacion']:.1f}%")
        print(f"   Léxica: {resultados['lexica']['similitud']:.1f}%")
        print('\n📊 CALIFICACIÓN:')
        print(f"   {resultados['calificacion']['porcentaje']:.1f}% → {resultados['calificacion']['nota_sobre_10']:.1f}/10")
        print('\n✅ Ideas encontradas:')
        for idea in resultados['semantica']['ideas_encontradas']:
            print(f"   ✓ {idea['nombre']} ({idea['peso']}%)")
        if resultados['semantica']['ideas_faltantes']:
            print('\n❌ Ideas faltantes:')
            for idea in resultados['semantica']['ideas_faltantes']:
                print(f"   ✗ {idea['nombre']} ({idea['peso']}%)")
        if resultados['errores_detectados']:
            print('\n⚠️ Errores detectados:')
            for error in resultados['errores_detectados']:
                print(f"   ❌ {error}")
        print(f"\n📈 Coincidencia de palabras: {resultados['lexica']['coincidencia_palabras']:.1f}%")
        print('=' * 60)

    def evaluar_desde_consola(self):
        print('\n' + '=' * 60)
        print('🤖 MODO INTERACTIVO DE EVALUACIÓN')
        print('=' * 60)
        pregunta = input('\n📋 Ingresa la pregunta: ').strip()
        referencia = input('\n📖 Ingresa la respuesta de referencia: ').strip()
        ideas = []
        num_ideas = int(input('\n💡 ¿Cuántas ideas clave quieres definir? '))
        peso_total = 0
        for i in range(num_ideas):
            print(f"\n--- Idea {i+1} ---")
            nombre = input('Nombre de la idea: ').strip()
            peso = float(input('Peso de la idea (%): '))
            peso_total += peso
            palabras = input('Palabras clave (separadas por coma): ').strip()
            ideas.append({
                'nombre': nombre,
                'peso': peso,
                'palabras_clave': [p.strip() for p in palabras.split(',') if p.strip()]
            })
        if abs(peso_total - 100) > 0.1:
            print(f"⚠️ El peso total es {peso_total}%, lo ideal es 100%.")
        errores_graves = []
        tiene_errores = input('\n¿Deseas definir errores graves? (s/n): ').strip().lower()
        if tiene_errores == 's':
            num_errores = int(input('Cuántos errores graves: '))
            for i in range(num_errores):
                texto = input(f'Frase falsa {i+1}: ').strip()
                penal = float(input('Penalización (%): '))
                errores_graves.append({'texto': texto, 'penalizacion': penal})
        respuesta = input('\n👨‍🎓 Ingresa la respuesta del estudiante: ').strip()
        resultado = self.evaluar(pregunta, referencia, respuesta, ideas, errores_graves)
        self.imprimir_resultados(resultado)
        return resultado

    def evaluar_multiples(self):
        print('\n' + '=' * 60)
        print('🔄 MODO EVALUACIÓN MÚLTIPLE')
        print('=' * 60)
        pregunta = input('\n📋 Pregunta: ').strip()
        referencia = input('\n📖 Respuesta de referencia: ').strip()
        ideas = []
        num_ideas = int(input('\n¿Cuántas ideas clave? '))
        for i in range(num_ideas):
            nombre = input(f'Nombre idea {i+1}: ').strip()
            peso = float(input('Peso (%): '))
            palabras = input('Palabras clave (separadas por coma): ').strip()
            ideas.append({
                'nombre': nombre,
                'peso': peso,
                'palabras_clave': [p.strip() for p in palabras.split(',') if p.strip()]
            })
        respuestas = []
        while True:
            nombre_est = input('\nNombre del estudiante (o fin para terminar): ').strip()
            if nombre_est.lower() == 'fin':
                break
            respuesta = input('Respuesta: ').strip()
            respuestas.append((nombre_est, respuesta))
        for nombre_est, respuesta in respuestas:
            resultado = self.evaluar(pregunta, referencia, respuesta, ideas)
            print(f"\n📊 {nombre_est}: {resultado['calificacion']['nota_sobre_10']:.1f}/10")
            self.imprimir_resultados(resultado)
        self.guardar_historial()
        return respuestas

    def guardar_historial(self, archivo='evaluaciones.json'):
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(self.historial, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Historial guardado en {archivo}")


def ejemplo_precargado():
    evaluador = EvaluadorRespuestas()
    pregunta = '¿Por qué la Tierra es un planeta habitable?'
    referencia = ('La Tierra es habitable porque tiene agua líquida, atmósfera con oxígeno, '
                  'temperatura adecuada y está a la distancia correcta del Sol.')
    ideas = [
        {'nombre': 'Agua líquida', 'peso': 25, 'palabras_clave': ['agua líquida', 'agua']},
        {'nombre': 'Atmósfera/oxígeno', 'peso': 25, 'palabras_clave': ['atmósfera', 'oxígeno', 'aire']},
        {'nombre': 'Temperatura adecuada', 'peso': 25, 'palabras_clave': ['temperatura', 'calor', 'frío']},
        {'nombre': 'Distancia al Sol', 'peso': 25, 'palabras_clave': ['distancia', 'sol', 'zona de habitabilidad']}
    ]
    errores_graves = [
        {'texto': 'tiene vida', 'penalizacion': 20},
        {'texto': 'estamos acostumbrados', 'penalizacion': 20}
    ]
    respuestas = [
        ('CASO A', 'Porque tiene agua, aire para respirar, no hace demasiado calor ni frío, y está a la distancia justa del Sol.'),
        ('CASO B', 'Porque tiene vida y estamos acostumbrados a vivir aquí.'),
        ('CASO C', referencia)
    ]
    for nombre, respuesta in respuestas:
        print(f"\n--- {nombre} ---")
        resultado = evaluador.evaluar(pregunta, referencia, respuesta, ideas, errores_graves)
        evaluador.imprimir_resultados(resultado)
    evaluador.guardar_historial()
    return evaluador


def main():
    print('\n' + '=' * 60)
    print('🎓 SISTEMA DE EVALUACIÓN DE RESPUESTAS')
    print('=' * 60)
    print('\nSelecciona una opción:')
    print('1. Ejecutar ejemplo precargado (Tierra habitable)')
    print('2. Modo interactivo (evaluar una respuesta)')
    print('3. Modo múltiple (evaluar varias respuestas)')
    print('4. Salir')
    opcion = input('\nOpción (1-4): ').strip()
    if opcion == '1':
        ejemplo_precargado()
    elif opcion == '2':
        evaluador = EvaluadorRespuestas()
        evaluador.evaluar_desde_consola()
        evaluador.guardar_historial()
    elif opcion == '3':
        evaluador = EvaluadorRespuestas()
        evaluador.evaluar_multiples()
    else:
        print('👋 Hasta luego!')


if __name__ == '__main__':
    main()
