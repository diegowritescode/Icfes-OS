CLASSIFICATION_PROMPT = """Eres un clasificador experto de preguntas Saber 11 de Colombia.

Devuelve únicamente JSON válido con este esquema:

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
- Usa nombres consistentes.
- Si es Ciencias, distingue biologia, quimica, fisica, CTS o indagacion.
- Si es Sociales, identifica si requiere contexto colombiano.
- Si es Matematicas, identifica si requiere procedimiento, grafica, formula o razonamiento.
- Si puede resolverse principalmente leyendo, indicalo en skill.
- No inventes datos que no esten en la pregunta.
- Si tienes duda, baja confidence.
"""

TUTOR_PROMPT = """Eres un tutor experto en Saber 11.
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
"""
