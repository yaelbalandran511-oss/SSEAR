import re
import json
from datetime import datetime

# ============================================================
# EVALUADOR POR IDEAS CLAVE - VERSIÓN UNIVERSAL
# ============================================================

class EvaluadorRespuestas:
    def __init__(self):
        self.historial = []
    
    def normalizar(self, texto):
        """Limpia y normaliza texto para comparación"""
        texto = texto.lower()
        texto = re.sub(r'[áàä]', 'a', texto)
        texto = re.sub(r'[éèë]', 'e', texto)
        texto = re.sub(r'[íìï]', 'i', texto)
        texto = re.sub(r'[óòö]', 'o', texto)
        texto = re.sub(r'[úùü]', 'u', texto)
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    def similitud_lexica(self, referencia, respuesta):
        """Fórmula correcta: (2 * comunes) / (total_ref + total_res) * 100"""
        ref_norm = self.normalizar(referencia)
        res_norm = self.normalizar(respuesta)
        
        palabras_ref = set(ref_norm.split())
        palabras_res = set(res_norm.split())
        
        comunes = palabras_ref & palabras_res
        
        if not palabras_ref or not palabras_res:
            return 0.0
        
        return (2 * len(comunes)) / (len(palabras_ref) + len(palabras_res)) * 100
    
    def coincidencia_palabras(self, referencia, respuesta):
        """Porcentaje de palabras de referencia que aparecen en respuesta"""
        ref_norm = self.normalizar(referencia)
        res_norm = self.normalizar(respuesta)
        
        palabras_ref = set(ref_norm.split())
        palabras_res = set(res_norm.split())
        
        if not palabras_ref:
            return 0.0
        
        comunes = palabras_ref & palabras_res
        return (len(comunes) / len(palabras_ref)) * 100
    
    def evaluar_por_ideas(self, respuesta, ideas):
        """Evalúa basado en ideas clave definidas por el usuario"""
        respuesta_norm = self.normalizar(respuesta)
        puntaje = 0
        ideas_encontradas = []
        ideas_faltantes = []
        
        for idea in ideas:
            encontrada = False
            for palabra_clave in idea["palabras_clave"]:
                if palabra_clave.lower() in respuesta_norm:
                    encontrada = True
                    break
            
            if encontrada:
                puntaje += idea["peso"]
                ideas_encontradas.append({
                    "nombre": idea["nombre"],
                    "peso": idea["peso"],
                    "palabras_clave": idea["palabras_clave"]
                })
            else:
                ideas_faltantes.append({
                    "nombre": idea["nombre"],
                    "peso": idea["peso"],
                    "palabras_clave": idea["palabras_clave"]
                })
        
        return puntaje, ideas_encontradas, ideas_faltantes
    
    def penalizar_errores(self, respuesta, errores_graves):
        """Detecta y penaliza afirmaciones falsas"""
        respuesta_norm = self.normalizar(respuesta)
        penalizacion = 0
        errores_detectados = []
        
        for error in errores_graves:
            palabras_error = self.normalizar(error["texto"])
            if palabras_error in respuesta_norm:
                penalizacion += error.get("penalizacion", 20)
                errores_detectados.append(error["texto"])
        
        return min(penalizacion, 50), errores_detectados  # Máx 50% penalización
    
    def evaluar(self, pregunta, referencia, respuesta, ideas, errores_graves=None, 
                peso_semantica=0.80, peso_lexica=0.20):
        """
        Evalúa una respuesta de estudiante
        
        Parámetros:
        - pregunta: texto de la pregunta
        - referencia: respuesta ideal
        - respuesta: respuesta del estudiante
        - ideas: lista de diccionarios con {"nombre": str, "peso": float, "palabras_clave": list}
        - errores_graves: lista de diccionarios con {"texto": str, "penalizacion": float}
        - peso_semantica: peso para la semántica (default 0.80)
        - peso_lexica: peso para la léxica (default 0.20)
        """
        
        # Calcular puntajes
        semantica_bruta, ideas_ok, ideas_missing = self.evaluar_por_ideas(respuesta, ideas)
        
        # Penalizaciones
        penalizacion = 0
        errores = []
        if errores_graves:
            penalizacion, errores = self.penalizar_errores(respuesta, errores_graves)
        
        semantica_final = max(0, semantica_bruta - penalizacion)
        
        # Similitud léxica
        lexica = self.similitud_lexica(referencia, respuesta)
        coincidencia = self.coincidencia_palabras(referencia, respuesta)
        
        # Calificación final
        calificacion = (peso_semantica * semantica_final) + (peso_lexica * lexica)
        nota = calificacion / 10
        
        # Resultados
        resultados = {
            "fecha": datetime.now().isoformat(),
            "pregunta": pregunta,
            "respuesta_referencia": referencia,
            "respuesta_estudiante": respuesta,
            "semantica": {
                "bruta": round(semantica_bruta, 1),
                "penalizacion": round(penalizacion, 1),
                "final": round(semantica_final, 1),
                "ideas_encontradas": ideas_ok,
                "ideas_faltantes": ideas_missing
            },
            "lexica": {
                "similitud": round(lexica, 1),
                "coincidencia_palabras": round(coincidencia, 1)
            },
            "calificacion": {
                "porcentaje": round(calificacion, 1),
                "nota_sobre_10": round(nota, 1),
                "peso_semantica": peso_semantica,
                "peso_lexica": peso_lexica
            },
            "errores_detectados": errores
        }
        
        self.historial.append(resultados)
        return resultados
    
    def imprimir_resultados(self, resultados):
        """Imprime los resultados de forma legible"""
        print("\n" + "="*60)
        print(f"📋 PREGUNTA: {resultados['pregunta']}")
        print("="*60)
        
        print(f"\n📝 Respuesta del estudiante:")
        print(f"   {resultados['respuesta_estudiante']}")
        
        print(f"\n🎯 PUNTAJES:")
        print(f"   Semántica (ideas clave): {resultados['semantica']['bruta']:.1f}%")
        if resultados['semantica']['penalizacion'] > 0:
            print(f"   Penalización: -{resultados['semantica']['penalizacion']:.1f}%")
        print(f"   Semántica final: {resultados['semantica']['final']:.1f}%")
        print(f"   Léxica: {resultados['lexica']['similitud']:.1f}%")
        
        print(f"\n📊 CALIFICACIÓN:")
        print(f"   {resultados['calificacion']['porcentaje']:.1f}% → {resultados['calificacion']['nota_sobre_10']:.1f}/10")
        
        print(f"\n✅ Ideas encontradas ({len(resultados['semantica']['ideas_encontradas'])}):")
        for idea in resultados['semantica']['ideas_encontradas']:
            print(f"   ✓ {idea['nombre']} ({idea['peso']}%)")
        
        if resultados['semantica']['ideas_faltantes']:
            print(f"\n❌ Ideas faltantes ({len(resultados['semantica']['ideas_faltantes'])}):")
            for idea in resultados['semantica']['ideas_faltantes']:
                print(f"   ✗ {idea['nombre']} ({idea['peso']}%) - sugerencia: {idea['palabras_clave'][0]}")
        
        if resultados['errores_detectados']:
            print(f"\n⚠️ ERRORES DETECTADOS:")
            for error in resultados['errores_detectados']:
                print(f"   ❌ {error}")
        
        print(f"\n📈 Métricas adicionales:")
        print(f"   Coincidencia de palabras: {resultados['lexica']['coincidencia_palabras']:.1f}%")
    
    def guardar_historial(self, archivo="evaluaciones.json"):
        """Guarda el historial de evaluaciones en un archivo JSON"""
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(self.historial, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Historial guardado en {archivo}")
    
    def evaluar_desde_consola(self):
        """Modo interactivo: permite evaluar cualquier pregunta en tiempo real"""
        print("\n" + "="*60)
        print("🤖 EVALUADOR DE RESPUESTAS - MODO INTERACTIVO")
        print("="*60)
        
        # Ingresar pregunta
        pregunta = input("\n📋 Ingresa la pregunta: ")
        
        # Ingresar respuesta de referencia
        print("\n📖 Ingresa la respuesta de referencia (ideal):")
        referencia = input("> ")
        
        # Configurar ideas clave
        print("\n💡 Ahora configura las IDEAS CLAVE que debe tener la respuesta:")
        ideas = []
        num_ideas = int(input("¿Cuántas ideas clave quieres definir? (ej: 4): "))
        
        peso_total = 0
        for i in range(num_ideas):
            print(f"\n--- Idea {i+1} ---")
            nombre = input("  Nombre de la idea: ")
            peso = float(input(f"  Peso (0-100%, suma debe ser 100%): "))
            peso_total += peso
            
            palabras = input("  Palabras clave (separadas por coma): ")
            palabras_clave = [p.strip().lower() for p in palabras.split(",")]
            ideas.append({
                "nombre": nombre,
                "peso": peso,
                "palabras_clave": palabras_clave
            })
        
        if abs(peso_total - 100) > 0.1:
            print(f"⚠️ Advertencia: El peso total es {peso_total}%, debería ser 100%")
        
        # Configurar errores graves (opcional)
        tiene_errores = input("\n¿Quieres definir errores graves? (s/n): ").lower()
        errores_graves = []
        if tiene_errores == 's':
            num_errores = int(input("¿Cuántos errores graves? "))
            for i in range(num_errores):
                texto = input(f"  Error {i+1} (frase falsa): ")
                penalizacion = float(input(f"  Penalización (% a restar, ej: 20): "))
                errores_graves.append({
                    "texto": texto,
                    "penalizacion": penalizacion
                })
        
        # Ingresar respuesta del estudiante
        print("\n👨‍🎓 Ingresa la respuesta del estudiante:")
        respuesta = input("> ")
        
        # Evaluar
        resultados = self.evaluar(pregunta, referencia, respuesta, ideas, errores_graves)
        self.imprimir_resultados(resultados)
        
        return resultados


# ============================================================
# EJEMPLOS DE USO
# ============================================================

def ejemplo_precargado():
    """Ejecuta un ejemplo con datos precargados"""
    print("\n" + "="*60)
    print("📚 EJEMPLO CON DATOS PRECARGADOS")
    print("="*60)
    
    evaluador = EvaluadorRespuestas()
    
    # Ejemplo 1: Tierra habitable
    ideas_tierra = [
        {"nombre": "Agua líquida", "peso": 25, "palabras_clave": ["agua líquida", "agua"]},
        {"nombre": "Atmósfera/oxígeno", "peso": 25, "palabras_clave": ["atmósfera", "oxígeno", "aire"]},
        {"nombre": "Temperatura adecuada", "peso": 25, "palabras_clave": ["temperatura", "calor", "frío"]},
        {"nombre": "Distancia al Sol", "peso": 25, "palabras_clave": ["distancia", "sol", "zona de habitabilidad"]}
    ]
    
    errores_tierra = [
        {"texto": "tiene vida", "penalizacion": 20},
        {"texto": "estamos acostumbrados", "penalizacion": 25}
    ]
    
    resultados = evaluador.evaluar(
        pregunta="¿Por qué la Tierra es un planeta habitable?",
        referencia="La Tierra es habitable porque tiene agua líquida, atmósfera con oxígeno, temperatura adecuada y está a la distancia correcta del Sol.",
        respuesta="Porque tiene agua, aire para respirar, no hace demasiado calor ni frío, y está a la distancia justa del Sol.",
        ideas=ideas_tierra,
        errores_graves=errores_tierra
    )
    evaluador.imprimir_resultados(resultados)
    
    return evaluador


def modo_usuario():
    """Permite al usuario evaluar cualquier texto en tiempo real"""
    evaluador = EvaluadorRespuestas()
    evaluador.evaluar_desde_consola()
    return evaluador


def evaluar_multiples():
    """Evalúa múltiples respuestas para una misma pregunta"""
    print("\n" + "="*60)
    print("🔄 MODO EVALUACIÓN MÚLTIPLE")
    print("="*60)
    
    evaluador = EvaluadorRespuestas()
    
    # Configurar pregunta y criterios
    pregunta = input("\n📋 Pregunta: ")
    referencia = input("\n📖 Respuesta de referencia: ")
    
    print("\n💡 Definir ideas clave:")
    ideas = []
    num_ideas = int(input("Número de ideas clave: "))
    
    for i in range(num_ideas):
        nombre = input(f"  Idea {i+1} - nombre: ")
        peso = float(input(f"  Peso (%): "))
        palabras = input(f"  Palabras clave (separadas por coma): ")
        ideas.append({
            "nombre": nombre,
            "peso": peso,
            "palabras_clave": [p.strip().lower() for p in palabras.split(",")]
        })
    
    # Evaluar múltiples estudiantes
    respuestas = []
    while True:
        print("\n" + "-"*40)
        nombre_est = input("Nombre del estudiante (o 'fin' para terminar): ")
        if nombre_est.lower() == 'fin':
            break
        respuesta = input("Respuesta: ")
        respuestas.append((nombre_est, respuesta))
    
    # Evaluar todos
    for nombre_est, respuesta in respuestas:
        resultados = evaluador.evaluar(pregunta, referencia, respuesta, ideas)
        print(f"\n📊 {nombre_est}: {resultados['calificacion']['nota_sobre_10']:.1f}/10")
    
    evaluador.guardar_historial()
    return evaluador


# ============================================================
# EJECUTAR PROGRAMA
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎓 SISTEMA DE EVALUACIÓN DE RESPUESTAS")
    print("="*60)
    print("\nSelecciona una opción:")
    print("1. Ejecutar ejemplo precargado (Tierra habitable)")
    print("2. Modo interactivo (evaluar una respuesta)")
    print("3. Modo múltiple (evaluar varias respuestas)")
    print("4. Salir")
    
    opcion = input("\nOpción (1-4): ")
    
    if opcion == "1":
        evaluador = ejemplo_precargado()
        evaluador.guardar_historial()
    elif opcion == "2":
        evaluador = modo_usuario()
        evaluador.guardar_historial()
    elif opcion == "3":
        evaluador = evaluar_multiples()
    else:
        print("👋 Hasta luego!")
