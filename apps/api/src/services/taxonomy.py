from __future__ import annotations

AREAS = [
    "lectura_critica",
    "matematicas",
    "sociales_ciudadanas",
    "ciencias_naturales",
    "ingles",
]

STRATEGIC_AREA_WEIGHTS: dict[str, float] = {
    "ciencias_naturales": 1.00,
    "matematicas": 0.95,
    "sociales_ciudadanas": 0.85,
    "ingles": 0.35,
    "lectura_critica": 0.25,
}

AREA_TOPIC_HINTS: dict[str, dict[str, list[str]]] = {
    "matematicas": {
        "porcentajes": ["porcentaje", "%", "descuento", "incremento"],
        "razones_y_proporciones": ["razon", "proporcion", "relacion"],
        "regla_de_tres": ["directamente proporcional", "inversamente proporcional"],
        "ecuaciones_lineales": ["ecuacion", "x", "despejar"],
        "plano_cartesiano": ["plano cartesiano", "coordenada"],
        "funciones_lineales": ["funcion lineal", "pendiente", "recta"],
        "lectura_de_graficas": ["grafica", "tabla", "diagrama"],
        "promedio_mediana_moda": ["promedio", "mediana", "moda"],
        "probabilidad_basica": ["probabilidad", "azar"],
        "areas_y_perimetros": ["area", "perimetro"],
        "trigonometria_basica": ["seno", "coseno", "tangente", "triangulo rectangulo"],
    },
    "ciencias_naturales": {
        "celula": ["celula", "organelo", "membrana"],
        "adn_genes_herencia": ["adn", "gen", "herencia", "alelo"],
        "ecosistemas": ["ecosistema", "cadena alimentaria", "poblacion"],
        "fotosintesis_respiracion": ["fotosintesis", "respiracion"],
        "atomos_y_moleculas": ["atomo", "molecula"],
        "tabla_periodica_basica": ["tabla periodica", "grupo", "periodo"],
        "enlaces_quimicos": ["enlace", "ionico", "covalente"],
        "mezclas_y_soluciones": ["mezcla", "solucion", "concentracion"],
        "cambios_fisicos_y_quimicos": ["cambio fisico", "cambio quimico"],
        "fuerza_y_movimiento": ["fuerza", "movimiento", "velocidad", "aceleracion"],
        "energia": ["energia", "trabajo"],
        "calor_temperatura": ["calor", "temperatura"],
        "electricidad_basica": ["corriente", "voltaje", "resistencia"],
        "variables_experimentales": ["variable independiente", "variable dependiente", "control"],
        "analisis_de_graficas_cientificas": ["grafica", "experimento", "datos"],
    },
    "sociales_ciudadanas": {
        "constitucion_1991": ["constitucion", "1991"],
        "ramas_del_poder": ["rama ejecutiva", "rama legislativa", "rama judicial"],
        "derechos_fundamentales": ["derecho fundamental", "derechos fundamentales"],
        "accion_de_tutela": ["tutela"],
        "mecanismos_de_participacion": ["referendo", "plebiscito", "cabildo", "voto"],
        "conflicto_armado_colombiano": ["conflicto armado"],
        "desplazamiento_forzado": ["desplazamiento"],
        "acuerdo_de_paz": ["acuerdo de paz"],
        "justicia_transicional": ["justicia transicional"],
        "desigualdad": ["desigualdad", "inequidad"],
        "estado_y_ciudadania": ["ciudadania", "estado"],
    },
    "lectura_critica": {
        "inferencia": ["inferir", "se deduce", "implica"],
        "argumentacion": ["argumento", "tesis", "premisa"],
        "intencion_del_autor": ["intencion", "proposito"],
        "estructura_textual": ["estructura", "conector"],
    },
    "ingles": {
        "vocabulario": ["meaning", "word", "synonym"],
        "gramatica": ["grammar", "verb", "tense"],
        "comprension_lectora": ["text", "according to", "main idea"],
        "coherencia": ["complete", "sentence", "paragraph"],
    },
}


def infer_topic(area: str, text: str) -> str:
    normalized = text.lower()
    for topic, hints in AREA_TOPIC_HINTS.get(area, {}).items():
        if any(hint in normalized for hint in hints):
            return topic
    return "sin_clasificar"
