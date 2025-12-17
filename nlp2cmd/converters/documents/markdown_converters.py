"""
Markdown Converters - text2markdown, text3markdown, text4markdown

Kompletna obsługa Markdown:
- text2markdown: Parse, convert, extract from Markdown
- text3markdown: Generate Markdown documents
- text4markdown: Live preview, real-time rendering
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
# text2markdown - Parse & Convert Markdown (READ)
# ============================================================================

class Text2Markdown(BaseConverter):
    """
    Parser i konwerter Markdown.
    
    Funkcje:
    - Parsowanie struktury
    - Konwersja do HTML
    - Ekstrakcja sekcji
    - Analiza dokumentu
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę"""
        return f"markdown_{intent.get('action', 'analyze')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję"""
        text = text.lower()
        
        action = "analyze"
        if "convert" in text or "konwertuj" in text or "html" in text:
            action = "to_html"
        elif "extract" in text or "wyciągnij" in text:
            action = "extract"
        elif "toc" in text or "spis" in text:
            action = "toc"
        elif "links" in text or "linki" in text:
            action = "links"
        elif "code" in text or "kod" in text:
            action = "code_blocks"
        
        return {
            "action": action,
            "description": text
        }
    
    def analyze_markdown(self, md: str) -> Dict[str, Any]:
        """Analizuje dokument Markdown"""
        
        lines = md.split('\n')
        
        # Count headers
        headers = {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}
        for line in lines:
            if line.startswith('######'):
                headers["h6"] += 1
            elif line.startswith('#####'):
                headers["h5"] += 1
            elif line.startswith('####'):
                headers["h4"] += 1
            elif line.startswith('###'):
                headers["h3"] += 1
            elif line.startswith('##'):
                headers["h2"] += 1
            elif line.startswith('#'):
                headers["h1"] += 1
        
        # Count code blocks
        code_blocks = len(re.findall(r'```', md)) // 2
        
        # Count links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', md)
        
        # Count images
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', md)
        
        # Count lists
        bullet_lists = len(re.findall(r'^\s*[-*+]\s', md, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\s*\d+\.\s', md, re.MULTILINE))
        
        # Word count
        text_only = re.sub(r'[#*`\[\]()!]', '', md)
        words = len(text_only.split())
        
        return {
            "headers": headers,
            "total_headers": sum(headers.values()),
            "code_blocks": code_blocks,
            "links": len(links),
            "images": len(images),
            "bullet_lists": bullet_lists,
            "numbered_lists": numbered_lists,
            "lines": len(lines),
            "words": words,
            "characters": len(md)
        }
    
    def to_html(self, md: str) -> str:
        """Konwertuje Markdown do HTML"""
        
        html = md
        
        # Headers
        html = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
        html = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Code
        html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code class="\1">\2</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Images
        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', html)
        
        # Horizontal rule
        html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)
        
        # Lists (simplified)
        html = re.sub(r'^\* (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Paragraphs
        paragraphs = html.split('\n\n')
        html = '\n'.join([
            f'<p>{p}</p>' if not p.startswith('<') else p
            for p in paragraphs if p.strip()
        ])
        
        return html
    
    def extract_toc(self, md: str) -> List[Dict[str, Any]]:
        """Ekstraktuje spis treści"""
        
        toc = []
        
        for line in md.split('\n'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                text = match.group(2)
                slug = re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')
                
                toc.append({
                    "level": level,
                    "text": text,
                    "slug": slug
                })
        
        return toc
    
    def extract_code_blocks(self, md: str) -> List[Dict[str, str]]:
        """Ekstraktuje bloki kodu"""
        
        blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        
        for match in re.finditer(pattern, md, re.DOTALL):
            blocks.append({
                "language": match.group(1) or "text",
                "code": match.group(2).strip()
            })
        
        return blocks
    
    def extract_links(self, md: str) -> List[Dict[str, str]]:
        """Ekstraktuje linki"""
        
        links = []
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(pattern, md):
            links.append({
                "text": match.group(1),
                "url": match.group(2)
            })
        
        return links
    
    def execute(self, text: str, md_content: str = None) -> ConversionResult:
        """Wykonuje operację na Markdown"""
        
        try:
            intent = self.parse_intent(text)
            
            if not md_content:
                return ConversionResult(
                    success=False,
                    error="No Markdown content provided"
                )
            
            if intent["action"] == "analyze":
                result = self.analyze_markdown(md_content)
                output = str(result)
            elif intent["action"] == "to_html":
                result = self.to_html(md_content)
                output = result
            elif intent["action"] == "toc":
                result = self.extract_toc(md_content)
                output = str(result)
            elif intent["action"] == "code_blocks":
                result = self.extract_code_blocks(md_content)
                output = str(result)
            elif intent["action"] == "links":
                result = self.extract_links(md_content)
                output = str(result)
            else:
                result = self.analyze_markdown(md_content)
                output = str(result)
            
            return ConversionResult(
                success=True,
                command=f"Markdown {intent['action']}",
                output=output,
                metadata={
                    "action": intent["action"],
                    "result": result
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3markdown - Generate Markdown (WRITE)
# ============================================================================

class Text3Markdown(BaseConverter):
    """
    Generator dokumentów Markdown.
    
    Funkcje:
    - README generation
    - API documentation
    - Release notes
    - Technical docs
    """
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę"""
        return f"generate_{intent.get('doc_type', 'readme')}"
    
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

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the {license} License - see the [LICENSE](LICENSE) file for details.

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

## Rate Limiting

{rate_limit}

---

Last updated: {date}
''',

        "release_notes": '''# Release Notes - {version}

**Release Date:** {date}

## 🎉 Highlights

{highlights}

## ✨ New Features

{features}

## 🐛 Bug Fixes

{bugfixes}

## 💥 Breaking Changes

{breaking}

## 📦 Dependencies

{dependencies}

## 📈 Upgrade Guide

{upgrade}

---

Full changelog: [{prev_version}...{version}]({changelog_url})
''',

        "tech_doc": '''# {title}

## Overview

{overview}

## Architecture

{architecture}

## Components

{components}

## Configuration

```{config_lang}
{config_example}
```

## Deployment

{deployment}

## Monitoring

{monitoring}

## Troubleshooting

{troubleshooting}

## References

{references}
''',

        "changelog": '''# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{entries}
'''
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję"""
        text = text.lower()
        
        doc_type = "readme"
        if "api" in text:
            doc_type = "api_doc"
        elif "release" in text or "notes" in text or "changelog" in text:
            doc_type = "release_notes"
        elif "tech" in text or "technical" in text or "architecture" in text:
            doc_type = "tech_doc"
        
        # Extract title
        title_match = re.search(r'(?:for|dla|about|o)\s+["\']?([^"\']+)["\']?', text)
        title = title_match.group(1).strip() if title_match else "Project"
        
        return {
            "doc_type": doc_type,
            "title": title,
            "description": text
        }
    
    def generate_readme(
        self,
        title: str,
        description: str = "",
        features: List[str] = None,
        language: str = "python"
    ) -> str:
        """Generuje README.md"""
        
        features = features or [
            "Feature 1 - Description",
            "Feature 2 - Description",
            "Feature 3 - Description"
        ]
        
        features_md = "\n".join([f"- {f}" for f in features])
        
        usage_examples = {
            "python": "from project import main\n\nmain()",
            "javascript": "const project = require('project');\n\nproject.init();",
            "bash": "./project.sh --help"
        }
        
        return self.TEMPLATES["readme"].format(
            title=title,
            description=description or f"A great project called {title}",
            installation=f"pip install {title.lower().replace(' ', '-')}",
            language=language,
            usage_example=usage_examples.get(language, usage_examples["python"]),
            features=features_md,
            license="MIT",
            author="Your Name"
        )
    
    def generate_api_doc(
        self,
        title: str,
        base_url: str = "https://api.example.com/v1",
        endpoints: List[Dict] = None
    ) -> str:
        """Generuje dokumentację API"""
        
        endpoints = endpoints or [
            {"method": "GET", "path": "/users", "description": "Get all users"},
            {"method": "POST", "path": "/users", "description": "Create user"},
            {"method": "GET", "path": "/users/{id}", "description": "Get user by ID"},
        ]
        
        endpoints_md = ""
        for ep in endpoints:
            endpoints_md += f'''### {ep["method"]} {ep["path"]}

{ep["description"]}

**Request:**
```bash
curl -X {ep["method"]} "{base_url}{ep["path"]}"
```

**Response:**
```json
{{
  "success": true,
  "data": {{}}
}}
```

---

'''
        
        return self.TEMPLATES["api_doc"].format(
            title=title,
            description=f"API documentation for {title}",
            base_url=base_url,
            auth_description="Use Bearer token in Authorization header",
            endpoints=endpoints_md,
            rate_limit="100 requests per minute",
            date=datetime.now().strftime("%Y-%m-%d")
        )
    
    def generate_release_notes(
        self,
        version: str,
        features: List[str] = None,
        bugfixes: List[str] = None,
        breaking: List[str] = None
    ) -> str:
        """Generuje release notes"""
        
        features = features or ["New feature 1", "New feature 2"]
        bugfixes = bugfixes or ["Fixed issue #1", "Fixed issue #2"]
        breaking = breaking or ["No breaking changes"]
        
        return self.TEMPLATES["release_notes"].format(
            version=version,
            date=datetime.now().strftime("%Y-%m-%d"),
            highlights=f"Version {version} brings exciting new features!",
            features="\n".join([f"- {f}" for f in features]),
            bugfixes="\n".join([f"- {b}" for b in bugfixes]),
            breaking="\n".join([f"- {b}" for b in breaking]),
            dependencies="No dependency changes",
            upgrade=f"Run `pip install --upgrade project=={version}`",
            prev_version="0.0.0",
            changelog_url="https://github.com/project/releases"
        )
    
    def generate_tech_doc(
        self,
        title: str,
        overview: str = "",
        components: List[Dict] = None
    ) -> str:
        """Generuje dokumentację techniczną"""
        
        components = components or [
            {"name": "Component A", "description": "Main component"},
            {"name": "Component B", "description": "Supporting component"}
        ]
        
        components_md = ""
        for comp in components:
            components_md += f'''### {comp["name"]}

{comp["description"]}

'''
        
        return self.TEMPLATES["tech_doc"].format(
            title=title,
            overview=overview or f"Technical documentation for {title}",
            architecture="```\n[Client] -> [API] -> [Database]\n```",
            components=components_md,
            config_lang="yaml",
            config_example="app:\n  name: project\n  port: 8080",
            deployment="Deploy using Docker or Kubernetes",
            monitoring="Use Prometheus and Grafana for monitoring",
            troubleshooting="Check logs in /var/log/app/",
            references="- [Official Docs](https://docs.example.com)"
        )
    
    def execute(self, text: str) -> ConversionResult:
        """Generuje dokument Markdown"""
        
        try:
            intent = self.parse_intent(text)
            
            if intent["doc_type"] == "api_doc":
                md = self.generate_api_doc(intent["title"])
            elif intent["doc_type"] == "release_notes":
                md = self.generate_release_notes("1.0.0")
            elif intent["doc_type"] == "tech_doc":
                md = self.generate_tech_doc(intent["title"])
            else:
                md = self.generate_readme(intent["title"])
            
            return ConversionResult(
                success=True,
                command=f"Generated {intent['doc_type']}",
                output=md,
                metadata={
                    "doc_type": intent["doc_type"],
                    "title": intent["title"],
                    "lines": len(md.split('\n'))
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))
    
    def save_markdown(self, md: str, filepath: str) -> bool:
        """Zapisuje Markdown do pliku"""
        try:
            Path(filepath).write_text(md)
            return True
        except Exception as e:
            logger.error(f"Error saving Markdown: {e}")
            return False


# ============================================================================
# text4markdown - Live Markdown Preview (STREAM)
# ============================================================================

class Text4Markdown(BaseStreamConverter):
    """
    Real-time Markdown streaming.
    
    Funkcje:
    - Live preview
    - Auto-refresh
    - Hot reload
    - Multi-file watching
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._watch_paths: List[Path] = []
        self._last_modified: Dict[str, float] = {}
        self._converter = Text2Markdown()
    
    async def connect(self, target: str) -> bool:
        """Połącz z katalogiem/plikiem do monitorowania"""
        try:
            path = Path(target)
            
            if path.is_dir():
                self._watch_paths = list(path.glob("**/*.md"))
            elif path.is_file():
                self._watch_paths = [path]
            else:
                self._watch_paths = list(Path(".").glob(target))
            
            for p in self._watch_paths:
                if p.exists():
                    self._last_modified[str(p)] = p.stat().st_mtime
            
            self.state = StreamState.CONNECTED
            logger.info(f"Watching {len(self._watch_paths)} Markdown files")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self._watch_paths = []
        self._last_modified = {}
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Nie używane"""
        return True
    
    async def receive(self) -> Optional[StreamEvent]:
        """Sprawdza zmiany w plikach"""
        
        for path in self._watch_paths:
            if not path.exists():
                continue
            
            current_mtime = path.stat().st_mtime
            last_mtime = self._last_modified.get(str(path), 0)
            
            if current_mtime > last_mtime:
                self._last_modified[str(path)] = current_mtime
                
                content = path.read_text()
                html = self._converter.to_html(content)
                analysis = self._converter.analyze_markdown(content)
                
                return StreamEvent(
                    timestamp=datetime.now(),
                    event_type="markdown_changed",
                    data={
                        "path": str(path),
                        "markdown": content,
                        "html": html,
                        "analysis": analysis
                    },
                    source="text4markdown",
                    metadata={"mtime": current_mtime}
                )
        
        await asyncio.sleep(0.5)
        return None
