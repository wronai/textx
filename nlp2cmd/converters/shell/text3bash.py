"""
Text3Bash - Generowanie skryptów bash na podstawie opisów w języku naturalnym.

Ten konwerter generuje kompletne, gotowe do użycia skrypty bash.
"""

from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Text3Bash(BaseConverter):
    """
    Generator skryptów bash z języka naturalnego.
    
    Obsługuje:
    - Kompletne skrypty z obsługą błędów
    - Funkcje i zmienne
    - Argumenty wiersza poleceń
    - Logging i monitoring
    - Best practices bash
    """
    
    # Szablony dla różnych typów skryptów
    SCRIPT_TEMPLATES = {
        "backup": {
            "description": "Backup script template",
            "structure": ["setup", "validation", "backup", "cleanup", "notification"]
        },
        "deploy": {
            "description": "Deployment script template",
            "structure": ["setup", "build", "test", "deploy", "verify"]
        },
        "monitor": {
            "description": "Monitoring script template",
            "structure": ["setup", "check", "alert", "log"]
        },
        "cron": {
            "description": "Cron job template",
            "structure": ["setup", "lock", "execute", "unlock", "log"]
        }
    }
    
    def __init__(
        self,
        shebang: str = "#!/bin/bash",
        set_flags: List[str] = ["e", "u", "o pipefail"],
        include_logging: bool = True,
        include_colors: bool = True,
        **kwargs
    ):
        """
        Inicjalizacja Text3Bash.
        
        Args:
            shebang: Shebang line
            set_flags: Flagi set (e=exit on error, u=undefined vars, pipefail)
            include_logging: Czy dodawać funkcje logowania
            include_colors: Czy używać kolorów w output
        """
        super().__init__(**kwargs)
        self.shebang = shebang
        self.set_flags = set_flags
        self.include_logging = include_logging
        self.include_colors = include_colors
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "script_type": str,     # backup, deploy, monitor, custom
                "operations": List[str], # Lista operacji
                "requires_args": bool,   # Czy wymaga argumentów CLI
                "requires_root": bool,   # Czy wymaga root
                "features": List[str]    # Dodatkowe funkcje
            }
        """
        text = text.strip().lower()
        
        # Wykryj typ skryptu
        script_type = "custom"
        for stype in self.SCRIPT_TEMPLATES:
            if stype in text:
                script_type = stype
                break
        
        # Wykryj czy wymaga root
        requires_root = any(keyword in text for keyword in [
            "sudo", "root", "system", "instaluj", "install"
        ])
        
        # Wykryj czy wymaga argumentów
        requires_args = any(keyword in text for keyword in [
            "parametr", "argument", "opcje", "options"
        ])
        
        # Wyodrębnij operacje (uproszczona wersja)
        operations = self._extract_operations(text)
        
        # Dodatkowe funkcje
        features = []
        if "log" in text or "logowanie" in text:
            features.append("logging")
        if "email" in text or "powiadomienie" in text:
            features.append("notification")
        if "retry" in text or "ponów" in text:
            features.append("retry")
        
        return {
            "script_type": script_type,
            "operations": operations,
            "requires_args": requires_args,
            "requires_root": requires_root,
            "features": features,
            "description": text
        }
    
    def _extract_operations(self, text: str) -> List[str]:
        """Ekstraktuje operacje ze tekstu"""
        # Uproszczona wersja - można rozwinąć z LLM
        operations = []
        
        operation_keywords = {
            "backup": ["backup", "kopia", "archiwum"],
            "check": ["sprawdź", "check", "verify"],
            "deploy": ["wdróż", "deploy"],
            "notify": ["powiadom", "notify", "email"],
            "cleanup": ["wyczyść", "cleanup", "remove old"],
        }
        
        for op, keywords in operation_keywords.items():
            if any(kw in text for kw in keywords):
                operations.append(op)
        
        return operations or ["main"]
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje skrypt bash.
        
        Returns:
            Kompletny skrypt bash
        """
        script_parts = []
        
        # 1. Header
        script_parts.append(self._generate_header(intent))
        
        # 2. Configuration
        script_parts.append(self._generate_config(intent))
        
        # 3. Helper functions
        if self.include_logging:
            script_parts.append(self._generate_logging_functions())
        
        if self.include_colors:
            script_parts.append(self._generate_color_functions())
        
        # 4. Main functions
        for operation in intent["operations"]:
            script_parts.append(self._generate_function(operation, intent))
        
        # 5. Argument parsing
        if intent["requires_args"]:
            script_parts.append(self._generate_arg_parser())
        
        # 6. Main execution
        script_parts.append(self._generate_main(intent))
        
        return "\n\n".join(script_parts)
    
    def _generate_header(self, intent: Dict[str, Any]) -> str:
        """Generuje header skryptu"""
        flags = ",".join(self.set_flags) if self.set_flags else ""
        
        header = f"""{self.shebang}
#
# Generated by NLP2CMD
# Description: {intent['description']}
# Type: {intent['script_type']}
#

set -{flags}"""
        
        return header
    
    def _generate_config(self, intent: Dict[str, Any]) -> str:
        """Generuje sekcję konfiguracji"""
        config = """# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "$0")"
LOG_FILE="${SCRIPT_DIR}/${SCRIPT_NAME}.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)"""
        
        if intent["script_type"] == "backup":
            config += """
BACKUP_DIR="${SCRIPT_DIR}/backups"
BACKUP_FILE="backup_${TIMESTAMP}.tar.gz"
"""
        
        return config
    
    def _generate_logging_functions(self) -> str:
        """Generuje funkcje logowania"""
        return """# Logging functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO: $*"
}

log_error() {
    log "ERROR: $*" >&2
}

log_success() {
    log "SUCCESS: $*"
}"""
    
    def _generate_color_functions(self) -> str:
        """Generuje funkcje kolorów"""
        return """# Color functions
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

print_error() {
    echo -e "${RED}ERROR: $*${NC}" >&2
}

print_success() {
    echo -e "${GREEN}SUCCESS: $*${NC}"
}

print_info() {
    echo -e "${YELLOW}INFO: $*${NC}"
}"""
    
    def _generate_function(self, operation: str, intent: Dict[str, Any]) -> str:
        """Generuje funkcję dla konkretnej operacji"""
        
        if operation == "backup":
            return """# Backup function
do_backup() {
    log_info "Starting backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" . \\
        --exclude="${BACKUP_DIR}" \\
        --exclude=".git" \\
        --exclude="*.log" || {
        log_error "Backup failed"
        return 1
    }
    
    log_success "Backup completed: ${BACKUP_FILE}"
    return 0
}"""
        
        elif operation == "check":
            return """# Check function
do_check() {
    log_info "Running checks..."
    
    # Example checks
    if [[ ! -d "$SCRIPT_DIR" ]]; then
        log_error "Script directory not found"
        return 1
    fi
    
    log_success "All checks passed"
    return 0
}"""
        
        elif operation == "deploy":
            return """# Deploy function
do_deploy() {
    log_info "Starting deployment..."
    
    # Build
    log_info "Building..."
    # Add build commands here
    
    # Deploy
    log_info "Deploying..."
    # Add deploy commands here
    
    log_success "Deployment completed"
    return 0
}"""
        
        elif operation == "cleanup":
            return """# Cleanup function
do_cleanup() {
    log_info "Cleaning up..."
    
    # Remove old backups (keep last 7)
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
        log_success "Cleaned up old backups"
    fi
    
    return 0
}"""
        
        else:  # main/custom
            return """# Main operation
do_main() {
    log_info "Executing main operation..."
    
    # Add your code here
    
    log_success "Operation completed"
    return 0
}"""
    
    def _generate_arg_parser(self) -> str:
        """Generuje parser argumentów"""
        return """# Argument parsing
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

Options:
    -h, --help      Show this help message
    -v, --verbose   Verbose output
    --dry-run       Dry run mode

Examples:
    $SCRIPT_NAME
    $SCRIPT_NAME --verbose
EOF
    exit 0
}

# Parse arguments
VERBOSE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done"""
    
    def _generate_main(self, intent: Dict[str, Any]) -> str:
        """Generuje główną funkcję main"""
        operations = intent["operations"]
        
        main_calls = "\n    ".join([
            f"do_{op} || exit 1" for op in operations
        ])
        
        return f"""# Main function
main() {{
    log_info "Script started"
    
    {main_calls}
    
    log_success "Script completed successfully"
    return 0
}}

# Run main
main "$@"
exit $?"""
    
    def execute(self, text: str) -> ConversionResult:
        """
        Generuje skrypt bash.
        
        Args:
            text: Opis skryptu w języku naturalnym
            
        Returns:
            Wynik z wygenerowanym skryptem
        """
        try:
            # Parse intent
            intent = self.parse_intent(text)
            
            # Generate script
            script = self.generate_command(intent)
            
            return ConversionResult(
                success=True,
                command="Generated bash script",
                output=script,
                metadata={
                    "script_type": intent["script_type"],
                    "operations": intent["operations"],
                    "length": len(script.split("\n"))
                }
            )
            
        except Exception as e:
            logger.error(f"Błąd generowania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def save_script(
        self,
        script: str,
        filepath: str,
        make_executable: bool = True
    ) -> bool:
        """
        Zapisuje skrypt do pliku.
        
        Args:
            script: Zawartość skryptu
            filepath: Ścieżka docelowa
            make_executable: Czy nadać uprawnienia +x
            
        Returns:
            True jeśli sukces
        """
        try:
            path = Path(filepath)
            path.write_text(script)
            
            if make_executable:
                import os
                os.chmod(filepath, 0o755)
            
            logger.info(f"Zapisano skrypt: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd zapisu: {e}")
            return False
