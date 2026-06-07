# Product Spec

## Vision

ICFES OS convierte material Saber 11 en una plataforma personal de inteligencia adaptativa. El objetivo no es almacenar apuntes, sino responder cada dia: que estudiar, por que se falla y que temas dan mayor retorno ahora.

## Usuario

Programador con cerca de 60 dias de preparacion. Fortalezas: Lectura Critica e Ingles. Debilidades: Ciencias Naturales, Matematicas intermedias y Sociales/Ciudadanas. La estrategia prioriza Ciencias, Matematicas y Sociales, manteniendo Lectura e Ingles con baja carga.

## Objetivos

- Estructurar preguntas desde JSONL/CSV/PDF.
- Registrar intentos, confianza, tiempo y tipo de error.
- Calcular prioridades por tema usando frecuencia, recencia, errores, confianza y peso estrategico.
- Recomendar un plan diario ejecutable.
- Funcionar localmente sin API keys.

## Casos de uso Fase 1

- Importar preguntas sample.
- Practicar una pregunta y registrar respuesta.
- Ver precision global, por area y por tema.
- Identificar top temas prioritarios.
- Generar plan diario por minutos disponibles.
- Editar clasificacion manualmente.
- Clasificar con IA si existe API key o fallback si no.

## Restricciones

- Sin pagos, multiusuario, app movil ni login obligatorio.
- Sin material protegido incluido.
- Extraccion PDF basica, no OCR perfecto.
- Sin prediccion de preguntas exactas ni ventajas indebidas.

## Fase 2

La siguiente fase debe profundizar embeddings, tutor IA, cola de revision PDF, simulacros cortos, sesiones de estudio y analitica longitudinal.
