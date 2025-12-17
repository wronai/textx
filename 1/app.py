#!/usr/bin/env python3
"""
NLP2CMD Text4 API Service

REST API service for text-to-HTML conversion using NLP2CMD converters.
Provides endpoints for:
- text2html: Parse/analyze HTML
- text3html: Generate HTML
- text4html: Stream HTML updates
"""

import sys
sys.path.insert(0, '/app')

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
from datetime import datetime

# Import NLP2CMD converters
from nlp2cmd.converters.web.html_converters import Text2HTML, Text3HTML, Text4HTML

app = FastAPI(
    title="NLP2CMD Text4 API",
    description="Natural Language to HTML Conversion Service",
    version="0.4.0"
)

# CORS - allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize converters
text2html = Text2HTML()
text3html = Text3HTML()

# ============================================================================
# Models
# ============================================================================

class ConvertRequest(BaseModel):
    """Request for conversion"""
    command: str
    context: Optional[Dict[str, Any]] = None
    html_content: Optional[str] = None  # For text2html analysis

class PipelineStep(BaseModel):
    """Single step in pipeline"""
    converter: str
    command: str
    config: Optional[Dict[str, Any]] = None

class PipelineRequest(BaseModel):
    """Pipeline request"""
    name: Optional[str] = "pipeline"
    steps: List[PipelineStep]
    context: Optional[Dict[str, Any]] = None

class ConvertResponse(BaseModel):
    """Response from conversion"""
    success: bool
    converter: str
    command: str
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - service info"""
    return {
        "service": "NLP2CMD Text4 API",
        "version": "0.4.0",
        "converters": ["text2html", "text3html", "text4html"],
        "endpoints": {
            "convert": "POST /api/v1/convert/{converter}",
            "pipeline": "POST /api/v1/pipeline",
            "converters": "GET /api/v1/converters",
            "health": "GET /health",
            "stream": "WS /api/v1/stream"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "converters": {
            "text2html": "ready",
            "text3html": "ready",
            "text4html": "ready"
        }
    }

@app.get("/api/v1/converters")
async def list_converters():
    """List available converters"""
    return {
        "converters": [
            {
                "name": "text2html",
                "type": "parser",
                "description": "Parse and analyze HTML",
                "actions": ["analyze", "extract", "validate", "seo", "links", "images"]
            },
            {
                "name": "text3html",
                "type": "generator",
                "description": "Generate HTML from natural language",
                "templates": ["page", "landing", "form", "table", "card", "component"]
            },
            {
                "name": "text4html",
                "type": "stream",
                "description": "Real-time HTML streaming and live updates"
            }
        ]
    }

@app.post("/api/v1/convert/text2html", response_model=ConvertResponse)
async def convert_text2html(request: ConvertRequest):
    """
    Parse/analyze HTML using text2html converter.
    
    Examples:
    - "analyze html structure"
    - "validate html"
    - "seo analysis"
    - "extract links"
    """
    try:
        result = text2html.execute(request.command, request.html_content)
        
        return ConvertResponse(
            success=result.success,
            converter="text2html",
            command=request.command,
            output=result.output if result.success else None,
            error=result.error if not result.success else None,
            metadata=result.metadata,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/convert/text3html", response_model=ConvertResponse)
async def convert_text3html(request: ConvertRequest):
    """
    Generate HTML using text3html converter.
    
    Examples:
    - "generate landing page title: My Product"
    - "generate form for contact"
    - "generate table"
    - "generate card"
    """
    try:
        result = text3html.execute(request.command)
        
        return ConvertResponse(
            success=result.success,
            converter="text3html",
            command=request.command,
            output=result.output if result.success else None,
            error=result.error if not result.success else None,
            metadata=result.metadata,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/convert/{converter}", response_model=ConvertResponse)
async def convert_generic(converter: str, request: ConvertRequest):
    """Generic converter endpoint"""
    if converter == "text2html":
        return await convert_text2html(request)
    elif converter == "text3html":
        return await convert_text3html(request)
    else:
        raise HTTPException(status_code=404, detail=f"Converter '{converter}' not found")

@app.post("/api/v1/pipeline")
async def execute_pipeline(request: PipelineRequest):
    """
    Execute multi-step pipeline.
    
    Example pipeline:
    [
        {"converter": "text3html", "command": "generate landing page"},
        {"converter": "text2html", "command": "validate"}
    ]
    """
    results = []
    current_output = None
    
    for i, step in enumerate(request.steps):
        try:
            if step.converter == "text2html":
                result = text2html.execute(step.command, current_output)
            elif step.converter == "text3html":
                result = text3html.execute(step.command)
            else:
                results.append({
                    "step": i + 1,
                    "converter": step.converter,
                    "status": "error",
                    "error": f"Unknown converter: {step.converter}"
                })
                continue
            
            current_output = result.output if result.success else current_output
            
            results.append({
                "step": i + 1,
                "converter": step.converter,
                "command": step.command,
                "status": "success" if result.success else "error",
                "output_preview": result.output[:200] + "..." if result.output and len(result.output) > 200 else result.output,
                "error": result.error
            })
            
        except Exception as e:
            results.append({
                "step": i + 1,
                "converter": step.converter,
                "status": "error",
                "error": str(e)
            })
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    
    return {
        "name": request.name,
        "status": "success" if success_count == len(results) else "partial",
        "total_steps": len(results),
        "successful_steps": success_count,
        "steps_results": results,
        "final_output": current_output,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# WebSocket for streaming (text4html)
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/api/v1/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time HTML streaming.
    
    Send commands like:
    {"action": "generate", "command": "generate landing page"}
    {"action": "subscribe", "topic": "html-updates"}
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            action = data.get("action")
            
            if action == "generate":
                # Generate HTML and stream result
                command = data.get("command", "generate page")
                result = text3html.execute(command)
                
                await websocket.send_json({
                    "event": "generated",
                    "success": result.success,
                    "output": result.output,
                    "metadata": result.metadata,
                    "timestamp": datetime.now().isoformat()
                })
                
            elif action == "analyze":
                # Analyze HTML
                command = data.get("command", "analyze")
                html_content = data.get("html_content")
                result = text2html.execute(command, html_content)
                
                await websocket.send_json({
                    "event": "analyzed",
                    "success": result.success,
                    "output": result.output,
                    "metadata": result.metadata,
                    "timestamp": datetime.now().isoformat()
                })
                
            elif action == "ping":
                await websocket.send_json({
                    "event": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                
            else:
                await websocket.send_json({
                    "event": "error",
                    "message": f"Unknown action: {action}",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ============================================================================
# Demo endpoint - generates sample HTML
# ============================================================================

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Demo page showing service capabilities"""
    result = text3html.execute("generate landing page title: NLP2CMD Text4 API")
    return result.output if result.success else "<html><body><h1>Demo Error</h1></body></html>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
