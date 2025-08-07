import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from typing import Optional, List, Dict, Any

# ==============================================================================
# CLASE LÓGICA DEL MCP
# ==============================================================================
class PromptHouseMCP:
    def __init__(self):
        self.prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        os.makedirs(self.prompts_dir, exist_ok=True)

    def _get_prompt_path(self, name: str, category: str) -> str:
        category_path = os.path.join(self.prompts_dir, category)
        os.makedirs(category_path, exist_ok=True)
        return os.path.join(category_path, f"{name}.md")

    def _list_tools(self) -> dict:
        # Definición de herramientas con outputSchema
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
                            "message": {"type": "string"}
                        },
                        "required": ["message"]
                    }
                },
                {
                    "name": "prompts.list_categories",
                    "title": "List Categories",
                    "description": "Lista las categorías de prompts disponibles",
                    "inputSchema": {"type": "object", "properties": {}, "required": []},
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "categories": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["categories"]
                    }
                },
                {
                    "name": "prompts.list_prompts",
                    "title": "List Prompts",
                    "description": "Lista todos los prompts organizados por categoría (o de una categoría)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"category": {"type": "string"}},
                        "required": []
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "prompts": {
                                "type": "object",
                                "additionalProperties": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "required": ["prompts"]
                    }
                },
                {
                    "name": "prompts.load_prompt",
                    "title": "Load Prompt",
                    "description": "Carga el contenido de un prompt existente",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "category": {"type": "string"}},
                        "required": ["name", "category"]
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {"content": {"type": "string"}},
                        "required": ["content"]
                    }
                },
                {
                    "name": "prompts.delete_prompt",
                    "title": "Delete Prompt",
                    "description": "Elimina un prompt existente de una categoría",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "category": {"type": "string"}},
                        "required": ["name", "category"]
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                        "required": ["message"]
                    }
                },
                {
                    "name": "prompts.help",
                    "title": "Help",
                    "description": "Muestra instrucciones de uso del MCP",
                    "inputSchema": {"type": "object", "properties": {}, "required": []},
                    "outputSchema": {
                        "type": "object",
                        "properties": {"help": {"type": "array", "items": {"type": "string"}}},
                        "required": ["help"]
                    }
                }
            ]
        }

    def save_prompt(self, name: str, category: str, prompt_content: str) -> dict:
        path = self._get_prompt_path(name, category)
        with open(path, "w", encoding="utf-8") as f:
            f.write(prompt_content)
        return {"message": f"Prompt '{name}' saved in '{category}'."}

    def list_categories(self) -> dict:
        cats = [name for name in os.listdir(self.prompts_dir)
                if os.path.isdir(os.path.join(self.prompts_dir, name))]
        return {"categories": cats}

    def list_prompts(self, category: Optional[str] = None) -> dict:
        grouped: Dict[str, List[str]] = {}
        if category:
            cat_path = os.path.join(self.prompts_dir, category)
            grouped[category] = [fn[:-3] for fn in os.listdir(cat_path) if fn.endswith('.md')] if os.path.isdir(cat_path) else []
        else:
            for entry in os.listdir(self.prompts_dir):
                path = os.path.join(self.prompts_dir, entry)
                if os.path.isdir(path):
                    grouped[entry] = [fn[:-3] for fn in os.listdir(path) if fn.endswith('.md')]
        return {"prompts": grouped}

    def load_prompt(self, name: str, category: str) -> dict:
        path = self._get_prompt_path(name, category)
        if not os.path.isfile(path):
            raise ValueError(f"'{name}' not found in '{category}'.")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}

    def delete_prompt(self, name: str, category: str) -> dict:
        path = self._get_prompt_path(name, category)
        if not os.path.isfile(path):
            raise ValueError(f"'{name}' not found in '{category}'.")
        os.remove(path)
        return {"message": f"Prompt '{name}' deleted from '{category}'."}

    def help(self) -> dict:
        texto = [
            "Uso de kanairos-prompts MCP:",
            "1) prompts.list_categories → ver categorías disponibles",
            "2) prompts.list_prompts {\"category\": <cat>} → ver prompts en esa categoría",
            "3) prompts.list_prompts {} → ver prompts de todas las categorías agrupados",
            "4) prompts.save_prompt {\"name\": <n>, \"category\": <c>, \"prompt_content\": <texto>}",
            "5) prompts.load_prompt {\"name\": <n>, \"category\": <c>} → obtener contenido",
            "6) prompts.delete_prompt {\"name\": <n>, \"category\": <c>}"
        ]
        return {"help": texto}

# ==============================================================================
# SERVIDOR FASTAPI CON ENDPOINT JSON-RPC UNIFICADO Y WRAPPING
# ==============================================================================
app = FastAPI()
mcp = PromptHouseMCP()

@app.post("/")
async def mcp_endpoint(request: Request):
    payload = await request.json()
    req_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if req_id is None:
        return Response(status_code=204)

    if method == "initialize":
        tools = mcp._list_tools()["tools"]
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}},
                           "serverInfo": {"name": "kanairos-prompts", "version": "0.1.0"},
                           "tools": tools}}

    if method == "tools/list":
        tools = mcp._list_tools()["tools"]
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}

    if method == "tools/call":
        tool = params.get("tool") or params.get("name")
        if not tool:
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602, "message": "Missing 'tool' parameter"}}
        args = params.get("arguments", {})
        func_name = tool.split('.')[-1]
        if not hasattr(mcp, func_name):
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{tool}' not found."}}
        try:
            raw = getattr(mcp, func_name)(**args)
            text = json.dumps(raw, indent=2, ensure_ascii=False)
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": text}],
                    "structuredContent": raw,
                    "isError": False
                }
            }
        except ValueError as e:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": str(e)}], "isError": True}
            }
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32000, "message": f"Internal server error: {str(e)}"}}

    raise HTTPException(status_code=404, detail=f"Method '{method}' not found")

if __name__ == "__main__":
    import uvicorn
    print("✅ MCP kanairos-prompts iniciado en http://0.0.0.0:8765")
    uvicorn.run(app, host="0.0.0.0", port=8765)
