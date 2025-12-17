/**
 * SDK Demo Application Logic
 */

// Store last generated HTML
let lastGeneratedHtml = '';

// Set example command
function setExample(cmd) {
    document.getElementById('command').value = cmd;
}

// Generate HTML
async function generateHtml() {
    const command = document.getElementById('command').value;
    const jsonDataStr = document.getElementById('json-data').value;
    const statusEl = document.getElementById('status');
    const outputEl = document.getElementById('output-code');
    
    if (!command) {
        statusEl.className = 'status error';
        statusEl.textContent = 'Wprowadź komendę';
        return;
    }
    
    statusEl.className = 'status info';
    statusEl.textContent = 'Generowanie...';
    
    try {
        let data = null;
        if (jsonDataStr.trim()) {
            try {
                data = JSON.parse(jsonDataStr);
            } catch (e) {
                statusEl.className = 'status error';
                statusEl.textContent = 'Błąd parsowania JSON: ' + e.message;
                return;
            }
        }
        
        const html = await text2html(command, data);
        lastGeneratedHtml = html;
        
        outputEl.textContent = html;
        statusEl.className = 'status success';
        statusEl.textContent = `✅ Wygenerowano HTML (${html.length} znaków)`;
        
    } catch (error) {
        statusEl.className = 'status error';
        statusEl.textContent = '❌ Błąd: ' + error.message;
        outputEl.textContent = '';
    }
}

// Insert to page
async function insertToPage() {
    if (!lastGeneratedHtml) {
        await generateHtml();
    }
    
    if (lastGeneratedHtml) {
        text2dom("umieść na dole #output-container", lastGeneratedHtml);
        document.getElementById('status').className = 'status success';
        document.getElementById('status').textContent = '✅ HTML wstawiony do strony';
    }
}

// Demo text2dom with data
async function demoText2Dom() {
    const json_data = [
        { name: "Jan Kowalski", age: 25, city: "Warszawa", status: "Active" },
        { name: "Anna Nowak", age: 30, city: "Kraków", status: "Active" },
        { name: "Piotr Wiśniewski", age: 35, city: "Gdańsk", status: "Inactive" }
    ];
    
    // Clear previous content
    const container = document.getElementById('output-container');
    container.innerHTML = '';
    
    // Create table from data and insert
    const tableHtml = dataToTable(json_data, { title: "Lista użytkowników" });
    text2dom("umieść na dole #output-container", tableHtml);
    
    // Also try to generate via API if available
    try {
        const html = await text2html("generate card title: Sukces", { message: "Tabela została wygenerowana!" });
        text2dom("dodaj na górze #output-container", html);
    } catch (e) {
        // Fallback if API not available
        const fallbackCard = `<div style="padding: 1rem; background: #d4edda; border-radius: 4px; margin-bottom: 1rem;">
            <strong>✅ Sukces!</strong> Tabela została wygenerowana z danych JSON.
        </div>`;
        text2dom("dodaj na górze #output-container", fallbackCard);
    }
}

// Demo pipeline
async function demoPipeline() {
    const container = document.getElementById('output-container');
    container.innerHTML = '<p style="color: #666;">Wykonywanie pipeline...</p>';
    
    try {
        const nlp = new NLP2CMD('http://localhost:8001');
        
        const result = await nlp.pipeline([
            { converter: "text2html", command: "generate form for login" },
            { converter: "text3html", command: "add button" }
        ]);
        
        if (result.final_output) {
            container.innerHTML = '';
            text2dom("wstaw do #output-container", result.final_output);
        } else {
            container.innerHTML = '<p style="color: #dc3545;">Pipeline nie zwrócił wyniku</p>';
        }
        
    } catch (error) {
        container.innerHTML = `<p style="color: #dc3545;">Błąd: ${error.message}</p>`;
    }
}

// Clear output
function clearOutput() {
    document.getElementById('output-container').innerHTML = 
        '<p style="color: #999; text-align: center;">← Tutaj pojawi się wygenerowany HTML →</p>';
}

// Demo text4style
async function demoText4Style(command) {
    try {
        await text4style(command, '#style-demo');
    } catch (e) {
        console.error('text4style error:', e);
        text2style(command, '#style-demo');
    }
}

// Reset style demo
function resetStyleDemo() {
    const el = document.getElementById('style-demo');
    if (el) {
        el.removeAttribute('style');
        el.style.padding = '1rem';
        el.style.background = '#f0f0f0';
        el.style.borderRadius = '4px';
        el.style.margin = '1rem 0';
    }
}
