/**
 * NLP2CMD JavaScript SDK
 * 
 * Uproszczony klient do generowania i edycji kodu z poziomu przeglądarki.
 * 
 * Nomenklatura:
 * - text2X: GENERATE - tworzy nowy kod z opisu
 * - text3X: EDIT - edytuje istniejący kod
 * - text4X: SERVICE - rozproszona usługa
 * 
 * Użycie:
 *   <script src="nlp2cmd-sdk.js"></script>
 *   <script>
 *     const nlp = new NLP2CMD('http://localhost:8001');
 *     
 *     // Generate HTML
 *     const html = await text2html("generate landing page title: CloudSync");
 *     
 *     // Insert into DOM
 *     text2dom("umieść na dole strony", html);
 *     
 *     // Pipeline
 *     const result = await nlp.pipeline([
 *       { converter: "text2html", command: "generate table" },
 *       { converter: "text3html", command: "add footer" }
 *     ]);
 *   </script>
 */

(function(global) {
    'use strict';

    // =========================================================================
    // Configuration
    // =========================================================================
    
    const DEFAULT_CONFIG = {
        apiUrl: 'http://localhost:8001',
        wsUrl: 'ws://localhost:8001/api/v1/stream',
        timeout: 30000,
        debug: false
    };

    let config = { ...DEFAULT_CONFIG };
    let wsConnection = null;

    // =========================================================================
    // NLP2CMD Main Class
    // =========================================================================

    class NLP2CMD {
        constructor(apiUrl = null, options = {}) {
            this.apiUrl = apiUrl || config.apiUrl;
            this.wsUrl = options.wsUrl || config.wsUrl;
            this.timeout = options.timeout || config.timeout;
            this.debug = options.debug || config.debug;
            this._ws = null;
            this._wsCallbacks = new Map();
            this._requestId = 0;
        }

        // =====================================================================
        // HTTP API Methods
        // =====================================================================

        async _request(endpoint, method = 'GET', body = null) {
            const url = `${this.apiUrl}${endpoint}`;
            
            const options = {
                method,
                headers: { 'Content-Type': 'application/json' }
            };
            
            if (body) {
                options.body = JSON.stringify(body);
            }

            if (this.debug) {
                console.log(`[NLP2CMD] ${method} ${url}`, body);
            }

            try {
                const response = await fetch(url, options);
                const data = await response.json();
                
                if (this.debug) {
                    console.log(`[NLP2CMD] Response:`, data);
                }
                
                return data;
            } catch (error) {
                console.error(`[NLP2CMD] Error:`, error);
                throw error;
            }
        }

        /**
         * Health check
         */
        async health() {
            return this._request('/health');
        }

        /**
         * List available converters
         */
        async converters() {
            return this._request('/api/v1/converters');
        }

        /**
         * Generic convert method
         */
        async convert(converter, command, options = {}) {
            return this._request(`/api/v1/convert/${converter}`, 'POST', {
                command,
                html_content: options.htmlContent || options.html_content,
                context: options.context
            });
        }

        /**
         * Execute pipeline
         */
        async pipeline(steps, name = 'pipeline') {
            return this._request('/api/v1/pipeline', 'POST', {
                name,
                steps: steps.map(s => ({
                    converter: s.converter,
                    command: s.command,
                    config: s.config
                }))
            });
        }

        // =====================================================================
        // WebSocket Methods
        // =====================================================================

        /**
         * Connect to WebSocket for streaming
         */
        async connectWs() {
            return new Promise((resolve, reject) => {
                if (this._ws && this._ws.readyState === WebSocket.OPEN) {
                    resolve(this._ws);
                    return;
                }

                this._ws = new WebSocket(this.wsUrl);
                
                this._ws.onopen = () => {
                    if (this.debug) console.log('[NLP2CMD] WebSocket connected');
                    resolve(this._ws);
                };
                
                this._ws.onerror = (error) => {
                    console.error('[NLP2CMD] WebSocket error:', error);
                    reject(error);
                };
                
                this._ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (this.debug) console.log('[NLP2CMD] WS message:', data);
                    
                    // Emit to callbacks
                    this._wsCallbacks.forEach((callback, id) => {
                        callback(data);
                    });
                };
                
                this._ws.onclose = () => {
                    if (this.debug) console.log('[NLP2CMD] WebSocket closed');
                    this._ws = null;
                };
            });
        }

        /**
         * Send command via WebSocket
         */
        async wsSend(action, command, options = {}) {
            await this.connectWs();
            
            const message = {
                action,
                command,
                ...options
            };
            
            this._ws.send(JSON.stringify(message));
        }

        /**
         * Subscribe to WebSocket messages
         */
        onMessage(callback) {
            const id = ++this._requestId;
            this._wsCallbacks.set(id, callback);
            return () => this._wsCallbacks.delete(id);
        }

        /**
         * Close WebSocket connection
         */
        disconnectWs() {
            if (this._ws) {
                this._ws.close();
                this._ws = null;
            }
        }
    }

    // =========================================================================
    // text2X - GENERATE Functions (create new content)
    // =========================================================================

    /**
     * text2html - Generate HTML from text description
     * @param {string} command - Natural language command
     * @param {object} data - Optional data context (e.g., JSON for tables)
     * @returns {Promise<string>} Generated HTML
     */
    async function text2html(command, data = null) {
        const client = new NLP2CMD(config.apiUrl);
        
        // If data provided, enhance command
        let finalCommand = command;
        if (data) {
            if (typeof data === 'object') {
                finalCommand = `${command} with data: ${JSON.stringify(data)}`;
            }
        }
        
        const result = await client.convert('text2html', finalCommand);
        
        if (result.success) {
            return result.output;
        } else {
            throw new Error(result.error || 'Generation failed');
        }
    }

    /**
     * text2markdown - Generate Markdown from text description
     */
    async function text2markdown(command, data = null) {
        const client = new NLP2CMD(config.apiUrl);
        let finalCommand = command;
        if (data) {
            finalCommand = `${command} with data: ${JSON.stringify(data)}`;
        }
        
        const result = await client.convert('text2markdown', finalCommand);
        return result.success ? result.output : null;
    }

    /**
     * text2svg - Generate SVG from text description
     */
    async function text2svg(command, data = null) {
        const client = new NLP2CMD(config.apiUrl);
        let finalCommand = command;
        if (data) {
            finalCommand = `${command} with data: ${JSON.stringify(data)}`;
        }
        
        const result = await client.convert('text2svg', finalCommand);
        return result.success ? result.output : null;
    }

    /**
     * text2json - Generate JSON structure from text description
     */
    async function text2json(command, schema = null) {
        const client = new NLP2CMD(config.apiUrl);
        let finalCommand = command;
        if (schema) {
            finalCommand = `${command} schema: ${JSON.stringify(schema)}`;
        }
        
        const result = await client.convert('text2json', finalCommand);
        if (result.success) {
            try {
                return JSON.parse(result.output);
            } catch {
                return result.output;
            }
        }
        return null;
    }

    /**
     * text2css - Generate CSS from text description
     */
    async function text2css(command) {
        const client = new NLP2CMD(config.apiUrl);
        const result = await client.convert('text2css', command);
        return result.success ? result.output : null;
    }

    /**
     * text2js - Generate JavaScript from text description
     */
    async function text2js(command) {
        const client = new NLP2CMD(config.apiUrl);
        const result = await client.convert('text2js', command);
        return result.success ? result.output : null;
    }

    // =========================================================================
    // text3X - EDIT Functions (modify existing content)
    // =========================================================================

    /**
     * text3html - Edit existing HTML
     * @param {string} command - Edit command (e.g., "add button to form")
     * @param {string} html - Existing HTML to edit
     * @returns {Promise<string>} Modified HTML
     */
    async function text3html(command, html) {
        const client = new NLP2CMD(config.apiUrl);
        const result = await client.convert('text3html', command, { htmlContent: html });
        
        if (result.success) {
            return result.output;
        } else {
            throw new Error(result.error || 'Edit failed');
        }
    }

    /**
     * text3markdown - Edit existing Markdown
     */
    async function text3markdown(command, markdown) {
        const client = new NLP2CMD(config.apiUrl);
        const result = await client.convert('text3markdown', command, { mdContent: markdown });
        return result.success ? result.output : null;
    }

    /**
     * text3css - Edit existing CSS
     */
    async function text3css(command, css) {
        const client = new NLP2CMD(config.apiUrl);
        const result = await client.convert('text3css', command, { cssContent: css });
        return result.success ? result.output : null;
    }

    // =========================================================================
    // text2dom - DOM Manipulation (special browser-only function)
    // =========================================================================

    /**
     * text2dom - Insert/manipulate HTML in DOM based on natural language
     * @param {string} command - Placement command (e.g., "umieść na dole strony")
     * @param {string|Promise<string>} html - HTML content or Promise returning HTML
     * @param {HTMLElement} container - Optional container element
     * @returns {HTMLElement} Inserted element
     */
    async function text2dom(command, html, container = null) {
        // Resolve HTML if it's a Promise
        const htmlContent = html instanceof Promise ? await html : html;
        
        if (!htmlContent) {
            console.error('[text2dom] No HTML content provided');
            return null;
        }

        // Parse placement command
        const placement = _parsePlacementCommand(command);
        
        // Create element from HTML
        const wrapper = document.createElement('div');
        wrapper.innerHTML = htmlContent;
        const element = wrapper.firstElementChild || wrapper;
        
        // Get target container
        const target = container || placement.target || document.body;
        
        // Insert based on position
        switch (placement.position) {
            case 'start':
            case 'top':
            case 'beginning':
            case 'początek':
            case 'góra':
                target.insertBefore(element, target.firstChild);
                break;
                
            case 'end':
            case 'bottom':
            case 'dół':
            case 'koniec':
            default:
                target.appendChild(element);
                break;
                
            case 'before':
                if (placement.reference) {
                    placement.reference.parentNode.insertBefore(element, placement.reference);
                } else {
                    target.appendChild(element);
                }
                break;
                
            case 'after':
                if (placement.reference) {
                    placement.reference.parentNode.insertBefore(element, placement.reference.nextSibling);
                } else {
                    target.appendChild(element);
                }
                break;
                
            case 'replace':
                if (placement.reference) {
                    placement.reference.parentNode.replaceChild(element, placement.reference);
                } else {
                    target.innerHTML = '';
                    target.appendChild(element);
                }
                break;
        }
        
        // Add animation if specified
        if (placement.animate) {
            element.style.opacity = '0';
            element.style.transition = 'opacity 0.3s ease';
            requestAnimationFrame(() => {
                element.style.opacity = '1';
            });
        }
        
        return element;
    }

    /**
     * Parse natural language placement command
     */
    function _parsePlacementCommand(command) {
        const cmd = command.toLowerCase();
        
        const result = {
            position: 'end',
            target: null,
            reference: null,
            animate: false
        };
        
        // Position detection
        if (/na (dole|końcu)|at (bottom|end)|append/i.test(cmd)) {
            result.position = 'end';
        } else if (/na (górze|początku)|at (top|start|beginning)|prepend/i.test(cmd)) {
            result.position = 'start';
        } else if (/przed|before/i.test(cmd)) {
            result.position = 'before';
        } else if (/po|za|after/i.test(cmd)) {
            result.position = 'after';
        } else if (/zastąp|replace/i.test(cmd)) {
            result.position = 'replace';
        }
        
        // Target detection
        const selectorMatch = cmd.match(/(w|in|do|into)\s+([#.\w-]+)/i);
        if (selectorMatch) {
            const selector = selectorMatch[2];
            result.target = document.querySelector(selector) || 
                           document.querySelector(`#${selector}`) ||
                           document.querySelector(`.${selector}`);
        }
        
        // Element name detection
        if (/body|strony|page/i.test(cmd)) {
            result.target = document.body;
        } else if (/header|nagłówk/i.test(cmd)) {
            result.target = document.querySelector('header') || document.body;
        } else if (/footer|stopk/i.test(cmd)) {
            result.target = document.querySelector('footer') || document.body;
        } else if (/main|główn/i.test(cmd)) {
            result.target = document.querySelector('main') || document.body;
        }
        
        // Animation
        if (/animat|płynnie|smooth/i.test(cmd)) {
            result.animate = true;
        }
        
        return result;
    }

    /**
     * text4style - SERVICE: LLM-based styling via API
     * @param {string} command - Natural language style command
     * @param {HTMLElement|string} element - Element or selector
     * @returns {Promise<HTMLElement>} Styled element
     */
    async function text4style(command, element) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) {
            console.warn(`[text4style] Element not found: ${element}`);
            return null;
        }

        try {
            const client = new NLP2CMD(config.apiUrl);
            const response = await client._request('/api/v1/style', 'POST', { command });
            
            if (response.success && response.styles) {
                // Apply styles
                for (const [prop, value] of Object.entries(response.styles)) {
                    el.style[prop] = value;
                }
                
                // Inject animations if needed
                if (response.animations && response.animations.length > 0) {
                    let styleEl = document.getElementById('nlp2cmd-dynamic-styles');
                    if (!styleEl) {
                        styleEl = document.createElement('style');
                        styleEl.id = 'nlp2cmd-dynamic-styles';
                        document.head.appendChild(styleEl);
                    }
                    
                    for (const anim of response.animations) {
                        if (!styleEl.textContent.includes(anim.name)) {
                            styleEl.textContent += anim.keyframes + '\n';
                        }
                    }
                }
                
                // Apply hover effects
                if (response.hover && Object.keys(response.hover).length > 0) {
                    const originalStyles = {};
                    
                    el.addEventListener('mouseenter', () => {
                        for (const [prop, value] of Object.entries(response.hover)) {
                            originalStyles[prop] = el.style[prop];
                            el.style[prop] = value;
                        }
                    });
                    
                    el.addEventListener('mouseleave', () => {
                        for (const [prop, value] of Object.entries(originalStyles)) {
                            el.style[prop] = value;
                        }
                    });
                }
                
                console.log(`[text4style] Applied styles:`, response.styles);
                return el;
            }
        } catch (error) {
            console.warn(`[text4style] API error, falling back to local: ${error.message}`);
            // Fallback to local text2style
            return text2style(command, el);
        }
        
        return el;
    }

    /**
     * text2style - Apply styles to element based on natural language (local fallback)
     * @param {string} command - Style command (e.g., "make it red and bold")
     * @param {HTMLElement|string} element - Element or selector
     */
    function text2style(command, element) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) {
            console.warn(`[text2style] Element not found: ${element}`);
            return null;
        }
        
        const cmd = command.toLowerCase();
        
        // Colors - detect if background or text color
        const colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'black', 'white', 'gray', 'cyan', 'magenta'];
        const isBackground = /background|tło|bg/i.test(cmd);
        
        for (const color of colors) {
            if (cmd.includes(color)) {
                if (isBackground) {
                    el.style.backgroundColor = color;
                    // Auto white text on dark backgrounds
                    if (['blue', 'purple', 'black', 'green', 'red'].includes(color)) {
                        el.style.color = 'white';
                    }
                } else {
                    el.style.color = color;
                }
            }
        }
        
        // Text styles
        if (/bold|pogrub/i.test(cmd)) el.style.fontWeight = 'bold';
        if (/italic|kursyw/i.test(cmd)) el.style.fontStyle = 'italic';
        if (/underline|podkreśl/i.test(cmd)) el.style.textDecoration = 'underline';
        if (/center|wyśrodkuj|środek/i.test(cmd)) el.style.textAlign = 'center';
        
        // Size
        const sizeMatch = cmd.match(/(\d+)(px|em|rem|%)/);
        if (sizeMatch) {
            el.style.fontSize = sizeMatch[0];
        }
        if (/big|duż|larger/i.test(cmd)) el.style.fontSize = '1.5em';
        if (/small|mał|smaller/i.test(cmd)) el.style.fontSize = '0.8em';
        
        // Display
        if (/hide|ukryj|schowaj/i.test(cmd)) el.style.display = 'none';
        if (/show|pokaż/i.test(cmd)) el.style.display = '';
        
        // Spacing
        if (/padding|wypełnienie/i.test(cmd)) {
            const paddingMatch = cmd.match(/padding[:\s]+(\d+)/);
            el.style.padding = paddingMatch ? `${paddingMatch[1]}px` : '1rem';
        }
        if (/margin|margines/i.test(cmd)) {
            const marginMatch = cmd.match(/margin[:\s]+(\d+)/);
            el.style.margin = marginMatch ? `${marginMatch[1]}px` : '1rem';
        }
        
        // Transparency/Opacity
        const opacityMatch = cmd.match(/(?:transparent|opacity|przezroczyst)[:\s]*(\d+)%?/i);
        if (opacityMatch) {
            const value = parseInt(opacityMatch[1]);
            el.style.opacity = value > 1 ? value / 100 : value;
        }
        
        // Blinking/Animation
        if (/blink|migaj|mrugaj|pulse|pulsuj/i.test(cmd)) {
            // Inject keyframes if not exists
            if (!document.getElementById('nlp2cmd-animations')) {
                const style = document.createElement('style');
                style.id = 'nlp2cmd-animations';
                style.textContent = `
                    @keyframes nlp2cmd-blink {
                        0%, 50% { opacity: 1; }
                        25%, 75% { opacity: 0.3; }
                    }
                    @keyframes nlp2cmd-pulse {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                    }
                    @keyframes nlp2cmd-color-blink {
                        0%, 100% { filter: hue-rotate(0deg); }
                        50% { filter: hue-rotate(180deg); }
                    }
                `;
                document.head.appendChild(style);
            }
            el.style.animation = 'nlp2cmd-blink 1s infinite';
        }
        
        // Rotation
        const rotateMatch = cmd.match(/(?:rotate|obróć)[:\s]*(-?\d+)/i);
        if (rotateMatch) {
            el.style.transform = `rotate(${rotateMatch[1]}deg)`;
        }
        
        // Border radius
        if (/round|zaokrągl/i.test(cmd)) {
            const radiusMatch = cmd.match(/(?:round|radius|zaokrągl)[:\s]*(\d+)/i);
            el.style.borderRadius = radiusMatch ? `${radiusMatch[1]}px` : '8px';
        }
        
        // Shadow
        if (/shadow|cień/i.test(cmd)) {
            el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
        }
        
        return el;
    }

    /**
     * text2query - Query DOM elements with natural language
     * @param {string} command - Query command (e.g., "find all buttons")
     * @returns {NodeList|Element}
     */
    function text2query(command) {
        const cmd = command.toLowerCase();
        
        // Direct selectors
        const selectorMatch = cmd.match(/[#.][a-z0-9_-]+/i);
        if (selectorMatch) {
            return document.querySelectorAll(selectorMatch[0]);
        }
        
        // Element types
        const elements = ['button', 'input', 'form', 'table', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'a', 'img', 'ul', 'li'];
        for (const el of elements) {
            if (cmd.includes(el)) {
                return document.querySelectorAll(el);
            }
        }
        
        // Polish names
        if (/przycisk/i.test(cmd)) return document.querySelectorAll('button');
        if (/formularz/i.test(cmd)) return document.querySelectorAll('form');
        if (/tabela/i.test(cmd)) return document.querySelectorAll('table');
        if (/obrazek|obraz/i.test(cmd)) return document.querySelectorAll('img');
        if (/link/i.test(cmd)) return document.querySelectorAll('a');
        
        // Attributes
        if (/with class|z klasą/i.test(cmd)) {
            const classMatch = cmd.match(/(?:class|klasą)[:\s]+["\']?([^"'\s]+)/i);
            if (classMatch) return document.querySelectorAll(`.${classMatch[1]}`);
        }
        
        if (/with id|z id/i.test(cmd)) {
            const idMatch = cmd.match(/(?:id)[:\s]+["\']?([^"'\s]+)/i);
            if (idMatch) return document.getElementById(idMatch[1]);
        }
        
        return document.querySelectorAll('*');
    }

    // =========================================================================
    // Utility Functions
    // =========================================================================

    /**
     * Configure SDK
     */
    function configure(options) {
        config = { ...config, ...options };
    }

    /**
     * Create table HTML from data
     */
    function dataToTable(data, options = {}) {
        if (!Array.isArray(data) || data.length === 0) {
            return '<table><tr><td>No data</td></tr></table>';
        }
        
        const headers = Object.keys(data[0]);
        const title = options.title || '';
        
        let html = '<table class="nlp2cmd-table">';
        
        if (title) {
            html += `<caption>${title}</caption>`;
        }
        
        html += '<thead><tr>';
        for (const h of headers) {
            html += `<th>${h}</th>`;
        }
        html += '</tr></thead><tbody>';
        
        for (const row of data) {
            html += '<tr>';
            for (const h of headers) {
                html += `<td>${row[h] ?? ''}</td>`;
            }
            html += '</tr>';
        }
        
        html += '</tbody></table>';
        
        // Add default styles
        if (!document.getElementById('nlp2cmd-table-styles')) {
            const style = document.createElement('style');
            style.id = 'nlp2cmd-table-styles';
            style.textContent = `
                .nlp2cmd-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
                .nlp2cmd-table th, .nlp2cmd-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }
                .nlp2cmd-table th { background: #f8f9fa; font-weight: 600; }
                .nlp2cmd-table tr:hover { background: #f8f9fa; }
                .nlp2cmd-table caption { font-weight: bold; margin-bottom: 0.5rem; }
            `;
            document.head.appendChild(style);
        }
        
        return html;
    }

    /**
     * Create list HTML from data
     */
    function dataToList(data, options = {}) {
        const type = options.ordered ? 'ol' : 'ul';
        let html = `<${type} class="nlp2cmd-list">`;
        
        for (const item of data) {
            if (typeof item === 'object') {
                html += `<li>${JSON.stringify(item)}</li>`;
            } else {
                html += `<li>${item}</li>`;
            }
        }
        
        html += `</${type}>`;
        return html;
    }

    // =========================================================================
    // Export to global scope
    // =========================================================================

    // Main class
    global.NLP2CMD = NLP2CMD;
    
    // Configure
    global.nlp2cmdConfig = configure;
    
    // text2X - GENERATE functions
    global.text2html = text2html;
    global.text2markdown = text2markdown;
    global.text2svg = text2svg;
    global.text2json = text2json;
    global.text2css = text2css;
    global.text2js = text2js;
    
    // text3X - EDIT functions
    global.text3html = text3html;
    global.text3markdown = text3markdown;
    global.text3css = text3css;
    
    // DOM functions
    global.text2dom = text2dom;
    global.text2style = text2style;  // Local regex-based (fallback)
    global.text4style = text4style;  // SERVICE - LLM-based via API
    global.text2query = text2query;
    
    // Utilities
    global.dataToTable = dataToTable;
    global.dataToList = dataToList;

    // Auto-configure from data attribute
    document.addEventListener('DOMContentLoaded', () => {
        const script = document.querySelector('script[data-nlp2cmd-api]');
        if (script) {
            const apiUrl = script.getAttribute('data-nlp2cmd-api');
            if (apiUrl) {
                configure({ apiUrl });
                console.log(`[NLP2CMD] Configured API: ${apiUrl}`);
            }
        }
    });

    console.log('[NLP2CMD] SDK loaded. Available functions: text2html, text2dom, text3html, text2style, text2query');

})(typeof window !== 'undefined' ? window : global);
