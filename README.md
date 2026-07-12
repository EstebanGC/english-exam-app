# English Exam Evaluator

Microservicio construido con **FastAPI** que recibe respuestas de exámenes de inglés (pregunta, respuesta del estudiante y rúbrica de evaluación) y las califica automáticamente usando un LLM, devolviendo un puntaje, un estado de aprobación y retroalimentación detallada por criterio.

Este servicio **no es una plataforma de exámenes completa**: no administra usuarios, exámenes ni preguntas. Su única responsabilidad es recibir los datos necesarios para evaluar una respuesta, calificarla, y guardar un historial de evaluaciones. Los exámenes, preguntas y usuarios viven en un sistema externo que consume esta API.

## Características

- Evaluación automática de respuestas de examen mediante LLM, basada en una rúbrica configurable enviada en cada petición.
- Cálculo de aprobación (`approved`) determinístico en el backend, no delegado al LLM.
- Retroalimentación desglosada por criterio de evaluación.
- Historial de evaluaciones persistido en PostgreSQL (tipos nativos `JSONB` para rúbrica y desglose de resultados).
- Compatible con cualquier proveedor de LLM que exponga una API compatible con OpenAI: [Groq](https://groq.com), modelos locales servidos con [LM Studio](https://lmstudio.ai), [Ollama](https://ollama.com), OpenAI, etc. El proveedor se configura por variables de entorno, sin tocar código.
- Validación estricta de entradas (longitud mínima/máxima, pesos de rúbrica) para evitar evaluaciones sobre datos vacíos o inválidos.

## Stack técnico

- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **PostgreSQL** — base de datos
- **Pydantic v2** — validación y schemas
- **OpenAI SDK** — cliente compatible con cualquier proveedor tipo OpenAI (Groq, LM Studio, etc.)

## Requisitos previos

- Python 3.11+
- PostgreSQL en ejecución
- Acceso a un proveedor de LLM compatible con la API de OpenAI (API key de Groq, o un modelo corriendo localmente en LM Studio/Ollama)

## Instalación

```bash
git clone <url-del-repositorio>
cd english-evaluator

python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tu_base

# Proveedor del LLM (compatible con API de OpenAI)
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=not-needed
LLM_MODEL_NAME=qwen2.5-7b-instruct
```

Para usar Groq en lugar de un modelo local, cambia:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=tu_groq_api_key
LLM_MODEL_NAME=llama-3.3-70b-versatile
```

## Base de datos

Ejecuta el script `db-script.sql` incluido en el repositorio sobre tu base PostgreSQL para crear la tabla `evaluations`:

```bash
psql -U tu_usuario -d tu_base -f db-script.sql
```

## Ejecución

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`, y la documentación interactiva (Swagger) en `http://127.0.0.1:8000/docs`.

## Uso

### `POST /evaluate`

Recibe una respuesta de examen y devuelve su evaluación.

**Request:**

```json
{
  "external_user_id": "user_123",
  "external_exam_id": "exam_456",
  "external_question_id": "q_789",
  "external_response_id": "resp_001",
  "question_text": "Describe your daily routine using present simple tense.",
  "student_answer": "I wake up at 7 am. I goes to work by bus. After work I cooking dinner.",
  "rubric": {
    "criteria": [
      { "name": "grammar", "weight": 25, "description": "Correct use of present simple" },
      { "name": "vocabulary", "weight": 25, "description": "Range and accuracy of vocabulary" },
      { "name": "coherence", "weight": 25, "description": "Logical flow of ideas" },
      { "name": "task_achievement", "weight": 25, "description": "Covers a full daily routine" }
    ]
  },
  "max_score": 100,
  "passing_score": 60
}
```

**Response (`201 Created`):**

```json
{
  "id": 1,
  "external_user_id": "user_123",
  "external_exam_id": "exam_456",
  "external_question_id": "q_789",
  "external_response_id": "resp_001",
  "score": 73.0,
  "approved": true,
  "feedback": "Your response is clear and covers a good portion of your daily routine...",
  "score_breakdown": [
    {
      "criterion": "grammar",
      "score": 15.0,
      "max": 25.0,
      "comment": "The student made a grammatical error in 'I goes to work by bus'..."
    }
  ],
  "model_used": "qwen2.5-7b-instruct",
  "evaluated_at": "2026-07-11T15:37:29.213841-05:00"
}
```

## Estructura del proyecto

```
app/
├── main.py                          # Punto de entrada de la app
├── models.py                        # Modelos SQLAlchemy
├── schemas.py                       # Schemas Pydantic (request/response)
├── routes/
│   └── evaluation_routes.py         # Endpoint POST /evaluate
├── services/
│   └── llm_evaluator.py             # Lógica de construcción de prompt y llamada al LLM
└── utils/
    ├── config.py                    # Conexión a base de datos
    └── __init__.py
db-script.sql                        # Script de creación de la tabla evaluations
```

## Notas de diseño

- El **puntaje de aprobación** (`approved`) se calcula en el backend comparando `score` contra `passing_score`, no se delega la decisión al LLM. Esto mantiene la regla de negocio determinística y auditable.
- La **rúbrica** viaja en cada petición; este servicio no almacena rúbricas propias, ya que el examen, la pregunta y sus criterios de evaluación son responsabilidad del sistema externo que consume esta API.
- Los campos `external_*_id` son de referencia/trazabilidad únicamente — no son llaves foráneas reales, ya que apuntan a entidades que viven en otro sistema.

## Próximos pasos

- Autenticación del endpoint `/evaluate` (API key propia para clientes de esta API).
- Asociar evaluaciones a una cuenta/cliente de la API.
- Manejo de errores más granular según el tipo de falla del LLM (timeout, modelo no disponible, respuesta mal formada).
