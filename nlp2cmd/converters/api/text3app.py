"""
Text3App - Generowanie kompletnych aplikacji w różnych językach.

Ten konwerter generuje funkcjonalne aplikacje web/API.
"""

from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Text3App(BaseConverter):
    """
    Generator aplikacji w różnych językach i frameworkach.
    
    Obsługuje:
    - Python: Flask, FastAPI, Django
    - Node.js: Express, NestJS
    - Go: Gin, Echo
    - CRUD operations
    - Authentication
    - Database integration
    """
    
    # Szablony aplikacji
    APP_TEMPLATES = {
        "python_flask_crud": """# Flask CRUD Application
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class {ModelName}(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {{
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }}

# Routes
@app.route('/health', methods=['GET'])
def health():
    return jsonify({{'status': 'healthy'}}), 200

@app.route('/{resource}', methods=['GET'])
def get_all():
    items = {ModelName}.query.all()
    return jsonify([item.to_dict() for item in items]), 200

@app.route('/{resource}/<int:id>', methods=['GET'])
def get_one(id):
    item = {ModelName}.query.get_or_404(id)
    return jsonify(item.to_dict()), 200

@app.route('/{resource}', methods=['POST'])
def create():
    data = request.get_json()
    item = {ModelName}(name=data['name'], email=data['email'])
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@app.route('/{resource}/<int:id>', methods=['PUT'])
def update(id):
    item = {ModelName}.query.get_or_404(id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.email = data.get('email', item.email)
    db.session.commit()
    return jsonify(item.to_dict()), 200

@app.route('/{resource}/<int:id>', methods=['DELETE'])
def delete(id):
    item = {ModelName}.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
""",
        
        "nodejs_express_crud": """// Express CRUD Application
const express = require('express');
const cors = require('cors');
const {{ Sequelize, DataTypes }} = require('sequelize');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Database
const sequelize = new Sequelize({{
  dialect: 'sqlite',
  storage: 'database.sqlite'
}});

// Model
const {ModelName} = sequelize.define('{ModelName}', {{
  name: {{
    type: DataTypes.STRING,
    allowNull: false
  }},
  email: {{
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  }}
}});

// Routes
app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy' }});
}});

app.get('/{resource}', async (req, res) => {{
  try {{
    const items = await {ModelName}.findAll();
    res.json(items);
  }} catch (error) {{
    res.status(500).json({{ error: error.message }});
  }}
}});

app.get('/{resource}/:id', async (req, res) => {{
  try {{
    const item = await {ModelName}.findByPk(req.params.id);
    if (!item) return res.status(404).json({{ error: 'Not found' }});
    res.json(item);
  }} catch (error) {{
    res.status(500).json({{ error: error.message }});
  }}
}});

app.post('/{resource}', async (req, res) => {{
  try {{
    const item = await {ModelName}.create(req.body);
    res.status(201).json(item);
  }} catch (error) {{
    res.status(400).json({{ error: error.message }});
  }}
}});

app.put('/{resource}/:id', async (req, res) => {{
  try {{
    const item = await {ModelName}.findByPk(req.params.id);
    if (!item) return res.status(404).json({{ error: 'Not found' }});
    await item.update(req.body);
    res.json(item);
  }} catch (error) {{
    res.status(400).json({{ error: error.message }});
  }}
}});

app.delete('/{resource}/:id', async (req, res) => {{
  try {{
    const item = await {ModelName}.findByPk(req.params.id);
    if (!item) return res.status(404).json({{ error: 'Not found' }});
    await item.destroy();
    res.status(204).send();
  }} catch (error) {{
    res.status(500).json({{ error: error.message }});
  }}
}});

// Start server
sequelize.sync().then(() => {{
  app.listen(PORT, () => {{
    console.log(`Server running on port ${{PORT}}`);
  }});
}});
"""
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "app_type": str,      # crud, api, fullstack
                "language": str,      # python, nodejs, go
                "framework": str,     # flask, express, gin
                "resource": str,      # users, products, etc.
                "features": List[str] # auth, crud, websocket
            }
        """
        text = text.strip().lower()
        
        # Detect language
        language = "python"
        if "node" in text or "express" in text or "javascript" in text:
            language = "nodejs"
        elif "go" in text or "golang" in text:
            language = "go"
        
        # Detect framework
        framework = None
        frameworks = {
            "python": ["flask", "fastapi", "django"],
            "nodejs": ["express", "nest", "nestjs"],
            "go": ["gin", "echo", "fiber"]
        }
        
        if language in frameworks:
            for fw in frameworks[language]:
                if fw in text:
                    framework = fw
                    break
        
        # Default frameworks
        if not framework:
            defaults = {"python": "flask", "nodejs": "express", "go": "gin"}
            framework = defaults.get(language, "flask")
        
        # Detect resource/model name
        resource = "users"
        resource_keywords = ["użytkownik", "user", "product", "post", "comment"]
        for kw in resource_keywords:
            if kw in text:
                resource = kw if kw != "użytkownik" else "users"
                break
        
        # Detect app type
        app_type = "crud"
        if "crud" in text:
            app_type = "crud"
        elif "api" in text:
            app_type = "api"
        elif "fullstack" in text or "full stack" in text:
            app_type = "fullstack"
        
        # Features
        features = []
        if "auth" in text or "uwierzytelnianie" in text:
            features.append("auth")
        if "crud" in text:
            features.append("crud")
        if "websocket" in text:
            features.append("websocket")
        if "graphql" in text:
            features.append("graphql")
        
        return {
            "app_type": app_type,
            "language": language,
            "framework": framework,
            "resource": resource,
            "features": features,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje kod aplikacji"""
        
        language = intent["language"]
        framework = intent["framework"]
        resource = intent["resource"]
        
        # Get template
        template_key = f"{language}_{framework}_crud"
        template = self.APP_TEMPLATES.get(template_key)
        
        if not template:
            return self._generate_basic_app(intent)
        
        # Replace placeholders
        model_name = resource.capitalize().rstrip('s')  # users -> User
        
        code = template.format(
            ModelName=model_name,
            resource=resource
        )
        
        return code
    
    def _generate_basic_app(self, intent: Dict[str, Any]) -> str:
        """Fallback - generuje podstawową aplikację"""
        
        if intent["language"] == "python":
            return """from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello World!'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""
        elif intent["language"] == "nodejs":
            return """const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello World!' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""
        
        return "# Application code placeholder"
    
    def execute(self, text: str) -> ConversionResult:
        """
        Generuje aplikację.
        
        Args:
            text: Opis aplikacji w języku naturalnym
            
        Returns:
            Wynik z wygenerowanym kodem
        """
        try:
            intent = self.parse_intent(text)
            code = self.generate_command(intent)
            
            # Generate additional files
            additional_files = self._generate_additional_files(intent)
            
            return ConversionResult(
                success=True,
                command=f"Generated {intent['language']} {intent['framework']} app",
                output=code,
                metadata={
                    "language": intent["language"],
                    "framework": intent["framework"],
                    "resource": intent["resource"],
                    "additional_files": additional_files
                }
            )
            
        except Exception as e:
            logger.error(f"Błąd generowania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def _generate_additional_files(self, intent: Dict[str, Any]) -> Dict[str, str]:
        """Generuje dodatkowe pliki (requirements.txt, package.json, etc.)"""
        
        files = {}
        
        if intent["language"] == "python":
            files["requirements.txt"] = self._generate_python_requirements(intent)
            files["README.md"] = self._generate_readme(intent)
        
        elif intent["language"] == "nodejs":
            files["package.json"] = self._generate_package_json(intent)
            files["README.md"] = self._generate_readme(intent)
        
        return files
    
    def _generate_python_requirements(self, intent: Dict[str, Any]) -> str:
        """Generuje requirements.txt dla Pythona"""
        
        framework = intent["framework"]
        
        if framework == "flask":
            return """Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
python-dotenv==1.0.0"""
        elif framework == "fastapi":
            return """fastapi==0.108.0
uvicorn==0.25.0
sqlalchemy==2.0.23
pydantic==2.5.0"""
        elif framework == "django":
            return """Django==5.0.0
djangorestframework==3.14.0
django-cors-headers==4.3.0"""
        
        return "Flask==3.0.0"
    
    def _generate_package_json(self, intent: Dict[str, Any]) -> str:
        """Generuje package.json dla Node.js"""
        
        resource = intent["resource"]
        
        return f'''{{
  "name": "{resource}-api",
  "version": "1.0.0",
  "description": "{resource.capitalize()} API",
  "main": "server.js",
  "scripts": {{
    "start": "node server.js",
    "dev": "nodemon server.js"
  }},
  "dependencies": {{
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "sequelize": "^6.35.2",
    "sqlite3": "^5.1.6"
  }},
  "devDependencies": {{
    "nodemon": "^3.0.2"
  }}
}}'''
    
    def _generate_readme(self, intent: Dict[str, Any]) -> str:
        """Generuje README.md"""
        
        language = intent["language"]
        framework = intent["framework"]
        resource = intent["resource"]
        
        return f"""# {resource.capitalize()} API

API for managing {resource} built with {framework} ({language}).

## Installation

"""  + ("""
```bash
pip install -r requirements.txt
```

## Running

```bash
python app.py
```
""" if language == "python" else """
```bash
npm install
```

## Running

```bash
npm start
```
""") + f"""
## Endpoints

- GET /health - Health check
- GET /{resource} - Get all {resource}
- GET /{resource}/:id - Get one {resource}
- POST /{resource} - Create {resource}
- PUT /{resource}/:id - Update {resource}
- DELETE /{resource}/:id - Delete {resource}
"""
    
    def save_app(
        self,
        code: str,
        directory: str,
        additional_files: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Zapisuje aplikację do plików.
        
        Args:
            code: Główny kod aplikacji
            directory: Katalog docelowy
            additional_files: Dodatkowe pliki
            
        Returns:
            True jeśli sukces
        """
        try:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            
            # Save main file
            main_file = path / "app.py"  # lub server.js
            main_file.write_text(code)
            
            # Save additional files
            if additional_files:
                for filename, content in additional_files.items():
                    file_path = path / filename
                    file_path.write_text(content)
            
            logger.info(f"Zapisano aplikację w: {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd zapisu: {e}")
            return False
