# KanAIrOS Prompts MCP

Este proyecto implementa un **servidor Model Context Protocol (MCP)** usando FastAPI para gestionar prompts organizados por categorías.

## Características principales

* **Guardar prompts** en archivos Markdown dentro de subcarpetas por categoría.
* **Listar prompts** por categoría o todas las categorías a la vez.
* **Listar categorías** de prompts disponibles.
* **Cargar y eliminar prompts** individuales.
* Interfaz JSON-RPC unificada que expone todas las operaciones como herramientas MCP, incluyendo soporte de `outputSchema` y `structuredContent` para compatibilidad con clientes como Gemini CLI.

## Requisitos

* Python 3.9 o superior
* [`fastapi`](https://fastapi.tiangolo.com/) y [`uvicorn`](https://www.uvicorn.org/) instalados (`pip install fastapi uvicorn`)

## Uso

Inicia el servidor con:

```bash
python main.py
```

El servidor escuchará en `http://0.0.0.0:8765` y responderá a peticiones JSON‑RPC según la especificación Model Context Protocol. Puedes interactuar con él mediante un cliente MCP compatible como [Gemini CLI](https://github.com/modelcontextprotocol/docs).

## Estructura

* `main.py`: implementa la clase `PromptHouseMCP` con las funciones de negocio y el endpoint unificado JSON‑RPC.
* `prompts/`: directorio donde se guardan los prompts por categoría. Se crea automáticamente.

## Herramientas disponibles

| Tool                           | Descripción                                         |
| ------------------------------ | ---------------------------------------------------- |
| `prompts.save_prompt`          | Guarda un prompt en la categoría indicada           |
| `prompts.list_prompts`         | Lista los prompts por categoría                      |
| `prompts.list_categories`      | Devuelve la lista de categorías disponibles          |
| `prompts.load_prompt`          | Devuelve el contenido de un prompt                   |
| `prompts.delete_prompt`        | Elimina un prompt de la categoría                    |
| `prompts.help`                 | Devuelve un texto explicando cómo usar el MCP        |

Cada herramienta define su propio `inputSchema` y `outputSchema` según el protocolo MCP.

## Contribución

Este repositorio está en desarrollo. Para contribuir:

1. Haz un fork y crea una rama a partir de `main`.
2. Aplica tus cambios y escribe pruebas si es posible.
3. Abre un *pull request* describiendo tu mejora o corrección.

Consulta `CONTRIBUTING.md` para más detalles.