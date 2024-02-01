import random
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon

# Definición del terreno
terreno_x = np.array([0, 275.23, 275.44, 0, 0])
terreno_y = np.array([0, 0, 106.01, 95.18, 0])
# Parámetros para la primera cámara
x_camara = 0
y_camara = 0
focal = 28
angulo_vision = 113
distancia_max = 50
#angulo_rotacion = 90
def calcular_area_triangulo(x_camara, y_camara, angulo_vision, distancia_max, angulo_rotacion, terreno_x, terreno_y, camaras_antiguas):
    angulo_rad = np.radians(angulo_rotacion)
    x1_rotado = x_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.cos(angulo_rad)
    y1_rotado = y_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.sin(angulo_rad)
    
    x2_rotado = x_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.cos(angulo_rad - np.radians(angulo_vision))
    y2_rotado = y_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.sin(angulo_rad - np.radians(angulo_vision))

    triangulo_vision = Polygon([(x_camara, y_camara), (x1_rotado, y1_rotado), (x2_rotado, y2_rotado)])

    terreno = Polygon(zip(terreno_x, terreno_y))
    
    # Verificar intersección con cámaras antiguas
    for camara_antigua in camaras_antiguas:
        area_interseccion = triangulo_vision.intersection(Polygon([(camara_antigua[0], camara_antigua[1]), 
                                                                    (camara_antigua[0] + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.cos(np.radians(camara_antigua[2])), 
                                                                     camara_antigua[1] + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.sin(np.radians(camara_antigua[2]))),
                                                                    (camara_antigua[0] + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.cos(np.radians(camara_antigua[2] - angulo_vision)), 
                                                                     camara_antigua[1] + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.sin(np.radians(camara_antigua[2] - angulo_vision))),
                                                                    (camara_antigua[0], camara_antigua[1])])).area
        if area_interseccion > 0:
            # Si hay intersección, se considera que la cámara no cubre área adicional
            return 0

    # Si no hay intersección con cámaras antiguas, se calcula la intersección con el terreno normalmente
    area_interseccion = triangulo_vision.intersection(terreno).area
    return area_interseccion

def dibujar_camara(x_camara, y_camara, focal, angulo_vision, distancia_max, angulo_rotacion, terreno_x, terreno_y, camaras_antiguas):
    x_camara, y_camara = limitar_a_terreno(x_camara, y_camara, terreno_x, terreno_y)
    area_total = calcular_area_triangulo(x_camara, y_camara, angulo_vision, distancia_max, angulo_rotacion, terreno_x, terreno_y, camaras_antiguas)
    print(f"Área total cubierta por la cámara: {area_total} Metros cuadrados")

    plt.plot(x_camara, y_camara, marker='o', markersize=10, color='red')

    angulo_rad = np.radians(angulo_rotacion)
    x1_rotado = x_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.cos(angulo_rad)
    y1_rotado = y_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.sin(angulo_rad)

    x2_rotado = x_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.cos(angulo_rad - np.radians(angulo_vision))
    y2_rotado = y_camara + distancia_max * np.tan(np.radians(angulo_vision / 2)) * np.sin(angulo_rad - np.radians(angulo_vision))

    plt.fill([x_camara, x1_rotado, x2_rotado, x_camara],
             [y_camara, y1_rotado, y2_rotado, y_camara],
             color='blue', alpha=0.3, label='Área de visión')

def limitar_a_terreno(x_camara, y_camara, terreno_x, terreno_y):
    # Limitar las cámaras a los límites del terreno
    x_camara = np.clip(x_camara, min(terreno_x), max(terreno_x))
    y_camara = np.clip(y_camara, min(terreno_y), max(terreno_y))
    return x_camara, y_camara

def inicializar_poblacion(tamano_poblacion, n_camaras):
    return [
        [
            [terreno_x[i], terreno_y[j], random.uniform(*rango_angulo)]
            for i in [0, 1, 2, 3]
            for j in [0, 2]
        ]
        for _ in range(tamano_poblacion)
    ]






def evaluar_aptitud(individuo):
    # Modificar el cálculo de área teniendo en cuenta las cámaras antiguas
    area_cubierta_total = sum(calcular_area_triangulo(individuo[i][0], individuo[i][1], angulo_vision, distancia_max, individuo[i][2], terreno_x, terreno_y, individuo[:i]) for i in range(len(individuo)))
    return area_cubierta_total

def seleccion_por_torneo(poblacion, tamano_torneo):
    torneo = random.sample(poblacion, tamano_torneo)
    torneo.sort(key=lambda x: evaluar_aptitud(x), reverse=True)
    return torneo[0]

def cruzamiento_un_punto(padre1, padre2):
    punto_corte = random.randint(1, n_camaras - 1)
    hijo = padre1[:punto_corte] + padre2[punto_corte:]
    return hijo

def mutacion_inversion_binaria(individuo, prob_mutacion):
    for i in range(n_camaras):
        if random.random() < prob_mutacion:
            individuo[i] = [random.uniform(*rango_x), random.uniform(*rango_y), random.uniform(*rango_angulo)]
    return individuo


n_generaciones = 40
prob_cruce = 0.8
tamano_poblacion = 50
n_camaras = 5
prob_mutacion = 0.1
rango_x = (min(terreno_x), max(terreno_x))
rango_y = (min(terreno_y), max(terreno_y))
rango_angulo = (0, 360)
# Seguimiento del fitness a lo largo de las generaciones
mejor_fitness_historia = []
promedio_fitness_historia = []
peor_fitness_historia = []

# Algoritmo genético
poblacion = inicializar_poblacion(tamano_poblacion, n_camaras)

for generacion in range(n_generaciones):
    nueva_poblacion = []

    # Evaluación de la población
    fitness_poblacion = [evaluar_aptitud(individuo) for individuo in poblacion]
    mejor_fitness = max(fitness_poblacion)
    promedio_fitness = np.mean(fitness_poblacion)
    peor_fitness = min(fitness_poblacion)

    # Guardar en el historial
    mejor_fitness_historia.append(mejor_fitness)
    promedio_fitness_historia.append(promedio_fitness)
    peor_fitness_historia.append(peor_fitness)

    for _ in range(tamano_poblacion // 2):
        padre1 = seleccion_por_torneo(poblacion, 5)
        padre2 = seleccion_por_torneo(poblacion, 5)

        # Aplicar cruce solo si se cumple la probabilidad de cruce
        if random.random() < prob_cruce:
            hijo1 = cruzamiento_un_punto(padre1, padre2)
            hijo2 = cruzamiento_un_punto(padre1, padre2)
        else:
            hijo1 = padre1
            hijo2 = padre2

        hijo1 = mutacion_inversion_binaria(hijo1, prob_mutacion)
        hijo2 = mutacion_inversion_binaria(hijo2, prob_mutacion)

        nueva_poblacion.extend([hijo1, hijo2])

    poblacion = nueva_poblacion

# Obtener el mejor individuo de la población final
mejor_individuo = max(poblacion, key=evaluar_aptitud)

# Dibujar el terreno
plt.plot(terreno_x, terreno_y, color='green', label='Terreno')

# Dibujar las cámaras del mejor individuo
for i in range(n_camaras):
    dibujar_camara(mejor_individuo[i][0], mejor_individuo[i][1], focal, angulo_vision, distancia_max, mejor_individuo[i][2], terreno_x, terreno_y, mejor_individuo[:i])

# Imprimir el mejor y el peor individuo encontrados
print("\nMejor individuo encontrado:")
print(mejor_individuo)
plt.axis('equal')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.title('Grafico Colocación de Cámaras')


plt.figure()
generaciones = range(n_generaciones)
plt.plot(generaciones, mejor_fitness_historia, label='Mejor Individuo')
plt.plot(generaciones, promedio_fitness_historia, label='Promedio Individuo')
plt.plot(generaciones, peor_fitness_historia, label='Peor Individuo')
plt.xlabel('Generación')
plt.ylabel('Metros Cubiertos(m2)')
plt.legend()
plt.title('Historial ')

plt.show()