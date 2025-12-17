"""
NLP2CMD Converters Package v0.4.0

All converters organized by category.
"""

# Shell
from .shell.text2shell import Text2Shell
from .shell.text3bash import Text3Bash

# Containers  
from .containers.text3docker import Text3Docker
from .containers.text2kubernetes import Text2Kubernetes
from .containers.text3kubernetes import Text3Kubernetes

# API
from .api.text3app import Text3App
from .api.text2api import Text2API

# Network
from .network.text2ssh import Text2SSH

# Infrastructure
from .infrastructure.text3terraform import Text3Terraform

# Database
from .database.text3database import Text3Database

# Web
from .web.html_converters import Text2HTML, Text3HTML, Text4HTML
from .web.svg_converters import Text3SVG, Text4SVG

# Documents
from .documents.markdown_converters import Text2Markdown, Text3Markdown, Text4Markdown

# Protocols
from .protocols.industrial_protocols import (
    Text2Modbus, Text3Modbus, Text4Modbus,
    Text2MQTT, Text3MQTT, Text4MQTT
)

# Hardware
from .hardware.hardware_interfaces import (
    Text2USB, Text3USB, Text4USB,
    Text2HDMI, Text4HDMI,
    Text2Serial, Text3Serial, Text4Serial
)

__all__ = [
    # Shell
    'Text2Shell', 'Text3Bash',
    # Containers
    'Text3Docker', 'Text2Kubernetes', 'Text3Kubernetes',
    # API
    'Text3App', 'Text2API',
    # Network
    'Text2SSH',
    # Infrastructure
    'Text3Terraform',
    # Database
    'Text3Database',
    # Web
    'Text2HTML', 'Text3HTML', 'Text4HTML', 'Text3SVG', 'Text4SVG',
    # Documents
    'Text2Markdown', 'Text3Markdown', 'Text4Markdown',
    # Protocols
    'Text2Modbus', 'Text3Modbus', 'Text4Modbus',
    'Text2MQTT', 'Text3MQTT', 'Text4MQTT',
    # Hardware
    'Text2USB', 'Text3USB', 'Text4USB',
    'Text2HDMI', 'Text4HDMI',
    'Text2Serial', 'Text3Serial', 'Text4Serial',
]
