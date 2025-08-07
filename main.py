import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from typing import Optional, List, Dict


class PromptHouseMCP:
    """
    Lógica de negocio para la interfaz MCP de KanAIrOS Prompts.

    Almacena prompts en subdirectorios por categoría y ofrece operaciones
    CRUD (crear, leer, actualizar, eliminar) a través de herramientas MCP.
    Cada método devuelve un diccionario con la clave `success` para indicar
    éxito o fallo y los datos correspondientes.
    """

    def __init__(self) -> None:
        # Directorio donde se guardan todas las categorías y prompts.
        self.prompts_dir: str = os.path.join(os.path.dirname(__file__), "prompts")
        os.makedirs(self.prompts_dir, exist_ok=True)

    def _get_prompt_path(self, name: str, category: str) -> str:
        """Devuelve la ruta completa al archivo de un prompt determinado."""
        category_path = os.path.join(self.prompts_dir, category)
        os.makedirs(category_path, exist_ok=True)
        return os.path.join(category_path, f"{name}.md")

    def _list_tools(self) -> Dict[str, List[Dict]]:
        """Devuelve la lista de herramientas disponibles con sus esquemas."""
        return {
            "tools": [
                {
                    "name": "prompts.save_prompt",
                    "title": "Save Prompt",
                    "description": "Guarda un prompt bajo una categoría especificada",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "prompt_content": {"type": "string"}
                        },
                        "required": ["name", "category", "prompt_content"]
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "success": {"type": "boolean"}
                        },
                        "required": ["message", "success"]
                    }
                },
                {
                    "name": "prompts.list_prompts",
                    "title": "List Prompts",
                    "description": "Lista los prompts por categoría",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"}
                        },
                        "required": []
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "prompts": {
                                "type": "object",
                                "additionalProperties": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "success": {"type": "boolean"}
                        },
                        "required": ["prompts", "success"]
                    }
                },
                {
                    "name": "prompts.list_categories",
                    "title": "List Categories",
                    "description": "Lista las categorías de prompts disponibles",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "categories": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "success": {"type": "boolean"}
                        },
                        "required": ["categories", "success"]
                    }
                },
                {
                    "name": "prompts.load_prompt",
                    "title": "Load Prompt",
                    "description": "Carga el contenido de un prompt existente",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"}
                        },
                        "required": ["name", "category"]
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "success": {"type": "boolean"}
                        },
                        "required": ["content", "success"]
                    }
                },
                {
                    "name": "prompts.delete_prompt",
                    "title": "Delete Prompt",
                    "description": "Elimina un prompt existente de una categoría",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"}
                        },
                        "required": ["name", "category"]
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "success": {"type": "boolean"}
                        },
                        "required": ["message", "success"]
                    }
                },
                {
                    "name": "prompts.help",
                    "title": "Help",
                    "description": "Muestra ayuda de uso de KanAIrOS Prompts MCP",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "help": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "success": {"type": "boolean"}
                        },
                        "required": ["help", "success"]
                    }
                }
            ]
        }

    # Métodos de las herramientas
    def save_prompt(self, name: str, category: str, prompt_content: str) -> Dict[str, object]:
        """Guarda el prompt en la categoría indicada."""
        path = self._get_prompt_path(name, category)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(prompt_content)
            return {"success": True, "message": f"Prompt '{name}' saved in '{category}'."}
        except Exception as e:
            raise ValueError(str(e))

    def list_prompts(self, category: Optional[str] = None) -> Dict[str, object]:
        """Lista los prompts existentes agrupados por categoría."""
        prompts: Dict[str, List[str]] = {}
        if category:
            path = os.path.join(self.prompts_dir, category)
            if os.path.isdir(path):
                prompts[category] = [fn[:-3] for fn in os.listdir(path) if fn.endswith(".md")]
            else:
                prompts[category] = []
        else:
            for cat in os.listdir(self.prompts_dir):
                path = os.path.join(self.prompts_dir, cat)
                if os.path.isdir(path):
                    prompts[cat] = [fn[:-3] for fn in os.listdir(path) if fn.endswith(".md")]
        return {"success": True, "prompts": prompts}

    def list_categories(self) -> Dict[str, object]:
        """Devuelve una lista de categorías disponibles."""
        categories = [name for name in os.listdir(self.prompts_dir)
                      if os.path.isdir(os.path.join(self.prompts_dir, name))]
        return {"success": True, "categories": categories}

    def load_prompt(self, name: str, category: str) -> Dict[str, object]:
        """Carga el contenido de un prompt."""
        path = self._get_prompt_path(name, category)
        if not os.path.isfile(path):
            raise ValueError(f"'{name}' not found in '{category}'.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            raise ValueError(str(e))

        return {"success": True, "content": content}

    def delete_prompt(self, name: str, category: str) -> Dict[str, object]:
        """Elimina un prompt."""
        path = self._get_prompt_path(name, category)
        if not os.path.isfile(path):
            raise ValueError(f"'{name}' not found in '{category}'.")
        try:
            os.remove(path)
            return {"success": True, "message": f"Prompt '{name}' deleted from '{category}'."}
        except Exception as e:
            raise ValueError(str(e))

    def help(self) -> Dict[str, object]:
        """Devuelve un texto con la ayuda de uso."""
        text = [
            "Uso de kanairos-prompts MCP:",
            "1) prompts.list_categories → ver categorías disponibles",
            "2) prompts.list_prompts {\"category\": <cat>} → ver prompts en esa categoría",
            "3) prompts.list_prompts {} → ver prompts de todas las categorías agrupados",
            "4) prompts.save_prompt {\"name\": <n>, \"category\": <c>, \"prompt_content\": <texto>}",
            "5) prompts.load_prompt {\"name\": <n>, \"category\": <c>} → obtener contenido",
            "6) prompts.delete_prompt {\"name\": <n>, \"category\": <c>}"
        ]
        return {"success": True, "help": text}


# Instancia de FastAPI y MCP
app = FastAPI()
mcp = PromptHouseMCP()


@app.post("/")
async def mcp_endpoint(request: Request):
    """Endpoint único que implementa JSON-RPC para el MCP."""
    payload = await request.json()
    req_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    # Notificaciones (no llevan id) → 204 No Content
    if req_id is None:
        return Response(status_code=204)

    # initialize
    if method == "initialize":
        tools = mcp._list_tools()["tools"]
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "kanairos-prompts", "version": "0.1.0"},
                "tools": tools
            }
        }

    # tools/list
    if method == "tools/list":
        tools = mcp._list_tools()["tools"]
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": tools}
        }

    # tools/call
    if method == "tools/call":
        # El campo puede llamarse "tool" o "name" según el cliente
        tool_name = params.get("tool") or params.get("name")
        args = params.get("arguments", {})
        if not tool_name:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": "Missing 'tool' parameter"}
            }
        func_name = tool_name.split(".")[-1]
        if not hasattr(mcp, func_name):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found."}
            }

        try:
            raw = getattr(mcp, func_name)(**args)  # Ejecuta la herramienta
            # Formateamos un texto legible para mostrar en 'content'.
            text = json.dumps(raw, indent=2, ensure_ascii=False)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": text}],
                    "structuredContent": raw,
                    "isError": False
                }
            }
        except ValueError as e:
            # Error controlado de la herramienta
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": str(e)}],
                    "isError": True
                }
            }
        except Exception as e:
            # Error interno → se informa en el objeto `error` de JSON-RPC
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": f"Internal server error: {str(e)}"
                }
            }

    # Método desconocido
    raise HTTPException(status_code=404, detail=f"Method '{method}' not found")


if __name__ == "__main__":
    import uvicorn
    print("✅ MCP kanairos-prompts iniciado en http://0.0.0.0:8765")
    uvicorn.run(app, host="0.0.0.0", port=8765)