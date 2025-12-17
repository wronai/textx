"""
SVG Converters - text3svg, text4svg

Generowanie i animacja grafiki SVG:
- text3svg: Generate SVG graphics (charts, diagrams, icons)
- text4svg: Animated SVG streaming
"""

from typing import Dict, Any, Optional, List, Tuple
from nlp2cmd.core.base import BaseConverter, ConversionResult
from nlp2cmd.core.stream_base import BaseStreamConverter, StreamEvent, StreamConfig, StreamState
from pathlib import Path
from datetime import datetime
import asyncio
import math
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# text3svg - Generate SVG (WRITE)
# ============================================================================

class Text3SVG(BaseConverter):
    """
    Generator grafiki SVG.
    
    Funkcje:
    - Charts (bar, line, pie)
    - Diagrams (flowchart, sequence)
    - Icons
    - Shapes
    - Text graphics
    """
    
    COLORS = [
        "#667eea", "#764ba2", "#f59e0b", "#10b981", "#ef4444",
        "#8b5cf6", "#06b6d4", "#f97316", "#84cc16", "#ec4899"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę SVG"""
        return f"svg_{intent.get('chart_type', 'shape')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję"""
        text = text.lower()
        
        chart_type = "shape"
        if "bar" in text or "słupkowy" in text:
            chart_type = "bar_chart"
        elif "line" in text or "liniowy" in text:
            chart_type = "line_chart"
        elif "pie" in text or "kołowy" in text:
            chart_type = "pie_chart"
        elif "flow" in text or "diagram" in text:
            chart_type = "flowchart"
        elif "icon" in text or "ikona" in text:
            chart_type = "icon"
        elif "logo" in text:
            chart_type = "logo"
        elif "circle" in text or "koło" in text:
            chart_type = "circle"
        elif "rect" in text or "prostokąt" in text:
            chart_type = "rectangle"
        
        return {
            "chart_type": chart_type,
            "description": text
        }
    
    def _svg_header(self, width: int = 400, height: int = 300, viewBox: str = None) -> str:
        """Generuje nagłówek SVG"""
        vb = viewBox or f"0 0 {width} {height}"
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{vb}">
  <defs>
    <style>
      .text {{ font-family: system-ui, sans-serif; }}
      .title {{ font-size: 16px; font-weight: bold; }}
      .label {{ font-size: 12px; fill: #666; }}
    </style>
  </defs>
'''
    
    def _svg_footer(self) -> str:
        """Zamyka SVG"""
        return '</svg>'
    
    def generate_bar_chart(
        self,
        data: List[Dict[str, Any]],
        title: str = "Bar Chart",
        width: int = 500,
        height: int = 300
    ) -> str:
        """Generuje wykres słupkowy"""
        
        svg = self._svg_header(width, height)
        
        # Title
        svg += f'  <text x="{width/2}" y="25" class="text title" text-anchor="middle">{title}</text>\n'
        
        # Chart area
        margin = {"top": 50, "right": 30, "bottom": 40, "left": 60}
        chart_width = width - margin["left"] - margin["right"]
        chart_height = height - margin["top"] - margin["bottom"]
        
        # Find max value
        max_val = max(d.get("value", 0) for d in data)
        
        # Bars
        bar_width = chart_width / len(data) * 0.8
        gap = chart_width / len(data) * 0.2
        
        for i, d in enumerate(data):
            x = margin["left"] + i * (bar_width + gap) + gap/2
            bar_height = (d.get("value", 0) / max_val) * chart_height
            y = margin["top"] + chart_height - bar_height
            color = self.COLORS[i % len(self.COLORS)]
            
            svg += f'  <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="4"/>\n'
            svg += f'  <text x="{x + bar_width/2}" y="{height - 15}" class="text label" text-anchor="middle">{d.get("label", "")}</text>\n'
            svg += f'  <text x="{x + bar_width/2}" y="{y - 5}" class="text label" text-anchor="middle">{d.get("value", 0)}</text>\n'
        
        # Axes
        svg += f'  <line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height - margin["bottom"]}" stroke="#ccc" stroke-width="2"/>\n'
        svg += f'  <line x1="{margin["left"]}" y1="{height - margin["bottom"]}" x2="{width - margin["right"]}" y2="{height - margin["bottom"]}" stroke="#ccc" stroke-width="2"/>\n'
        
        svg += self._svg_footer()
        return svg
    
    def generate_line_chart(
        self,
        data: List[Dict[str, Any]],
        title: str = "Line Chart",
        width: int = 500,
        height: int = 300
    ) -> str:
        """Generuje wykres liniowy"""
        
        svg = self._svg_header(width, height)
        
        # Title
        svg += f'  <text x="{width/2}" y="25" class="text title" text-anchor="middle">{title}</text>\n'
        
        # Chart area
        margin = {"top": 50, "right": 30, "bottom": 40, "left": 60}
        chart_width = width - margin["left"] - margin["right"]
        chart_height = height - margin["top"] - margin["bottom"]
        
        # Find max/min
        values = [d.get("value", 0) for d in data]
        max_val = max(values)
        min_val = min(values)
        range_val = max_val - min_val or 1
        
        # Generate points
        points = []
        for i, d in enumerate(data):
            x = margin["left"] + (i / (len(data) - 1)) * chart_width
            y = margin["top"] + chart_height - ((d.get("value", 0) - min_val) / range_val) * chart_height
            points.append((x, y))
        
        # Draw line
        path = f'M {points[0][0]} {points[0][1]}'
        for x, y in points[1:]:
            path += f' L {x} {y}'
        
        svg += f'  <path d="{path}" fill="none" stroke="{self.COLORS[0]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>\n'
        
        # Draw points
        for i, (x, y) in enumerate(points):
            svg += f'  <circle cx="{x}" cy="{y}" r="5" fill="{self.COLORS[0]}"/>\n'
            svg += f'  <text x="{x}" y="{height - 15}" class="text label" text-anchor="middle">{data[i].get("label", "")}</text>\n'
        
        # Axes
        svg += f'  <line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height - margin["bottom"]}" stroke="#ccc" stroke-width="2"/>\n'
        svg += f'  <line x1="{margin["left"]}" y1="{height - margin["bottom"]}" x2="{width - margin["right"]}" y2="{height - margin["bottom"]}" stroke="#ccc" stroke-width="2"/>\n'
        
        svg += self._svg_footer()
        return svg
    
    def generate_pie_chart(
        self,
        data: List[Dict[str, Any]],
        title: str = "Pie Chart",
        width: int = 400,
        height: int = 400
    ) -> str:
        """Generuje wykres kołowy"""
        
        svg = self._svg_header(width, height)
        
        # Title
        svg += f'  <text x="{width/2}" y="25" class="text title" text-anchor="middle">{title}</text>\n'
        
        # Center and radius
        cx, cy = width / 2, height / 2 + 20
        r = min(width, height) / 2 - 60
        
        # Calculate total
        total = sum(d.get("value", 0) for d in data)
        
        # Draw slices
        start_angle = -90  # Start from top
        
        for i, d in enumerate(data):
            value = d.get("value", 0)
            angle = (value / total) * 360
            
            # Convert to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(start_angle + angle)
            
            # Calculate arc points
            x1 = cx + r * math.cos(start_rad)
            y1 = cy + r * math.sin(start_rad)
            x2 = cx + r * math.cos(end_rad)
            y2 = cy + r * math.sin(end_rad)
            
            # Large arc flag
            large_arc = 1 if angle > 180 else 0
            
            color = self.COLORS[i % len(self.COLORS)]
            
            # Draw slice
            path = f'M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z'
            svg += f'  <path d="{path}" fill="{color}" stroke="white" stroke-width="2"/>\n'
            
            # Label
            label_angle = math.radians(start_angle + angle / 2)
            label_r = r * 0.7
            label_x = cx + label_r * math.cos(label_angle)
            label_y = cy + label_r * math.sin(label_angle)
            
            percentage = (value / total) * 100
            svg += f'  <text x="{label_x}" y="{label_y}" class="text" text-anchor="middle" fill="white" font-weight="bold">{percentage:.1f}%</text>\n'
            
            start_angle += angle
        
        # Legend
        legend_y = height - 30
        legend_x = 20
        for i, d in enumerate(data):
            color = self.COLORS[i % len(self.COLORS)]
            x = legend_x + (i % 3) * 130
            y = legend_y + (i // 3) * 20
            svg += f'  <rect x="{x}" y="{y - 10}" width="12" height="12" fill="{color}" rx="2"/>\n'
            svg += f'  <text x="{x + 18}" y="{y}" class="text label">{d.get("label", "")}</text>\n'
        
        svg += self._svg_footer()
        return svg
    
    def generate_flowchart(
        self,
        nodes: List[Dict[str, str]],
        connections: List[Tuple[int, int]] = None,
        title: str = "Flowchart"
    ) -> str:
        """Generuje flowchart"""
        
        width = 600
        height = 100 + len(nodes) * 80
        
        svg = self._svg_header(width, height)
        
        # Title
        svg += f'  <text x="{width/2}" y="30" class="text title" text-anchor="middle">{title}</text>\n'
        
        # Draw nodes
        node_positions = []
        for i, node in enumerate(nodes):
            x = width / 2
            y = 70 + i * 80
            node_positions.append((x, y))
            
            node_type = node.get("type", "process")
            label = node.get("label", f"Step {i+1}")
            
            if node_type == "start" or node_type == "end":
                # Oval
                svg += f'  <ellipse cx="{x}" cy="{y}" rx="60" ry="25" fill="{self.COLORS[0]}" stroke="{self.COLORS[1]}" stroke-width="2"/>\n'
            elif node_type == "decision":
                # Diamond
                points = f"{x},{y-30} {x+50},{y} {x},{y+30} {x-50},{y}"
                svg += f'  <polygon points="{points}" fill="{self.COLORS[2]}" stroke="{self.COLORS[1]}" stroke-width="2"/>\n'
            else:
                # Rectangle
                svg += f'  <rect x="{x-60}" y="{y-25}" width="120" height="50" fill="{self.COLORS[3]}" stroke="{self.COLORS[1]}" stroke-width="2" rx="8"/>\n'
            
            svg += f'  <text x="{x}" y="{y + 5}" class="text" text-anchor="middle" fill="white">{label}</text>\n'
        
        # Draw connections
        connections = connections or [(i, i+1) for i in range(len(nodes)-1)]
        
        for start_idx, end_idx in connections:
            if start_idx < len(node_positions) and end_idx < len(node_positions):
                x1, y1 = node_positions[start_idx]
                x2, y2 = node_positions[end_idx]
                
                # Arrow
                svg += f'  <line x1="{x1}" y1="{y1 + 30}" x2="{x2}" y2="{y2 - 30}" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>\n'
        
        # Arrowhead marker
        svg = svg.replace('</defs>', '''    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
    </marker>
  </defs>
''')
        
        svg += self._svg_footer()
        return svg
    
    def generate_icon(self, icon_type: str = "check", size: int = 64, color: str = None) -> str:
        """Generuje ikonę SVG"""
        
        color = color or self.COLORS[0]
        
        icons = {
            "check": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="20 6 9 17 4 12"/>
</svg>''',
            "x": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="6" x2="6" y2="18"/>
  <line x1="6" y1="6" x2="18" y2="18"/>
</svg>''',
            "star": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="2">
  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
</svg>''',
            "heart": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="2">
  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
</svg>''',
            "arrow": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="5" y1="12" x2="19" y2="12"/>
  <polyline points="12 5 19 12 12 19"/>
</svg>'''
        }
        
        return icons.get(icon_type, icons["check"])
    
    def execute(self, text: str) -> ConversionResult:
        """Generuje SVG na podstawie opisu"""
        
        try:
            intent = self.parse_intent(text)
            
            if intent["chart_type"] == "bar_chart":
                data = [
                    {"label": "A", "value": 30},
                    {"label": "B", "value": 50},
                    {"label": "C", "value": 40},
                    {"label": "D", "value": 70},
                    {"label": "E", "value": 25}
                ]
                svg = self.generate_bar_chart(data, "Sales Data")
                
            elif intent["chart_type"] == "line_chart":
                data = [
                    {"label": "Jan", "value": 10},
                    {"label": "Feb", "value": 25},
                    {"label": "Mar", "value": 20},
                    {"label": "Apr", "value": 35},
                    {"label": "May", "value": 30},
                    {"label": "Jun", "value": 45}
                ]
                svg = self.generate_line_chart(data, "Monthly Trend")
                
            elif intent["chart_type"] == "pie_chart":
                data = [
                    {"label": "Product A", "value": 35},
                    {"label": "Product B", "value": 25},
                    {"label": "Product C", "value": 20},
                    {"label": "Product D", "value": 20}
                ]
                svg = self.generate_pie_chart(data, "Market Share")
                
            elif intent["chart_type"] == "flowchart":
                nodes = [
                    {"type": "start", "label": "Start"},
                    {"type": "process", "label": "Process"},
                    {"type": "decision", "label": "Decision?"},
                    {"type": "process", "label": "Action"},
                    {"type": "end", "label": "End"}
                ]
                svg = self.generate_flowchart(nodes, title="Process Flow")
                
            elif intent["chart_type"] == "icon":
                icon_type = "check"
                if "star" in text:
                    icon_type = "star"
                elif "heart" in text:
                    icon_type = "heart"
                elif "arrow" in text:
                    icon_type = "arrow"
                elif "x" in text or "close" in text:
                    icon_type = "x"
                svg = self.generate_icon(icon_type)
                
            else:
                # Default: simple shape
                svg = self._svg_header(200, 200)
                svg += f'  <rect x="50" y="50" width="100" height="100" fill="{self.COLORS[0]}" rx="10"/>\n'
                svg += self._svg_footer()
            
            return ConversionResult(
                success=True,
                command=f"Generated {intent['chart_type']} SVG",
                output=svg,
                metadata={
                    "chart_type": intent["chart_type"],
                    "size": len(svg)
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))
    
    def save_svg(self, svg: str, filepath: str) -> bool:
        """Zapisuje SVG do pliku"""
        try:
            Path(filepath).write_text(svg)
            return True
        except Exception as e:
            logger.error(f"Error saving SVG: {e}")
            return False


# ============================================================================
# text4svg - Animated SVG Streaming (STREAM)
# ============================================================================

class Text4SVG(BaseStreamConverter):
    """
    Animated SVG streaming.
    
    Funkcje:
    - Real-time chart updates
    - Animation frames
    - Data visualization streaming
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._generator = Text3SVG()
        self._data_source = None
        self._frame_count = 0
    
    async def connect(self, target: str) -> bool:
        """Połącz z źródłem danych dla animacji"""
        try:
            self.state = StreamState.CONNECTED
            logger.info(f"SVG streaming connected: {target}")
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Wyślij nowe dane do animacji"""
        self._data_source = data
        return True
    
    async def receive(self) -> Optional[StreamEvent]:
        """Generuje kolejną klatkę animacji"""
        
        self._frame_count += 1
        
        # Simulate data changes
        import random
        data = [
            {"label": "A", "value": random.randint(20, 80)},
            {"label": "B", "value": random.randint(20, 80)},
            {"label": "C", "value": random.randint(20, 80)},
            {"label": "D", "value": random.randint(20, 80)}
        ]
        
        svg = self._generator.generate_bar_chart(data, f"Real-time Data (Frame {self._frame_count})")
        
        await asyncio.sleep(1)  # 1 FPS
        
        return StreamEvent(
            timestamp=datetime.now(),
            event_type="svg_frame",
            data={
                "frame": self._frame_count,
                "svg": svg,
                "data": data
            },
            source="text4svg",
            metadata={"fps": 1}
        )
