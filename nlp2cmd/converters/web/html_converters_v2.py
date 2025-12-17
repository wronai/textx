"""
HTML Converters v2 - Corrected Nomenclature

Prawidłowa nomenklatura:
- text2html: GENERATE HTML code from text description
- text3html: EDIT existing HTML file (modify, add, remove elements)
- text4html: SERVICE - distributed service for generate/edit on all app levels (firmware→frontend)
"""

from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
from nlp2cmd.core.stream_base import BaseStreamConverter, StreamEvent, StreamConfig, StreamState
from pathlib import Path
from datetime import datetime
import asyncio
import re
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# text2html - GENERATE HTML code from text description
# ============================================================================

class Text2HTML(BaseConverter):
    """
    Generator HTML - tworzy kod HTML z opisu tekstowego.
    
    Funkcje:
    - Generowanie stron HTML z opisu
    - Tworzenie komponentów UI
    - Landing pages, formularze, tabele
    - Email templates
    
    Przykłady:
    - "generate landing page for CloudSync"
    - "create contact form"
    - "generate table with user data"
    """
    
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

        "form": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, sans-serif; padding: 2rem; background: #f5f5f5; }}
        .form {{
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .form h2 {{ margin-bottom: 1.5rem; color: #333; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        .form-group label {{ display: block; margin-bottom: 0.5rem; font-weight: 500; }}
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
        .btn-primary:hover {{ background: #5a67d8; }}
    </style>
</head>
<body>
    <form action="{action}" method="{method}" class="form">
        <h2>{title}</h2>
{fields}
        <button type="submit" class="btn-primary">{submit_text}</button>
    </form>
</body>
</html>''',

        "table": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, sans-serif; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ margin-bottom: 1.5rem; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        .table th, .table td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }}
        .table th {{ background: #f8f9fa; font-weight: 600; }}
        .table tr:hover {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <table class="table">
            <thead>
                <tr>{headers}</tr>
            </thead>
            <tbody>
{rows}
            </tbody>
        </table>
    </div>
</body>
</html>''',

        "card": '''<div class="card" style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; max-width: 400px;">
    <div class="card-header" style="padding: 1rem 1.5rem; background: #f8f9fa; border-bottom: 1px solid #ddd;">
        <h3 style="margin: 0;">{title}</h3>
    </div>
    <div class="card-body" style="padding: 1.5rem;">
        {content}
    </div>
    <div class="card-footer" style="padding: 1rem 1.5rem; background: #f8f9fa; border-top: 1px solid #ddd;">
        {footer}
    </div>
</div>'''
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        return f"generate_{intent.get('template', 'page')}_html"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję generowania HTML"""
        text_lower = text.lower()
        
        template = "page"
        if "landing" in text_lower:
            template = "landing"
        elif "form" in text_lower or "formularz" in text_lower:
            template = "form"
        elif "table" in text_lower or "tabela" in text_lower:
            template = "table"
        elif "card" in text_lower or "karta" in text_lower:
            template = "card"
        
        # Extract title
        title_match = re.search(r'(?:title|tytuł)[:\s]+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Try to extract from "for X" pattern
            for_match = re.search(r'(?:for|dla|about)\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
            title = for_match.group(1).strip() if for_match else "My Page"
        
        return {
            "template": template,
            "title": title,
            "description": text
        }
    
    def generate_landing(self, title: str, description: str, features: List[Dict] = None) -> str:
        """Generuje landing page"""
        features = features or [
            {"title": "Fast", "description": "Lightning fast performance"},
            {"title": "Secure", "description": "Enterprise-grade security"},
            {"title": "Scalable", "description": "Grows with your needs"},
        ]
        
        features_html = ""
        for feature in features:
            features_html += f'''            <div class="feature">
                <h3>{feature["title"]}</h3>
                <p>{feature["description"]}</p>
            </div>
'''
        
        return self.TEMPLATES["landing"].format(
            lang="en",
            title=title,
            description=description,
            features=features_html
        )
    
    def generate_form(self, title: str, fields: List[Dict] = None) -> str:
        """Generuje formularz HTML"""
        fields = fields or [
            {"name": "name", "label": "Name", "type": "text"},
            {"name": "email", "label": "Email", "type": "email"},
            {"name": "message", "label": "Message", "type": "textarea"}
        ]
        
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
            
            fields_html += f'''        <div class="form-group">
            <label for="{field_name}">{field_label}</label>
            {input_html}
        </div>
'''
        
        return self.TEMPLATES["form"].format(
            title=title,
            action="#",
            method="POST",
            fields=fields_html,
            submit_text="Submit"
        )
    
    def generate_table(self, title: str, headers: List[str] = None, rows: List[List[str]] = None) -> str:
        """Generuje tabelę HTML"""
        headers = headers or ["ID", "Name", "Status", "Date"]
        rows = rows or [
            ["1", "Item One", "Active", "2024-01-15"],
            ["2", "Item Two", "Pending", "2024-01-16"],
            ["3", "Item Three", "Completed", "2024-01-17"]
        ]
        
        headers_html = "".join([f'<th>{h}</th>' for h in headers])
        rows_html = ""
        for row in rows:
            cells = "".join([f'<td>{cell}</td>' for cell in row])
            rows_html += f'                <tr>{cells}</tr>\n'
        
        return self.TEMPLATES["table"].format(
            title=title,
            headers=headers_html,
            rows=rows_html
        )
    
    def generate_page(self, title: str, content: str = "") -> str:
        """Generuje prostą stronę HTML"""
        default_css = '''        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; line-height: 1.6; padding: 2rem; }
        h1 { margin-bottom: 1rem; color: #333; }
        p { margin-bottom: 1rem; color: #666; }'''
        
        body = content or f'''    <h1>{title}</h1>
    <p>Welcome to {title}. This page was generated automatically.</p>'''
        
        return self.TEMPLATES["page"].format(
            lang="en",
            title=title,
            description=f"Page: {title}",
            css=default_css,
            body=body
        )
    
    def execute(self, text: str) -> ConversionResult:
        """Generuje HTML na podstawie opisu tekstowego"""
        try:
            intent = self.parse_intent(text)
            
            if intent["template"] == "landing":
                html = self.generate_landing(intent["title"], intent["description"])
            elif intent["template"] == "form":
                html = self.generate_form(intent["title"])
            elif intent["template"] == "table":
                html = self.generate_table(intent["title"])
            elif intent["template"] == "card":
                html = self.TEMPLATES["card"].format(
                    title=intent["title"],
                    content="<p>Card content goes here.</p>",
                    footer="<a href='#'>Learn more</a>"
                )
            else:
                html = self.generate_page(intent["title"])
            
            return ConversionResult(
                success=True,
                command=f"Generated {intent['template']} HTML",
                output=html,
                metadata={
                    "template": intent["template"],
                    "title": intent["title"],
                    "lines": len(html.split('\n')),
                    "size_bytes": len(html.encode('utf-8'))
                }
            )
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3html - EDIT existing HTML file
# ============================================================================

class Text3HTML(BaseConverter):
    """
    Edytor HTML - modyfikuje istniejący kod HTML.
    
    Funkcje:
    - Dodawanie elementów do HTML
    - Usuwanie elementów
    - Modyfikacja atrybutów
    - Zmiana stylów
    - Aktualizacja treści
    
    Przykłady:
    - "add button to form"
    - "change title to 'New Title'"
    - "remove footer section"
    - "add class 'active' to nav"
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        return f"html_edit_{intent.get('action', 'modify')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję edycji HTML"""
        text_lower = text.lower()
        
        action = "modify"
        if any(word in text_lower for word in ["add", "dodaj", "insert", "wstaw"]):
            action = "add"
        elif any(word in text_lower for word in ["remove", "usuń", "delete", "skasuj"]):
            action = "remove"
        elif any(word in text_lower for word in ["change", "zmień", "update", "modify", "replace"]):
            action = "modify"
        elif any(word in text_lower for word in ["style", "css", "styl"]):
            action = "style"
        
        # Extract target element
        target_match = re.search(r'(?:to|in|from|w|do|z)\s+["\']?(\w+)["\']?', text, re.IGNORECASE)
        target = target_match.group(1) if target_match else None
        
        # Extract value
        value_match = re.search(r'["\']([^"\']+)["\']', text)
        value = value_match.group(1) if value_match else None
        
        return {
            "action": action,
            "target": target,
            "value": value,
            "description": text
        }
    
    def add_element(self, html: str, element: str, target: str = "body", position: str = "end") -> str:
        """Dodaje element do HTML"""
        if target == "body":
            if position == "end":
                html = html.replace("</body>", f"    {element}\n</body>")
            else:
                html = html.replace("<body>", f"<body>\n    {element}")
        elif target == "head":
            html = html.replace("</head>", f"    {element}\n</head>")
        else:
            # Add after target element
            pattern = rf'(<{target}[^>]*>.*?</{target}>)'
            html = re.sub(pattern, rf'\1\n    {element}', html, flags=re.DOTALL | re.IGNORECASE)
        return html
    
    def remove_element(self, html: str, selector: str) -> str:
        """Usuwa element z HTML"""
        # Simple tag removal
        pattern = rf'<{selector}[^>]*>.*?</{selector}>'
        html = re.sub(pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
        return html
    
    def modify_element(self, html: str, target: str, attribute: str, value: str) -> str:
        """Modyfikuje atrybut elementu"""
        if attribute == "text" or attribute == "content":
            # Change inner text
            pattern = rf'(<{target}[^>]*>).*?(</{target}>)'
            html = re.sub(pattern, rf'\1{value}\2', html, flags=re.DOTALL | re.IGNORECASE)
        else:
            # Change attribute
            pattern = rf'(<{target})([^>]*)(>)'
            
            def replace_attr(match):
                tag_start = match.group(1)
                attrs = match.group(2)
                tag_end = match.group(3)
                
                # Check if attribute exists
                attr_pattern = rf'{attribute}=["\'][^"\']*["\']'
                if re.search(attr_pattern, attrs):
                    attrs = re.sub(attr_pattern, f'{attribute}="{value}"', attrs)
                else:
                    attrs += f' {attribute}="{value}"'
                
                return f'{tag_start}{attrs}{tag_end}'
            
            html = re.sub(pattern, replace_attr, html, count=1, flags=re.IGNORECASE)
        
        return html
    
    def add_style(self, html: str, selector: str, styles: str) -> str:
        """Dodaje style CSS"""
        style_block = f"\n{selector} {{ {styles} }}\n"
        
        if "</style>" in html:
            html = html.replace("</style>", f"{style_block}</style>")
        elif "</head>" in html:
            html = html.replace("</head>", f"<style>{style_block}</style>\n</head>")
        
        return html
    
    def execute(self, text: str, html_content: str = None) -> ConversionResult:
        """Edytuje HTML na podstawie komendy"""
        try:
            if not html_content:
                return ConversionResult(
                    success=False,
                    error="No HTML content provided for editing. Use text2html to generate HTML first."
                )
            
            intent = self.parse_intent(text)
            modified_html = html_content
            
            if intent["action"] == "add":
                # Determine what to add
                if "button" in text.lower():
                    element = '<button class="btn">Click me</button>'
                elif "link" in text.lower():
                    element = '<a href="#">New Link</a>'
                elif "paragraph" in text.lower() or "text" in text.lower():
                    element = f'<p>{intent["value"] or "New paragraph"}</p>'
                elif "div" in text.lower():
                    element = f'<div>{intent["value"] or ""}</div>'
                else:
                    element = f'<div>{intent["value"] or "New element"}</div>'
                
                modified_html = self.add_element(html_content, element, intent["target"] or "body")
                
            elif intent["action"] == "remove":
                target = intent["target"] or intent["value"]
                if target:
                    modified_html = self.remove_element(html_content, target)
                    
            elif intent["action"] == "modify":
                if intent["target"] and intent["value"]:
                    # Try to determine what to modify
                    if "title" in text.lower():
                        modified_html = self.modify_element(html_content, "title", "text", intent["value"])
                    elif "class" in text.lower():
                        modified_html = self.modify_element(html_content, intent["target"], "class", intent["value"])
                    else:
                        modified_html = self.modify_element(html_content, intent["target"], "text", intent["value"])
                        
            elif intent["action"] == "style":
                if intent["target"] and intent["value"]:
                    modified_html = self.add_style(html_content, intent["target"], intent["value"])
            
            changes_made = modified_html != html_content
            
            return ConversionResult(
                success=True,
                command=f"HTML {intent['action']}",
                output=modified_html,
                metadata={
                    "action": intent["action"],
                    "target": intent["target"],
                    "changes_made": changes_made,
                    "original_size": len(html_content),
                    "new_size": len(modified_html)
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text4html - SERVICE for distributed HTML generation/editing
# ============================================================================

class Text4HTML(BaseStreamConverter):
    """
    Usługa HTML - rozproszona usługa do generowania i edycji HTML
    na wszystkich poziomach aplikacji (firmware → backend → frontend).
    
    Funkcje:
    - REST API do generowania HTML
    - WebSocket streaming
    - Pipeline processing
    - Multi-language support (wywoływane z dowolnego języka)
    - Deployment do różnych celów
    
    Przykłady użycia:
    - Z firmware (C): nlp2cmd_convert("text4html", "generate landing page")
    - Z backend (Python): client.convert("text4html", "edit form add button")
    - Z frontend (JS): await client.stream("text4html", "generate dashboard")
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._generator = Text2HTML()
        self._editor = Text3HTML()
        self._current_html: str = None
        self._session_id: str = None
        self._request_count: int = 0
    
    async def connect(self, target: str) -> bool:
        """
        Połącz z usługą text4html.
        
        Args:
            target: URL usługi lub identyfikator sesji
        """
        try:
            self._session_id = target or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.state = StreamState.CONNECTED
            logger.info(f"Text4HTML service connected: {self._session_id}")
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.state = StreamState.ERROR
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz z usługą"""
        self._session_id = None
        self._current_html = None
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """
        Wyślij komendę do usługi.
        
        Args:
            data: Dict z polami:
                - action: "generate" | "edit" | "deploy"
                - command: komenda w języku naturalnym
                - html_content: (opcjonalnie) HTML do edycji
                - deploy_target: (opcjonalnie) cel deploymentu
        """
        try:
            if isinstance(data, str):
                data = {"action": "generate", "command": data}
            
            action = data.get("action", "generate")
            command = data.get("command", "")
            
            self._request_count += 1
            
            if action == "generate":
                result = self._generator.execute(command)
                if result.success:
                    self._current_html = result.output
                return result.success
                
            elif action == "edit":
                html_content = data.get("html_content") or self._current_html
                result = self._editor.execute(command, html_content)
                if result.success:
                    self._current_html = result.output
                return result.success
                
            elif action == "deploy":
                target = data.get("deploy_target", {})
                return await self._deploy(target)
            
            return False
            
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    async def receive(self) -> Optional[StreamEvent]:
        """
        Odbiera wynik operacji jako event.
        
        Returns:
            StreamEvent z wygenerowanym/zedytowanym HTML
        """
        if not self._current_html:
            await asyncio.sleep(0.1)
            return None
        
        event = StreamEvent(
            timestamp=datetime.now(),
            event_type="html_result",
            data={
                "html": self._current_html,
                "size_bytes": len(self._current_html.encode('utf-8')),
                "lines": len(self._current_html.split('\n'))
            },
            source=f"text4html://{self._session_id}",
            metadata={
                "session_id": self._session_id,
                "request_count": self._request_count
            }
        )
        
        return event
    
    async def _deploy(self, target: Dict[str, Any]) -> bool:
        """Deployuje HTML do celu"""
        deploy_type = target.get("type", "file")
        
        if deploy_type == "file":
            path = target.get("path", "/tmp/generated.html")
            try:
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).write_text(self._current_html)
                logger.info(f"Deployed to file: {path}")
                return True
            except Exception as e:
                logger.error(f"Deploy error: {e}")
                return False
                
        elif deploy_type == "webhook":
            url = target.get("url")
            # W produkcji: HTTP POST do URL
            logger.info(f"Would deploy to webhook: {url}")
            return True
            
        elif deploy_type == "s3":
            bucket = target.get("bucket")
            key = target.get("key")
            # W produkcji: upload do S3
            logger.info(f"Would deploy to S3: {bucket}/{key}")
            return True
        
        return False
    
    # Convenience methods for direct use
    
    def generate(self, command: str) -> ConversionResult:
        """Synchroniczne generowanie HTML"""
        return self._generator.execute(command)
    
    def edit(self, command: str, html_content: str = None) -> ConversionResult:
        """Synchroniczna edycja HTML"""
        content = html_content or self._current_html
        result = self._editor.execute(command, content)
        if result.success:
            self._current_html = result.output
        return result
    
    def get_current_html(self) -> Optional[str]:
        """Zwraca aktualny HTML"""
        return self._current_html
    
    def set_html(self, html: str):
        """Ustawia HTML do edycji"""
        self._current_html = html


# ============================================================================
# Utility functions
# ============================================================================

def analyze_html(html: str) -> Dict[str, Any]:
    """Analizuje strukturę HTML (utility function)"""
    tags = re.findall(r'<(\w+)', html)
    tag_counts = {}
    for tag in tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1) if title_match else None
    
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    images = re.findall(r'src=["\']([^"\']+)["\']', html)
    
    return {
        "title": title,
        "tag_counts": tag_counts,
        "total_tags": len(tags),
        "links_count": len(links),
        "images_count": len(images),
        "size_bytes": len(html.encode('utf-8')),
        "lines": len(html.split('\n'))
    }


def validate_html(html: str) -> Dict[str, Any]:
    """Waliduje HTML (utility function)"""
    errors = []
    warnings = []
    
    if not html.strip().lower().startswith('<!doctype'):
        warnings.append("Missing DOCTYPE declaration")
    
    if '<html' not in html.lower():
        errors.append("Missing <html> tag")
    if '<head' not in html.lower():
        warnings.append("Missing <head> tag")
    if '<body' not in html.lower():
        warnings.append("Missing <body> tag")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
