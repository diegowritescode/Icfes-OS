# ICFES OS

## Sistema Personal de Inteligencia Adaptativa para Preparación Saber 11

**Versión:** 1.0
**Autor:** Diego Andrés Ramírez Mejía
**Objetivo operativo:** maximizar puntaje Saber 11 en 60 días mediante análisis automatizado de preguntas, detección de patrones, priorización de temas y práctica adaptativa.
**Meta académica:** asegurar un puntaje competitivo para ingreso a programas de ingeniería de software, sistemas, ciencia de datos o áreas relacionadas.

---

# 1. Resumen ejecutivo

ICFES OS es un sistema local de análisis, clasificación y entrenamiento adaptativo para el examen Saber 11. Su propósito no es reemplazar el estudio, sino convertir un gran volumen de cuadernillos, simulacros, respuestas y explicaciones en un motor de decisión diario.

El sistema parte de una realidad práctica: el estudiante tiene poco tiempo, recursos abundantes y fortalezas/desventajas claras. En este caso, las fortalezas son Lectura Crítica, Inglés, comprensión verbal y capacidad técnica. Las debilidades son Ciencias Naturales, Matemáticas intermedias y Sociales/Historia de Colombia.

La tesis central del proyecto es:

> El rendimiento en Saber 11 puede mejorar más rápido si el estudiante deja de estudiar por intuición y empieza a estudiar según frecuencia histórica, recencia, errores personales y retorno marginal por área.

ICFES OS transforma PDFs en datos estructurados, clasifica preguntas por tema y competencia, identifica patrones recurrentes, registra intentos del usuario, calcula prioridades de estudio y genera sesiones diarias optimizadas.

El sistema debe construirse en un día, con una arquitectura deliberadamente simple, local-first y enfocada en utilidad inmediata.

---

# 2. Problema

El estudiante cuenta con múltiples recursos: cuadernillos oficiales, simulacros, bancos de preguntas, respuestas y explicaciones. Sin embargo, el volumen de material genera tres problemas:

1. **Sobrecarga de información**
   Tener cientos o miles de preguntas no indica cuáles estudiar primero.

2. **Ausencia de priorización**
   No todos los temas tienen el mismo retorno. Algunos aparecen más, otros son más recientes, otros son críticos para el usuario porque los falla constantemente.

3. **Corrección ineficiente**
   Resolver preguntas sin clasificar errores produce una falsa sensación de avance. El aprendizaje real ocurre al transformar cada error en concepto, patrón y repetición.

4. **Falta de personalización**
   Un plan genérico de estudio no toma en cuenta que el estudiante ya domina Lectura Crítica e Inglés, pero está débil en Ciencias Naturales, Matemáticas y Sociales.

ICFES OS resuelve esto mediante un pipeline de análisis y práctica adaptativa.

---

# 3. Principios de diseño

## 3.1 Velocidad sobre perfección

El sistema debe ser funcional en 24 horas. No se busca una plataforma bonita ni escalable. Se busca una herramienta que produzca decisiones útiles desde el primer día.

## 3.2 Local-first

Los PDFs, preguntas y registros personales deben vivir localmente. Esto reduce complejidad, evita dependencias innecesarias y permite trabajar rápido.

## 3.3 Preguntas antes que teoría

El sistema no parte de “temas del colegio”, sino de preguntas reales. La ruta de aprendizaje debe ser:

> pregunta → error → concepto → patrón → repetición → dominio

## 3.4 Priorización por retorno

El tiempo se asigna según una fórmula de prioridad, no según ansiedad. Si Lectura Crítica ya está en 95/100, el sistema no debe recomendar estudiarla intensamente. Si Ciencias está bajo y pesa en el puntaje global, debe recibir más atención.

## 3.5 Explicabilidad

Cada recomendación debe poder justificarse:

* aparece mucho;
* aparece recientemente;
* el usuario lo falla;
* es base para otros temas;
* consume poco tiempo y da alto retorno;
* está alineado con competencias del examen.

---

# 4. Alcance del sistema

## 4.1 Incluido en MVP de 1 día

ICFES OS v1 debe incluir:

1. Carga manual de preguntas desde CSV/JSON.
2. Extracción semiautomática de texto desde PDFs.
3. Clasificación automática con IA.
4. Registro de intentos del usuario.
5. Dashboard básico.
6. Ranking de temas prioritarios.
7. Búsqueda semántica de preguntas similares.
8. Generador de explicación personalizada.
9. Plan diario de estudio.
10. Repetición espaciada básica.

## 4.2 No incluido en MVP

No se construirá en v1:

* app móvil;
* autenticación;
* multiusuario;
* OCR perfecto;
* extracción perfecta de imágenes;
* predicción de preguntas exactas;
* modelo entrenado desde cero;
* sistema de pagos;
* interfaz compleja;
* scraping masivo innecesario.

---

# 5. Arquitectura general

## 5.1 Stack recomendado para 1 día

**Lenguaje:** Python
**Interfaz:** Streamlit
**Base de datos:** SQLite
**Extracción PDF:** PyMuPDF
**Dataframes:** Pandas
**Embeddings:** ChromaDB o FAISS
**IA:** Claude, GPT o modelo compatible vía API
**Formato intermedio:** JSONL
**Visualización:** Streamlit charts / tablas

## 5.2 Arquitectura lógica

```txt
PDFs / CSV / JSON
      ↓
Ingesta de documentos
      ↓
Extracción de preguntas
      ↓
Normalización
      ↓
Clasificación IA
      ↓
Base SQLite + Vector DB
      ↓
Dashboard + práctica
      ↓
Registro de intentos
      ↓
Ranking de temas + plan diario
```

---

# 6. Modelo de datos

## 6.1 Tabla: questions

```sql
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    source_file TEXT,
    year INTEGER,
    area TEXT,
    question_number INTEGER,
    statement TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT,
    explanation TEXT,
    page INTEGER,
    raw_text TEXT,
    created_at TEXT
);
```

## 6.2 Tabla: classifications

```sql
CREATE TABLE classifications (
    question_id TEXT PRIMARY KEY,
    area TEXT,
    subarea TEXT,
    topic TEXT,
    subtopic TEXT,
    competence TEXT,
    skill TEXT,
    difficulty INTEGER,
    requires_formula INTEGER,
    requires_graph INTEGER,
    requires_colombia_context INTEGER,
    concepts_json TEXT,
    keywords_json TEXT,
    confidence REAL,
    FOREIGN KEY(question_id) REFERENCES questions(id)
);
```

## 6.3 Tabla: attempts

```sql
CREATE TABLE attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct INTEGER,
    confidence INTEGER,
    time_seconds INTEGER,
    error_type TEXT,
    notes TEXT,
    attempted_at TEXT,
    review_after TEXT,
    FOREIGN KEY(question_id) REFERENCES questions(id)
);
```

## 6.4 Tabla: topic_stats

```sql
CREATE TABLE topic_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT,
    topic TEXT,
    subtopic TEXT,
    total_questions INTEGER,
    recent_questions INTEGER,
    user_attempts INTEGER,
    user_errors INTEGER,
    error_rate REAL,
    avg_time_seconds REAL,
    priority_score REAL,
    updated_at TEXT
);
```

---

# 7. Taxonomía académica

La taxonomía debe ser simple, estable y útil. No debe intentar cubrir todo el currículo colombiano, sino clasificar preguntas de forma accionable.

## 7.1 Áreas

```txt
lectura_critica
matematicas
sociales_ciudadanas
ciencias_naturales
ingles
```

## 7.2 Matemáticas

Subáreas:

```txt
aritmetica
algebra
geometria
estadistica
probabilidad
funciones
razonamiento_cuantitativo
```

Temas de alta prioridad inicial:

```txt
porcentajes
razones_y_proporciones
regla_de_tres
fracciones_y_decimales
ecuaciones_lineales
plano_cartesiano
funciones_lineales
lectura_de_graficas
promedio_mediana_moda
probabilidad_basica
areas_y_perimetros
volumenes_basicos
```

## 7.3 Ciencias Naturales

Subáreas:

```txt
biologia
quimica
fisica
ciencia_tecnologia_sociedad
indagacion
```

Temas de alta prioridad inicial:

```txt
celula
adn_genes_herencia
ecosistemas
fotosintesis_respiracion
materia_y_estados
atomos_y_moleculas
tabla_periodica_basica
enlaces_quimicos
mezclas_y_soluciones
cambios_fisicos_y_quimicos
conservacion_de_masa
fuerza_y_movimiento
energia
calor_temperatura
ondas
electricidad_basica
variables_experimentales
analisis_de_graficas_cientificas
```

## 7.4 Sociales y Ciudadanas

Subáreas:

```txt
constitucion
estado_colombiano
democracia
derechos_humanos
conflicto_armado
economia_basica
geografia
ciudadania
analisis_de_perspectivas
```

Temas de alta prioridad inicial:

```txt
constitucion_1991
ramas_del_poder
derechos_fundamentales
accion_de_tutela
mecanismos_de_participacion
conflicto_armado_colombiano
guerrillas
paramilitarismo
narcotrafico
victimas
desplazamiento_forzado
acuerdo_de_paz
justicia_transicional
desigualdad
estado_y_ciudadania
```

## 7.5 Lectura Crítica

Subáreas:

```txt
comprension_literal
inferencia
estructura_textual
intencion_del_autor
argumentacion
vocabulario_contextual
intertextualidad
```

Uso en este proyecto: mantenimiento, no foco intensivo.

## 7.6 Inglés

Subáreas:

```txt
vocabulario
gramatica
comprension_lectora
coherencia
pragmatica
```

Uso en este proyecto: mantenimiento y adaptación al formato.

---

# 8. Pipeline de ingesta

## 8.1 Fase 1: registro de archivos

Cada PDF debe registrarse con metadata mínima:

```json
{
  "source_file": "saber11_ciencias_2023.pdf",
  "year": 2023,
  "area": "ciencias_naturales",
  "source_type": "official_past_exam",
  "priority": "high"
}
```

## 8.2 Fase 2: extracción de texto

La extracción automática no necesita ser perfecta. El objetivo inicial es obtener bloques de texto razonables.

Script:

```python
import fitz
from pathlib import Path

def extract_pdf_text(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({
            "page": i + 1,
            "text": text
        })
    return pages
```

## 8.3 Fase 3: segmentación de preguntas

Reglas iniciales:

* detectar números de pregunta;
* detectar opciones A, B, C, D;
* unir texto previo como enunciado;
* conservar página y archivo;
* permitir corrección manual.

La extracción perfecta no es necesaria. Con que el sistema pueda procesar 300–500 preguntas útiles el primer día, ya cumple.

---

# 9. Clasificación con IA

## 9.1 Objetivo

Convertir cada pregunta en metadata accionable.

## 9.2 Prompt de clasificación

```txt
Eres un clasificador experto de preguntas del examen Saber 11 de Colombia.

Clasifica la pregunta usando una taxonomía útil para preparación intensiva.

Devuelve únicamente JSON válido. No expliques fuera del JSON.

Esquema:
{
  "area": "",
  "subarea": "",
  "topic": "",
  "subtopic": "",
  "competence": "",
  "skill": "",
  "difficulty": 1,
  "requires_formula": false,
  "requires_graph": false,
  "requires_colombia_context": false,
  "concepts": [],
  "keywords": [],
  "likely_error_types": [],
  "confidence": 0.0
}

Criterios:
- difficulty va de 1 a 5.
- Usa nombres de temas simples y consistentes.
- Si es Ciencias, distingue biología, química, física, CTS o indagación.
- Si es Sociales, identifica si requiere contexto colombiano.
- Si es Matemáticas, identifica si requiere procedimiento, gráfica, fórmula o razonamiento.
- Si puede resolverse principalmente leyendo, indícalo en skill.

Pregunta:
{{question_text}}

Opciones:
A. {{option_a}}
B. {{option_b}}
C. {{option_c}}
D. {{option_d}}
```

## 9.3 Validación

Toda clasificación debe guardar un campo `confidence`.

Regla:

```txt
confidence >= 0.80 → usable automáticamente
0.60 <= confidence < 0.80 → revisar después
confidence < 0.60 → excluir de análisis prioritario
```

---

# 10. Motor de embeddings

## 10.1 Objetivo

Encontrar preguntas similares para descubrir patrones.

Ejemplos de uso:

* “Dame preguntas parecidas a esta de alcoholes.”
* “Agrupa preguntas de conflicto armado.”
* “Encuentra preguntas de lectura de gráficas en ciencias y matemáticas.”
* “Busca todas las preguntas parecidas a esta que fallé.”

## 10.2 Texto embebido

No se debe embebir solo el enunciado. Se debe crear un documento enriquecido:

```txt
Área: ciencias_naturales
Subárea: química
Tema: enlaces químicos
Subtema: polaridad molecular
Competencia: uso comprensivo del conocimiento científico

Pregunta:
...

Opciones:
A...
B...
C...
D...

Explicación:
...
```

## 10.3 Metadata vectorial

```json
{
  "question_id": "q_2024_ciencias_034",
  "year": 2024,
  "area": "ciencias_naturales",
  "topic": "enlaces_quimicos",
  "difficulty": 3
}
```

---

# 11. Registro de intentos

## 11.1 Flujo de práctica

El estudiante responde una pregunta y registra:

* respuesta elegida;
* seguridad del 1 al 5;
* tiempo usado;
* tipo de error;
* nota personal.

## 11.2 Tipos de error

```txt
no_sabia_concepto
formula_olvidada
lectura_apresurada
interprete_mal_grafica
calculo_mal
confundi_conceptos
cai_en_distractor
me_falto_contexto_colombia
dude_entre_dos
tiempo_excesivo
```

## 11.3 Interpretación de errores

No todos los errores valen igual.

```txt
no_sabia_concepto → estudiar teoría mínima
formula_olvidada → crear tarjeta/fórmula
interprete_mal_grafica → practicar gráficas
lectura_apresurada → estrategia de lectura
cai_en_distractor → analizar opciones
tiempo_excesivo → entrenamiento cronometrado
```

---

# 12. Scoring de prioridad

## 12.1 Variables

Para cada tema:

```txt
frequency_total
frequency_recent
personal_error_rate
avg_time_penalty
difficulty_penalty
strategic_weight
days_since_review
mastery_score
```

## 12.2 Fórmula v1

```txt
priority_score =
    0.25 * normalized_frequency_total
  + 0.25 * normalized_frequency_recent
  + 0.25 * personal_error_rate
  + 0.10 * avg_time_penalty
  + 0.10 * strategic_weight
  + 0.05 * days_since_review_factor
  - 0.20 * mastery_score
```

## 12.3 Interpretación

```txt
priority_score >= 0.75 → estudiar hoy
0.55 - 0.74 → estudiar esta semana
0.35 - 0.54 → mantenimiento
< 0.35 → baja prioridad
```

## 12.4 Pesos estratégicos iniciales por perfil

Dado el perfil del estudiante:

```txt
ciencias_naturales: 1.00
matematicas: 0.95
sociales_ciudadanas: 0.85
ingles: 0.35
lectura_critica: 0.25
```

Esto no significa abandonar Lectura e Inglés. Significa que el retorno marginal está en Ciencias, Matemáticas y Sociales.

---

# 13. Motor de recomendación diaria

## 13.1 Entrada

El motor recibe:

* días restantes;
* horas disponibles hoy;
* temas con mayor prioridad;
* preguntas falladas;
* temas no revisados;
* balance por área;
* fatiga cognitiva esperada.

## 13.2 Salida

Ejemplo:

```txt
Plan diario recomendado

Bloque 1 - Matemáticas, 90 min
Tema: porcentajes, proporciones y gráficas.
Tarea: 25 preguntas + corrección.

Bloque 2 - Ciencias, 120 min
Tema: enlaces químicos, mezclas y soluciones.
Tarea: mini teoría + 20 preguntas.

Bloque 3 - Sociales, 75 min
Tema: Constitución, derechos y tutela.
Tarea: lectura guiada + 20 preguntas.

Bloque 4 - Revisión, 45 min
Tarea: repetir 12 preguntas falladas hace 3 días.
```

## 13.3 Regla de oro

El sistema debe evitar recomendar áreas ya fuertes salvo para mantenimiento.

```txt
Si area_score_estimate >= 85:
    max_daily_minutes = 30
```

---

# 14. Tutor IA

## 14.1 Objetivo

Convertir cada error en una microclase.

## 14.2 Prompt de explicación

```txt
Eres un tutor experto en Saber 11. 
Explícale esta pregunta a un estudiante que tiene buena comprensión lectora, pero bases débiles en ciencias, matemáticas y sociales.

Pregunta:
{{question}}

Respuesta correcta:
{{correct_answer}}

Respuesta del estudiante:
{{user_answer}}

Tipo de error:
{{error_type}}

Explica:
1. Por qué la respuesta correcta es correcta.
2. Por qué la respuesta del estudiante es incorrecta.
3. Qué concepto mínimo debe aprender.
4. Cómo reconocer este patrón en el futuro.
5. Una regla mental o truco útil.
6. Una mini-lección de máximo 180 palabras.

Usa lenguaje claro, directo y sin tecnicismos innecesarios.
```

## 14.3 Salida esperada

```txt
Fallaste porque confundiste el nombre de la sustancia con la propiedad que el ICFES quería evaluar. En alcoholes, lo importante no es memorizar listas, sino reconocer el grupo -OH. Ese grupo cambia propiedades como polaridad, solubilidad y tipo de interacción con otras moléculas.

Patrón:
Cuando una pregunta mencione estructura molecular y propiedades, busca qué parte de la molécula explica el comportamiento.

Regla mental:
Estructura → interacción → propiedad.
```

---

# 15. Dashboard MVP

## 15.1 Vista principal

Elementos mínimos:

1. Puntaje estimado por área.
2. Preguntas respondidas hoy.
3. Tasa de acierto por área.
4. Top 10 temas prioritarios.
5. Top 10 errores frecuentes.
6. Preguntas para repetir hoy.
7. Plan recomendado.

## 15.2 Vista de temas

Tabla:

```txt
Área | Tema | Preguntas | Recientes | Tus errores | Prioridad
```

## 15.3 Vista de práctica

Flujo:

```txt
Pregunta
Opciones
Responder
Mostrar resultado
Registrar error
Generar explicación
Buscar similares
```

## 15.4 Vista de análisis

Gráficas:

* acierto por área;
* acierto por tema;
* tiempo promedio por área;
* errores por tipo;
* evolución por día.

---

# 16. Implementación en 1 día

## 16.1 Hora 0–1: estructura del proyecto

```txt
icfes-os/
  app.py
  data/
    raw/
    processed/
  db/
    icfes_os.sqlite
  scripts/
    ingest_pdf.py
    classify_questions.py
    build_embeddings.py
    import_questions.py
  src/
    db.py
    models.py
    scoring.py
    tutor.py
    recommender.py
    extraction.py
  prompts/
    classify_question.txt
    explain_error.txt
  exports/
```

## 16.2 Hora 1–3: base de datos + carga manual

Prioridad: permitir importar preguntas desde JSONL.

Formato JSONL:

```json
{"id":"q001","year":2024,"area":"ciencias_naturales","question_number":1,"statement":"...","option_a":"...","option_b":"...","option_c":"...","option_d":"...","correct_answer":"B","explanation":"..."}
```

Antes de extraer PDFs perfecto, debe existir forma de cargar datos manuales o semiautomáticos.

## 16.3 Hora 3–5: extractor PDF simple

Objetivo: extraer texto por página y generar archivos `.txt`.

No intentar resolver todos los formatos. Primero convertir PDFs a texto limpio.

## 16.4 Hora 5–7: clasificador IA

Procesar preguntas ya importadas y llenar tabla `classifications`.

## 16.5 Hora 7–9: práctica básica en Streamlit

Debe permitir:

* elegir área;
* mostrar pregunta;
* responder;
* ver respuesta correcta;
* registrar error;
* guardar intento.

## 16.6 Hora 9–11: scoring de temas

Calcular prioridad por tema.

## 16.7 Hora 11–13: dashboard

Mostrar:

* total respondidas;
* acierto por área;
* temas prioritarios;
* errores frecuentes;
* preguntas pendientes de repaso.

## 16.8 Hora 13–15: búsqueda semántica

Agregar ChromaDB o FAISS.

## 16.9 Hora 15–17: tutor IA

Botón: “Explícame mi error”.

## 16.10 Hora 17–19: recomendador diario

Generar plan según horas disponibles.

## 16.11 Hora 19–21: limpieza y pruebas

Probar con 50–100 preguntas.

## 16.12 Hora 21–24: uso real

Responder preguntas reales, corregir, ajustar taxonomía y validar que el sistema recomiende temas razonables.

---

# 17. Prompt maestro para Claude Code

```txt
Quiero construir en 1 día un sistema local llamado ICFES OS para preparación Saber 11.

Contexto:
Soy programador. Tengo muchos PDFs/cuadernillos de Saber 11, respuestas y explicaciones. Tengo 60 días para estudiar. Mis fortalezas son Lectura Crítica e Inglés. Mis debilidades son Ciencias Naturales, Matemáticas y Sociales/Historia de Colombia.

Objetivo:
Crear un sistema práctico, no perfecto, que me ayude a:
1. Cargar preguntas desde JSONL/CSV.
2. Extraer texto básico desde PDFs.
3. Guardar preguntas en SQLite.
4. Clasificar preguntas con IA por área, subárea, tema, subtema, competencia, dificultad y conceptos clave.
5. Registrar mis intentos, respuestas, tiempos, confianza y tipos de error.
6. Calcular prioridad de estudio por tema usando frecuencia, recencia y tasa de error personal.
7. Mostrar un dashboard en Streamlit.
8. Buscar preguntas similares usando embeddings.
9. Generar explicación personalizada de mis errores.
10. Recomendar un plan diario.

Stack:
- Python
- SQLite
- Streamlit
- Pandas
- PyMuPDF
- ChromaDB o FAISS
- OpenAI/Claude API configurable con variable de entorno

Crea:
- estructura completa de carpetas;
- requirements.txt;
- schema.sql;
- app.py en Streamlit;
- scripts de ingesta;
- módulo de scoring;
- módulo de clasificación;
- módulo de tutor;
- README con instrucciones de ejecución.

Restricciones:
- No construir login.
- No construir multiusuario.
- No construir app móvil.
- No perder tiempo en diseño visual.
- Priorizar funcionalidad en 24 horas.
- El sistema debe funcionar aunque solo cargue preguntas desde JSONL al inicio.
```

---

# 18. Prompt para generar datos desde PDFs

```txt
Tengo el texto extraído de un PDF de preguntas Saber 11.

Necesito que lo conviertas a JSONL.

Cada línea debe tener este esquema:
{
  "id": "",
  "year": null,
  "area": "",
  "question_number": null,
  "statement": "",
  "option_a": "",
  "option_b": "",
  "option_c": "",
  "option_d": "",
  "correct_answer": "",
  "explanation": "",
  "source_file": "",
  "page": null
}

Reglas:
- Devuelve solo JSONL válido.
- Si no sabes la respuesta correcta, deja correct_answer vacío.
- Si no hay explicación, deja explanation vacío.
- No inventes texto.
- Conserva la redacción original lo máximo posible.
- Si una pregunta no se puede reconstruir bien, omítela.
```

---

# 19. Prompt para limpieza y normalización de taxonomía

```txt
Normaliza estos temas de preguntas Saber 11.

Objetivo:
Evitar duplicados como:
- "porcentaje"
- "porcentajes"
- "calculo de porcentajes"
- "proporciones y porcentajes"

Devuelve una taxonomía limpia con:
{
  "canonical_topic": "",
  "aliases": [],
  "area": "",
  "subarea": "",
  "recommended_priority": "low|medium|high|critical"
}

Lista de temas:
{{topics}}
```

---

# 20. Métricas de éxito

ICFES OS es exitoso si, al final del primer día, permite responder afirmativamente:

1. ¿Puedo cargar al menos 100 preguntas?
2. ¿Puedo clasificarlas por tema?
3. ¿Puedo registrar mis respuestas?
4. ¿Puedo ver en qué temas fallo más?
5. ¿Puedo generar un plan diario?
6. ¿Puedo encontrar preguntas similares?
7. ¿Puedo recibir explicación personalizada de mis errores?
8. ¿Estoy estudiando mejor que antes de construirlo?

Si la respuesta es sí, el sistema ya sirve.

---

# 21. Métricas académicas del usuario

## 21.1 Puntajes objetivo

```txt
Meta mínima global: 320
Meta realista fuerte: 350
Meta ambiciosa: 380
```

## 21.2 Distribución esperada por área

```txt
Lectura Crítica: 90+
Inglés: 90+
Sociales y Ciudadanas: 70–80
Matemáticas: 65–75
Ciencias Naturales: 60–75
```

## 21.3 Prioridad de estudio

```txt
Ciencias Naturales: máxima
Matemáticas: máxima
Sociales y Ciudadanas: alta
Inglés: mantenimiento
Lectura Crítica: mantenimiento
```

---

# 22. Estrategia de uso diario

Cada día:

1. Abrir dashboard.
2. Ver top 5 temas prioritarios.
3. Resolver 20–40 preguntas.
4. Corregir todas.
5. Registrar error.
6. Leer explicación IA.
7. Repetir preguntas falladas antiguas.
8. Ajustar plan del día siguiente.

Regla:

> Ninguna pregunta fallada puede quedar sin clasificación de error.

---

# 23. Riesgos

## 23.1 Riesgo: construir demasiado

Mitigación:

```txt
Solo construir funcionalidades que afecten el estudio de mañana.
```

## 23.2 Riesgo: extracción PDF imperfecta

Mitigación:

```txt
Permitir carga manual desde JSONL/CSV.
No bloquear el sistema por extracción automática.
```

## 23.3 Riesgo: clasificaciones incorrectas

Mitigación:

```txt
Guardar confidence.
Permitir edición manual.
Agrupar temas similares semanalmente.
```

## 23.4 Riesgo: usar material no comparable

Mitigación:

```txt
Dar mayor peso a material Saber 11 reciente.
Usar material viejo solo como práctica secundaria.
Excluir Saber Pro, TyT y Universidad Nacional del análisis principal.
```

## 23.5 Riesgo: estudiar lo que ya se domina

Mitigación:

```txt
Limitar tiempo recomendado para áreas con alto desempeño.
```

---

# 24. Consideraciones legales y éticas

ICFES OS debe usarse para preparación personal. El sistema no debe vender, redistribuir ni publicar material protegido sin autorización. Tampoco debe promover el uso de exámenes filtrados reales o material no autorizado de aplicaciones futuras.

El uso correcto del sistema es:

* análisis personal;
* práctica;
* clasificación de preguntas;
* explicación de errores;
* planificación de estudio.

No es objetivo del sistema:

* predecir preguntas exactas;
* obtener ventaja indebida;
* distribuir material protegido;
* comercializar bancos de preguntas ajenos.

---

# 25. Roadmap posterior al MVP

## Día 2–3

* Mejorar extracción de PDFs.
* Agregar edición manual de preguntas.
* Añadir importación desde carpetas.
* Mejorar taxonomía.

## Día 4–7

* Agregar modo simulacro cronometrado.
* Estimar puntaje por área.
* Crear tarjetas de fórmulas y conceptos.
* Exportar plan semanal.

## Semana 2

* Agregar análisis de evolución.
* Ajustar pesos por desempeño real.
* Crear banco de preguntas falladas.
* Generar resúmenes por tema.

---

# 26. Conclusión

ICFES OS no debe ser una plataforma educativa genérica. Debe ser una máquina personal de priorización.

El estudiante no necesita estudiar más cosas; necesita estudiar las cosas correctas, en el orden correcto, con corrección profunda y repetición inteligente.

La ventaja técnica del estudiante permite convertir un paquete desordenado de PDFs en un sistema adaptativo que responde diariamente tres preguntas:

1. ¿Qué debo estudiar hoy?
2. ¿Por qué estoy fallando?
3. ¿Qué me da más puntos si lo aprendo ahora?

Si el sistema responde esas tres preguntas, cumple su función.

La versión 1 debe estar lista en 24 horas, aunque sea fea. La calidad vendrá después. El puntaje se gana estudiando con feedback, no perfeccionando software.

---

# 27. Especificación mínima de entrega

Al terminar el primer día, el repositorio debe permitir ejecutar:

```bash
pip install -r requirements.txt
python scripts/init_db.py
python scripts/import_questions.py data/processed/questions.jsonl
python scripts/classify_questions.py
streamlit run app.py
```

Y debe mostrar:

```txt
Dashboard
Práctica
Temas prioritarios
Errores frecuentes
Preguntas similares
Explicación de errores
Plan diario
```

Este es el producto mínimo viable de ICFES OS.
