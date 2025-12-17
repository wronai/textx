#!/usr/bin/env python3
"""
NLP2CMD Text4 API Service

REST API service for text-to-HTML conversion using NLP2CMD converters.

Nomenclature:
- text2html: GENERATE HTML code from text description
- text3html: EDIT existing HTML file
- text4html: SERVICE - distributed service for gen/edit on all app levels
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

# Import NLP2CMD converters (v2 with correct nomenclature)
from nlp2cmd.converters.web.html_converters_v2 import Text2HTML, Text3HTML, Text4HTML
from nlp2cmd.converters.web.html_converters_v2 import analyze_html, validate_html

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
    """List available converters with correct nomenclature"""
    return {
        "nomenclature": {
            "text2X": "GENERATE - creates new code from text description",
            "text3X": "EDIT - modifies existing file",
            "text4X": "SERVICE - distributed service for gen/edit on all app levels"
        },
        "converters": [
            {
                "name": "text2html",
                "type": "generator",
                "description": "GENERATE HTML code from text description",
                "templates": ["page", "landing", "form", "table", "card"]
            },
            {
                "name": "text3html",
                "type": "editor",
                "description": "EDIT existing HTML file (add/remove/modify elements)",
                "actions": ["add", "remove", "modify", "style"]
            },
            {
                "name": "text4html",
                "type": "service",
                "description": "SERVICE - distributed gen/edit for all app levels (firmware→frontend)"
            }
        ]
    }

@app.post("/api/v1/convert/text2html", response_model=ConvertResponse)
async def convert_text2html(request: ConvertRequest):
    """
    GENERATE HTML code from text description.
    
    Examples:
    - "generate landing page title: My Product"
    - "generate form for contact"
    - "generate table"
    - "generate card"
    """
    try:
        result = text2html.execute(request.command)
        
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
    EDIT existing HTML file.
    
    Examples:
    - "add button to form"
    - "change title to 'New Title'"
    - "remove footer section"
    - "add class 'active' to nav"
    
    Requires html_content in request body.
    """
    try:
        if not request.html_content:
            return ConvertResponse(
                success=False,
                converter="text3html",
                command=request.command,
                error="html_content is required for text3html (edit). Use text2html to generate HTML first.",
                timestamp=datetime.now().isoformat()
            )
        
        result = text3html.execute(request.command, request.html_content)
        
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
    
    Example pipeline (correct nomenclature):
    [
        {"converter": "text2html", "command": "generate landing page"},  # GENERATE
        {"converter": "text3html", "command": "add footer"}              # EDIT
    ]
    """
    results = []
    current_output = None
    
    for i, step in enumerate(request.steps):
        try:
            if step.converter == "text2html":
                # GENERATE - creates new HTML
                result = text2html.execute(step.command)
            elif step.converter == "text3html":
                # EDIT - modifies existing HTML (needs current_output)
                result = text3html.execute(step.command, current_output)
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
                # GENERATE HTML (text2html)
                command = data.get("command", "generate page")
                result = text2html.execute(command)
                
                await websocket.send_json({
                    "event": "generated",
                    "success": result.success,
                    "output": result.output,
                    "metadata": result.metadata,
                    "timestamp": datetime.now().isoformat()
                })
                
            elif action == "edit":
                # EDIT HTML (text3html)
                command = data.get("command", "add element")
                html_content = data.get("html_content")
                result = text3html.execute(command, html_content)
                
                await websocket.send_json({
                    "event": "edited",
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
# text4style - LLM-based styling service
# ============================================================================

class StyleRequest(BaseModel):
    """Request for text4style"""
    command: str
    element_info: Optional[Dict[str, Any]] = None

@app.post("/api/v1/style")
async def text4style(request: StyleRequest):
    """
    text4style - LLM-based CSS generation from natural language.
    
    Interprets complex styling commands and returns CSS properties.
    
    Examples:
    - "make it bold, red, blinking, transparent 20%"
    - "gradient background from blue to purple, rounded corners, shadow"
    - "professional dark theme with hover effects"
    """
    command = request.command.lower()
    
    # LLM-simulated style interpretation (w produkcji: prawdziwy LLM)
    styles = {}
    animations = []
    
    # Color interpretation
    color_map = {
        'red': '#ef4444', 'blue': '#3b82f6', 'green': '#22c55e',
        'yellow': '#eab308', 'orange': '#f97316', 'purple': '#a855f7',
        'pink': '#ec4899', 'black': '#000000', 'white': '#ffffff',
        'gray': '#6b7280', 'cyan': '#06b6d4', 'indigo': '#6366f1'
    }
    
    for color, hex_val in color_map.items():
        if color in command:
            if 'background' in command or 'bg' in command or 'tło' in command:
                styles['backgroundColor'] = hex_val
                # Auto contrast text
                if color in ['blue', 'purple', 'black', 'indigo', 'green', 'red']:
                    styles['color'] = '#ffffff'
            else:
                styles['color'] = hex_val
    
    # Gradient detection
    if 'gradient' in command:
        colors_found = [c for c in color_map.keys() if c in command]
        if len(colors_found) >= 2:
            styles['background'] = f'linear-gradient(135deg, {color_map[colors_found[0]]}, {color_map[colors_found[1]]})'
            styles['color'] = '#ffffff'
        else:
            styles['background'] = 'linear-gradient(135deg, #667eea, #764ba2)'
            styles['color'] = '#ffffff'
    
    # Text styles
    if 'bold' in command or 'pogrub' in command:
        styles['fontWeight'] = 'bold'
    if 'italic' in command or 'kursyw' in command:
        styles['fontStyle'] = 'italic'
    if 'underline' in command or 'podkreśl' in command:
        styles['textDecoration'] = 'underline'
    if 'center' in command or 'środek' in command:
        styles['textAlign'] = 'center'
    
    # Size
    import re
    size_match = re.search(r'(\d+)\s*(%|px|em|rem)', command)
    if size_match:
        styles['fontSize'] = f'{size_match.group(1)}{size_match.group(2)}'
    if 'big' in command or 'duż' in command:
        styles['fontSize'] = '1.5em'
    if 'small' in command or 'mał' in command:
        styles['fontSize'] = '0.8em'
    
    # Transparency
    opacity_match = re.search(r'(?:transparent|opacity|przezroczyst)[:\s]*(\d+)', command)
    if opacity_match:
        val = int(opacity_match.group(1))
        styles['opacity'] = str(val / 100 if val > 1 else val)
    
    # Border radius
    if 'round' in command or 'zaokrągl' in command:
        radius_match = re.search(r'(?:round|radius)[:\s]*(\d+)', command)
        styles['borderRadius'] = f'{radius_match.group(1)}px' if radius_match else '8px'
    
    # Shadow
    if 'shadow' in command or 'cień' in command:
        styles['boxShadow'] = '0 4px 12px rgba(0,0,0,0.15)'
    
    # Animations
    if 'blink' in command or 'migaj' in command:
        animations.append({
            'name': 'blink',
            'keyframes': '@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }',
            'value': 'blink 1s infinite'
        })
    if 'pulse' in command or 'pulsuj' in command:
        animations.append({
            'name': 'pulse', 
            'keyframes': '@keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }',
            'value': 'pulse 1s infinite'
        })
    if 'shake' in command or 'trzęs' in command:
        animations.append({
            'name': 'shake',
            'keyframes': '@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }',
            'value': 'shake 0.5s infinite'
        })
    if 'spin' in command or 'obraca' in command:
        animations.append({
            'name': 'spin',
            'keyframes': '@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }',
            'value': 'spin 2s linear infinite'
        })
    
    # Combine animations
    if animations:
        styles['animation'] = ', '.join([a['value'] for a in animations])
    
    # Hover effects (returned as separate)
    hover_styles = {}
    if 'hover' in command:
        hover_styles['transform'] = 'scale(1.02)'
        hover_styles['transition'] = 'all 0.2s ease'
        styles['transition'] = 'all 0.2s ease'
    
    # Dark theme
    if 'dark' in command or 'ciemn' in command:
        styles['backgroundColor'] = '#1f2937'
        styles['color'] = '#f3f4f6'
        styles['borderColor'] = '#374151'
    
    # Professional look
    if 'professional' in command or 'profesjonaln' in command:
        styles['fontFamily'] = 'system-ui, -apple-system, sans-serif'
        styles['padding'] = '1rem'
        styles['borderRadius'] = '8px'
        styles['boxShadow'] = '0 2px 8px rgba(0,0,0,0.1)'
    
    return {
        "success": True,
        "command": request.command,
        "styles": styles,
        "animations": animations,
        "hover": hover_styles,
        "css": '; '.join([f'{k}: {v}' for k, v in styles.items()]),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Demo endpoint - generates sample HTML
# ============================================================================

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Demo page showing service capabilities"""
    result = text2html.execute("generate landing page title: NLP2CMD Text4 API")
    return result.output if result.success else "<html><body><h1>Demo Error</h1></body></html>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
