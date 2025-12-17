"""Document converters - Markdown

Nomenclature:
- text2X: GENERATE - creates new document from text description
- text3X: EDIT - modifies existing document
- text4X: SERVICE - distributed service for gen/edit
"""
# Use v2 converters with correct nomenclature
from .markdown_converters_v2 import Text2Markdown, Text3Markdown, Text4Markdown

__all__ = ['Text2Markdown', 'Text3Markdown', 'Text4Markdown']
