"""
Markdown Converters v2 - Corrected Nomenclature

Prawidłowa nomenklatura:
- text2markdown: GENERATE Markdown from text description
- text3markdown: EDIT existing Markdown file
- text4markdown: SERVICE - distributed service for generate/edit Markdown
"""

from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
from nlp2cmd.core.stream_base import BaseStreamConverter, StreamEvent, StreamConfig, StreamState
from pathlib import Path
from datetime import datetime
import asyncio
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# text2markdown - GENERATE Markdown from text description
# ============================================================================

class Text2Markdown(BaseConverter):
    """
    Generator Markdown - tworzy dokumenty Markdown z opisu.
    
    Funkcje:
    - Generowanie README.md
    - Tworzenie dokumentacji API
    - Release notes
    - Technical documentation
    """
    
    TEMPLATES = {
        "readme": '''# {title}

{description}

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

```bash
{installation}
```

## 📖 Usage

```{language}
{usage_example}
```

## ✨ Features

{features}

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

## 📄 License

This project is licensed under the {license} License.

---

Made with ❤️ by {author}
''',

        "api_doc": '''# {title} API Documentation

## Overview

{description}

## Base URL

```
{base_url}
```

## Authentication

{auth_description}

## Endpoints

{endpoints}

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Internal Server Error |

---

Last updated: {date}
''',

        "changelog": '''# Changelog

All notable changes to this project will be documented in this file.

## [{version}] - {date}

### Added
{added}

### Changed
{changed}

### Fixed
{fixed}

### Removed
{removed}
'''
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        return f"generate_{intent.get('doc_type', 'readme')}_markdown"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        doc_type = "readme"
        if "api" in text_lower:
            doc_type = "api_doc"
        elif "changelog" in text_lower or "release" in text_lower:
            doc_type = "changelog"
        
        title_match = re.search(r'(?:for|dla|about)\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Project"
        
        return {
            "doc_type": doc_type,
            "title": title,
            "description": text
        }
    
    def generate_readme(self, title: str, description: str = "", features: List[str] = None) -> str:
        features = features or ["Feature 1", "Feature 2", "Feature 3"]
        features_md = "\n".join([f"- {f}" for f in features])
        
        return self.TEMPLATES["readme"].format(
            title=title,
            description=description or f"A great project called {title}",
            installation=f"pip install {title.lower().replace(' ', '-')}",
            language="python",
            usage_example=f"from {title.lower().replace(' ', '_')} import main\n\nmain()",
            features=features_md,
            license="MIT",
            author="Your Name"
        )
    
    def generate_api_doc(self, title: str, endpoints: List[Dict] = None) -> str:
        endpoints = endpoints or [
            {"method": "GET", "path": "/api/v1/items", "description": "Get all items"},
            {"method": "POST", "path": "/api/v1/items", "description": "Create item"},
        ]
        
        endpoints_md = ""
        for ep in endpoints:
            endpoints_md += f"### {ep['method']} `{ep['path']}`\n\n{ep['description']}\n\n"
        
        return self.TEMPLATES["api_doc"].format(
            title=title,
            description=f"API documentation for {title}",
            base_url="https://api.example.com/v1",
            auth_description="Use Bearer token in Authorization header",
            endpoints=endpoints_md,
            date=datetime.now().strftime("%Y-%m-%d")
        )
    
    def execute(self, text: str) -> ConversionResult:
        try:
            intent = self.parse_intent(text)
            
            if intent["doc_type"] == "api_doc":
                md = self.generate_api_doc(intent["title"])
            elif intent["doc_type"] == "changelog":
                md = self.TEMPLATES["changelog"].format(
                    version="1.0.0",
                    date=datetime.now().strftime("%Y-%m-%d"),
                    added="- New feature",
                    changed="- Updated documentation",
                    fixed="- Bug fixes",
                    removed="- Deprecated features"
                )
            else:
                md = self.generate_readme(intent["title"])
            
            return ConversionResult(
                success=True,
                command=f"Generated {intent['doc_type']} Markdown",
                output=md,
                metadata={
                    "doc_type": intent["doc_type"],
                    "title": intent["title"],
                    "lines": len(md.split('\n'))
                }
            )
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3markdown - EDIT existing Markdown file
# ============================================================================

class Text3Markdown(BaseConverter):
    """
    Edytor Markdown - modyfikuje istniejące dokumenty.
    
    Funkcje:
    - Dodawanie sekcji
    - Usuwanie sekcji
    - Modyfikacja nagłówków
    - Aktualizacja linków
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        return f"markdown_edit_{intent.get('action', 'modify')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        action = "modify"
        if any(word in text_lower for word in ["add", "dodaj", "insert"]):
            action = "add"
        elif any(word in text_lower for word in ["remove", "usuń", "delete"]):
            action = "remove"
        elif any(word in text_lower for word in ["change", "zmień", "update"]):
            action = "modify"
        
        return {
            "action": action,
            "description": text
        }
    
    def add_section(self, md: str, title: str, content: str, level: int = 2) -> str:
        header = "#" * level
        section = f"\n\n{header} {title}\n\n{content}\n"
        return md + section
    
    def remove_section(self, md: str, section_title: str) -> str:
        pattern = rf'^(#{1,6})\s+{re.escape(section_title)}.*?(?=^#|\Z)'
        return re.sub(pattern, '', md, flags=re.MULTILINE | re.DOTALL)
    
    def update_section(self, md: str, section_title: str, new_content: str) -> str:
        pattern = rf'(^#{1,6}\s+{re.escape(section_title)}\n+).*?(?=^#|\Z)'
        replacement = rf'\1{new_content}\n\n'
        return re.sub(pattern, replacement, md, flags=re.MULTILINE | re.DOTALL)
    
    def execute(self, text: str, md_content: str = None) -> ConversionResult:
        try:
            if not md_content:
                return ConversionResult(
                    success=False,
                    error="No Markdown content provided for editing"
                )
            
            intent = self.parse_intent(text)
            modified_md = md_content
            
            if intent["action"] == "add":
                # Extract section info from text
                section_match = re.search(r'section\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
                section_title = section_match.group(1) if section_match else "New Section"
                modified_md = self.add_section(md_content, section_title, "Content goes here.")
                
            elif intent["action"] == "remove":
                section_match = re.search(r'(?:section|remove)\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
                if section_match:
                    modified_md = self.remove_section(md_content, section_match.group(1))
            
            return ConversionResult(
                success=True,
                command=f"Markdown {intent['action']}",
                output=modified_md,
                metadata={
                    "action": intent["action"],
                    "changes_made": modified_md != md_content
                }
            )
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text4markdown - SERVICE for distributed Markdown generation/editing
# ============================================================================

class Text4Markdown(BaseStreamConverter):
    """
    Usługa Markdown - rozproszona usługa do generowania i edycji.
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._generator = Text2Markdown()
        self._editor = Text3Markdown()
        self._current_md: str = None
        self._session_id: str = None
    
    async def connect(self, target: str) -> bool:
        try:
            self._session_id = target or f"md_session_{datetime.now().strftime('%H%M%S')}"
            self.state = StreamState.CONNECTED
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        self._session_id = None
        self._current_md = None
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        try:
            if isinstance(data, str):
                data = {"action": "generate", "command": data}
            
            action = data.get("action", "generate")
            command = data.get("command", "")
            
            if action == "generate":
                result = self._generator.execute(command)
                if result.success:
                    self._current_md = result.output
                return result.success
            elif action == "edit":
                md_content = data.get("md_content") or self._current_md
                result = self._editor.execute(command, md_content)
                if result.success:
                    self._current_md = result.output
                return result.success
            
            return False
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    async def receive(self) -> Optional[StreamEvent]:
        if not self._current_md:
            await asyncio.sleep(0.1)
            return None
        
        return StreamEvent(
            timestamp=datetime.now(),
            event_type="markdown_result",
            data={"markdown": self._current_md},
            source=f"text4markdown://{self._session_id}",
            metadata={"session_id": self._session_id}
        )
    
    def generate(self, command: str) -> ConversionResult:
        return self._generator.execute(command)
    
    def edit(self, command: str, md_content: str = None) -> ConversionResult:
        content = md_content or self._current_md
        result = self._editor.execute(command, content)
        if result.success:
            self._current_md = result.output
        return result
