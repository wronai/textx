"""
HTML Converters - text2html, text3html, text4html

Kompletna obsługa HTML:
- text2html: Parse, analyze, scrape HTML
- text3html: Generate HTML pages, components
- text4html: Live reload, real-time updates
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
# text2html - Parse & Analyze HTML (READ)
# ============================================================================

class Text2HTML(BaseConverter):
    """
    Parser i analizator HTML.
    
    Funkcje:
    - Parsowanie struktury HTML
    - Ekstrakcja danych (scraping)
    - Analiza SEO
    - Walidacja
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę"""
        return f"html_{intent.get('action', 'analyze')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję z tekstu"""
        text = text.lower()
        
        action = "analyze"
        if "extract" in text or "wyciągnij" in text:
            action = "extract"
        elif "validate" in text or "waliduj" in text:
            action = "validate"
        elif "seo" in text:
            action = "seo"
        elif "links" in text or "linki" in text:
            action = "links"
        elif "images" in text or "obrazy" in text:
            action = "images"
        
        return {
            "action": action,
            "description": text
        }
    
    def analyze_html(self, html: str) -> Dict[str, Any]:
        """Analizuje strukturę HTML"""
        
        # Count tags
        tags = re.findall(r'<(\w+)', html)
        tag_counts = {}
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1) if title_match else None
        
        # Extract meta tags
        metas = re.findall(r'<meta\s+([^>]+)>', html, re.IGNORECASE)
        
        # Extract links
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        
        # Extract images
        images = re.findall(r'src=["\']([^"\']+)["\']', html)
        
        return {
            "title": title,
            "tag_counts": tag_counts,
            "total_tags": len(tags),
            "meta_count": len(metas),
            "links": links[:20],  # First 20
            "images": images[:20],
            "size_bytes": len(html.encode('utf-8'))
        }
    
    def extract_data(self, html: str, selector: str = None) -> List[str]:
        """Ekstraktuje dane z HTML"""
        
        # Simple extraction based on tags
        if selector:
            pattern = rf'<{selector}[^>]*>(.*?)</{selector}>'
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            return [m.strip() for m in matches]
        
        # Default: extract text content
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return [text.strip()]
    
    def validate_html(self, html: str) -> Dict[str, Any]:
        """Waliduje HTML"""
        
        errors = []
        warnings = []
        
        # Check doctype
        if not html.strip().lower().startswith('<!doctype'):
            warnings.append("Missing DOCTYPE declaration")
        
        # Check basic structure
        if '<html' not in html.lower():
            errors.append("Missing <html> tag")
        if '<head' not in html.lower():
            warnings.append("Missing <head> tag")
        if '<body' not in html.lower():
            warnings.append("Missing <body> tag")
        
        # Check for unclosed tags (simplified)
        open_tags = re.findall(r'<(\w+)[^>]*(?<!/)>', html)
        close_tags = re.findall(r'</(\w+)>', html)
        
        self_closing = ['br', 'hr', 'img', 'input', 'meta', 'link']
        
        for tag in set(open_tags):
            if tag.lower() not in self_closing:
                open_count = open_tags.count(tag)
                close_count = close_tags.count(tag)
                if open_count != close_count:
                    warnings.append(f"Possibly unclosed <{tag}> tag")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def seo_analysis(self, html: str) -> Dict[str, Any]:
        """Analiza SEO"""
        
        issues = []
        score = 100
        
        # Check title
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if not title_match:
            issues.append("Missing title tag")
            score -= 20
        elif len(title_match.group(1)) > 60:
            issues.append("Title too long (>60 chars)")
            score -= 5
        
        # Check meta description
        desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not desc_match:
            issues.append("Missing meta description")
            score -= 15
        
        # Check h1
        h1_count = len(re.findall(r'<h1', html, re.IGNORECASE))
        if h1_count == 0:
            issues.append("Missing H1 tag")
            score -= 10
        elif h1_count > 1:
            issues.append("Multiple H1 tags")
            score -= 5
        
        # Check images alt
        images = re.findall(r'<img[^>]+>', html, re.IGNORECASE)
        images_without_alt = [img for img in images if 'alt=' not in img.lower()]
        if images_without_alt:
            issues.append(f"{len(images_without_alt)} images without alt attribute")
            score -= min(10, len(images_without_alt) * 2)
        
        return {
            "score": max(0, score),
            "issues": issues,
            "recommendations": self._seo_recommendations(issues)
        }
    
    def _seo_recommendations(self, issues: List[str]) -> List[str]:
        """Generuje rekomendacje SEO"""
        recs = []
        
        if "Missing title" in str(issues):
            recs.append("Add a descriptive <title> tag (50-60 characters)")
        if "Missing meta description" in str(issues):
            recs.append("Add meta description (150-160 characters)")
        if "Missing H1" in str(issues):
            recs.append("Add one H1 tag with main keyword")
        if "alt attribute" in str(issues):
            recs.append("Add descriptive alt attributes to all images")
        
        return recs
    
    def execute(self, text: str, html_content: str = None) -> ConversionResult:
        """
        Wykonuje analizę HTML.
        
        Args:
            text: Komenda w języku naturalnym
            html_content: Zawartość HTML do analizy
        """
        try:
            intent = self.parse_intent(text)
            
            if not html_content:
                return ConversionResult(
                    success=False,
                    error="No HTML content provided"
                )
            
            if intent["action"] == "analyze":
                result = self.analyze_html(html_content)
            elif intent["action"] == "extract":
                result = {"extracted": self.extract_data(html_content)}
            elif intent["action"] == "validate":
                result = self.validate_html(html_content)
            elif intent["action"] == "seo":
                result = self.seo_analysis(html_content)
            elif intent["action"] == "links":
                links = re.findall(r'href=["\']([^"\']+)["\']', html_content)
                result = {"links": links}
            elif intent["action"] == "images":
                images = re.findall(r'src=["\']([^"\']+)["\']', html_content)
                result = {"images": images}
            else:
                result = self.analyze_html(html_content)
            
            return ConversionResult(
                success=True,
                command=f"HTML {intent['action']}",
                output=str(result),
                metadata={
                    "action": intent["action"],
                    "result": result
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3html - Generate HTML (WRITE)
# ============================================================================

class Text3HTML(BaseConverter):
    """
    Generator HTML.
    
    Funkcje:
    - Generowanie stron HTML
    - Komponenty UI
    - Landing pages
    - Email templates
    """
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę HTML"""
        return f"generate_{intent.get('template', 'page')}_html"
    
    TEMPLATES = {
        "page": '''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
{body}
</body>
</html>''',

        "landing": '''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, sans-serif; line-height: 1.6; }}
        .hero {{ 
            min-height: 100vh; 
            display: flex; 
            flex-direction: column;
            justify-content: center; 
            align-items: center;
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.25rem; margin-bottom: 2rem; opacity: 0.9; }}
        .btn {{
            padding: 1rem 2rem;
            font-size: 1.1rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            transition: transform 0.2s;
        }}
        .btn-primary {{ background: white; color: #667eea; }}
        .btn:hover {{ transform: translateY(-2px); }}
        .features {{ padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }}
        .features h2 {{ text-align: center; margin-bottom: 3rem; }}
        .feature-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
        .feature {{ padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .feature h3 {{ margin-bottom: 1rem; color: #667eea; }}
    </style>
</head>
<body>
    <section class="hero">
        <h1>{title}</h1>
        <p>{description}</p>
        <a href="#features" class="btn btn-primary">Learn More</a>
    </section>
    
    <section id="features" class="features">
        <h2>Features</h2>
        <div class="feature-grid">
{features}
        </div>
    </section>
</body>
</html>''',

        "component": '''<div class="{component_class}">
{content}
</div>

<style>
.{component_class} {{
{component_css}
}}
</style>''',

        "form": '''<form action="{action}" method="{method}" class="form">
{fields}
    <button type="submit" class="btn btn-primary">{submit_text}</button>
</form>

<style>
.form {{
    max-width: 500px;
    margin: 2rem auto;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}}
.form-group {{
    margin-bottom: 1.5rem;
}}
.form-group label {{
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}}
.form-group input, .form-group textarea, .form-group select {{
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}}
.btn-primary {{
    width: 100%;
    padding: 1rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
}}
</style>''',

        "table": '''<table class="table">
    <thead>
        <tr>
{headers}
        </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
</table>

<style>
.table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}}
.table th, .table td {{
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
}}
.table th {{
    background: #f8f9fa;
    font-weight: 600;
}}
.table tr:hover {{
    background: #f8f9fa;
}}
</style>''',

        "card": '''<div class="card">
    <div class="card-header">
        <h3>{title}</h3>
    </div>
    <div class="card-body">
        {content}
    </div>
    <div class="card-footer">
        {footer}
    </div>
</div>

<style>
.card {{
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    overflow: hidden;
}}
.card-header {{
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-bottom: 1px solid #ddd;
}}
.card-body {{
    padding: 1.5rem;
}}
.card-footer {{
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-top: 1px solid #ddd;
}}
</style>'''
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję"""
        text = text.lower()
        
        template = "page"
        if "landing" in text:
            template = "landing"
        elif "form" in text or "formularz" in text:
            template = "form"
        elif "table" in text or "tabela" in text:
            template = "table"
        elif "card" in text or "karta" in text:
            template = "card"
        elif "component" in text or "komponent" in text:
            template = "component"
        
        # Extract title
        title_match = re.search(r'(?:title|tytuł)[:\s]+["\']?([^"\']+)["\']?', text)
        title = title_match.group(1) if title_match else "My Page"
        
        return {
            "template": template,
            "title": title,
            "description": text
        }
    
    def generate_page(self, title: str, content: str = "", css: str = "") -> str:
        """Generuje stronę HTML"""
        
        default_css = '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; line-height: 1.6; padding: 2rem; }
        h1 { margin-bottom: 1rem; }
        p { margin-bottom: 1rem; }
        '''
        
        return self.TEMPLATES["page"].format(
            lang="pl",
            title=title,
            description=f"Page: {title}",
            css=css or default_css,
            body=content or f"<h1>{title}</h1>\n<p>Welcome to {title}</p>"
        )
    
    def generate_landing(self, title: str, description: str, features: List[Dict] = None) -> str:
        """Generuje landing page"""
        
        features = features or [
            {"title": "Feature 1", "description": "Description of feature 1"},
            {"title": "Feature 2", "description": "Description of feature 2"},
            {"title": "Feature 3", "description": "Description of feature 3"},
        ]
        
        features_html = ""
        for feature in features:
            features_html += f'''            <div class="feature">
                <h3>{feature["title"]}</h3>
                <p>{feature["description"]}</p>
            </div>
'''
        
        return self.TEMPLATES["landing"].format(
            lang="pl",
            title=title,
            description=description,
            features=features_html
        )
    
    def generate_form(self, fields: List[Dict], action: str = "#", method: str = "POST") -> str:
        """Generuje formularz"""
        
        fields_html = ""
        for field in fields:
            field_type = field.get("type", "text")
            field_name = field.get("name", "field")
            field_label = field.get("label", field_name.capitalize())
            
            if field_type == "textarea":
                input_html = f'<textarea name="{field_name}" rows="4"></textarea>'
            elif field_type == "select":
                options = "".join([f'<option value="{o}">{o}</option>' for o in field.get("options", [])])
                input_html = f'<select name="{field_name}">{options}</select>'
            else:
                input_html = f'<input type="{field_type}" name="{field_name}">'
            
            fields_html += f'''    <div class="form-group">
        <label for="{field_name}">{field_label}</label>
        {input_html}
    </div>
'''
        
        return self.TEMPLATES["form"].format(
            action=action,
            method=method,
            fields=fields_html,
            submit_text="Submit"
        )
    
    def generate_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Generuje tabelę"""
        
        headers_html = "".join([f'            <th>{h}</th>\n' for h in headers])
        
        rows_html = ""
        for row in rows:
            cells = "".join([f'            <td>{cell}</td>\n' for cell in row])
            rows_html += f'        <tr>\n{cells}        </tr>\n'
        
        return self.TEMPLATES["table"].format(
            headers=headers_html,
            rows=rows_html
        )
    
    def execute(self, text: str) -> ConversionResult:
        """Generuje HTML na podstawie opisu"""
        
        try:
            intent = self.parse_intent(text)
            
            if intent["template"] == "landing":
                html = self.generate_landing(
                    title=intent["title"],
                    description=intent["description"]
                )
            elif intent["template"] == "form":
                # Default form fields
                fields = [
                    {"name": "name", "label": "Name", "type": "text"},
                    {"name": "email", "label": "Email", "type": "email"},
                    {"name": "message", "label": "Message", "type": "textarea"}
                ]
                html = self.generate_form(fields)
            elif intent["template"] == "table":
                # Default table
                html = self.generate_table(
                    headers=["ID", "Name", "Status"],
                    rows=[
                        ["1", "Item 1", "Active"],
                        ["2", "Item 2", "Pending"],
                        ["3", "Item 3", "Completed"]
                    ]
                )
            else:
                html = self.generate_page(title=intent["title"])
            
            return ConversionResult(
                success=True,
                command=f"Generated {intent['template']} HTML",
                output=html,
                metadata={
                    "template": intent["template"],
                    "title": intent["title"],
                    "lines": len(html.split('\n'))
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))
    
    def save_html(self, html: str, filepath: str) -> bool:
        """Zapisuje HTML do pliku"""
        try:
            Path(filepath).write_text(html)
            return True
        except Exception as e:
            logger.error(f"Error saving HTML: {e}")
            return False


# ============================================================================
# text4html - Live HTML Updates (STREAM)
# ============================================================================

class Text4HTML(BaseStreamConverter):
    """
    Real-time HTML streaming.
    
    Funkcje:
    - Live reload
    - Hot module replacement
    - File watching
    - Browser sync
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._watch_paths: List[Path] = []
        self._last_modified: Dict[str, float] = {}
    
    async def connect(self, target: str) -> bool:
        """
        Połącz z katalogiem do monitorowania.
        
        Args:
            target: Ścieżka do katalogu/pliku
        """
        try:
            path = Path(target)
            
            if path.is_dir():
                self._watch_paths = list(path.glob("**/*.html"))
            elif path.is_file():
                self._watch_paths = [path]
            else:
                # Pattern
                self._watch_paths = list(Path(".").glob(target))
            
            # Initialize modification times
            for p in self._watch_paths:
                if p.exists():
                    self._last_modified[str(p)] = p.stat().st_mtime
            
            self.state = StreamState.CONNECTED
            logger.info(f"Watching {len(self._watch_paths)} HTML files")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.state = StreamState.ERROR
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self._watch_paths = []
        self._last_modified = {}
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Nie używane w text4html"""
        return True
    
    async def receive(self) -> Optional[StreamEvent]:
        """
        Sprawdza zmiany w plikach.
        
        Returns:
            StreamEvent jeśli wykryto zmianę
        """
        for path in self._watch_paths:
            if not path.exists():
                continue
            
            current_mtime = path.stat().st_mtime
            last_mtime = self._last_modified.get(str(path), 0)
            
            if current_mtime > last_mtime:
                self._last_modified[str(path)] = current_mtime
                
                # Read new content
                content = path.read_text()
                
                return StreamEvent(
                    timestamp=datetime.now(),
                    event_type="file_changed",
                    data={
                        "path": str(path),
                        "content": content,
                        "size": len(content)
                    },
                    source="text4html",
                    metadata={
                        "mtime": current_mtime
                    }
                )
        
        # No changes, wait a bit
        await asyncio.sleep(0.5)
        return None
    
    def add_watch(self, path: str):
        """Dodaj ścieżkę do monitorowania"""
        p = Path(path)
        if p.exists() and p not in self._watch_paths:
            self._watch_paths.append(p)
            self._last_modified[str(p)] = p.stat().st_mtime
    
    def remove_watch(self, path: str):
        """Usuń ścieżkę z monitorowania"""
        p = Path(path)
        if p in self._watch_paths:
            self._watch_paths.remove(p)
            self._last_modified.pop(str(p), None)
