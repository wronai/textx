"""Web converters - HTML, SVG

Nomenclature:
- text2X: GENERATE - creates new code from text description
- text3X: EDIT - modifies existing file
- text4X: SERVICE - distributed service for gen/edit on all app levels
"""
# Use v2 converters with correct nomenclature
from .html_converters_v2 import Text2HTML, Text3HTML, Text4HTML
from .html_converters_v2 import analyze_html, validate_html
from .svg_converters import Text3SVG, Text4SVG

__all__ = [
    'Text2HTML', 'Text3HTML', 'Text4HTML',
    'Text3SVG', 'Text4SVG',
    'analyze_html', 'validate_html'
]
