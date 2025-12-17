/**
 * Landing Page Example - Using only text4X service commands
 * 
 * Demonstracja generowania landing page za pomocą:
 * - text4html: generowanie HTML
 * - text4json: generowanie danych JSON
 * - text4dom: wstawianie do DOM
 * - text4style: stylowanie elementów
 */

// Debug logging
const debugPanel = document.createElement('div');
debugPanel.id = 'debug-panel';
document.body.appendChild(debugPanel);

const debugToggle = document.createElement('button');
debugToggle.className = 'debug-toggle';
debugToggle.textContent = '🔧 Debug';
debugToggle.onclick = () => debugPanel.classList.toggle('visible');
document.body.appendChild(debugToggle);

function log(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    debugPanel.appendChild(entry);
    debugPanel.scrollTop = debugPanel.scrollHeight;
    console.log(`[${type}] ${message}`);
}

// App container
const app = document.getElementById('app');

// ============================================================================
// Main: Generate Landing Page using text4X services
// ============================================================================

async function generateLandingPage() {
    log('Starting landing page generation...', 'info');
    
    try {
        // Step 1: Generate page data using API (simulated text4json)
        log('Step 1: Generating page data...', 'info');
        const pageData = await generatePageData();
        log(`Page data ready: ${pageData.title}`, 'success');
        
        // Step 2: Generate hero section
        log('Step 2: Generating hero section...', 'info');
        const heroHtml = await text2html(`generate landing page title: ${pageData.title}`);
        log('Hero section generated', 'success');
        
        // Step 3: Generate features section
        log('Step 3: Generating features cards...', 'info');
        const featuresHtml = await generateFeaturesSection(pageData.features);
        log('Features section generated', 'success');
        
        // Step 4: Generate pricing table
        log('Step 4: Generating pricing table...', 'info');
        const pricingHtml = await generatePricingSection(pageData.pricing);
        log('Pricing section generated', 'success');
        
        // Step 5: Generate testimonials
        log('Step 5: Generating testimonials...', 'info');
        const testimonialsHtml = await generateTestimonialsSection(pageData.testimonials);
        log('Testimonials generated', 'success');
        
        // Step 6: Generate CTA section
        log('Step 6: Generating CTA...', 'info');
        const ctaHtml = await generateCtaSection(pageData);
        log('CTA generated', 'success');
        
        // Step 7: Assemble page using text4dom
        log('Step 7: Assembling page...', 'info');
        app.innerHTML = '';
        
        // Insert all sections
        text2dom("umieść na dole #app", heroHtml);
        text2dom("umieść na dole #app", featuresHtml);
        text2dom("umieść na dole #app", pricingHtml);
        text2dom("umieść na dole #app", testimonialsHtml);
        text2dom("umieść na dole #app", ctaHtml);
        text2dom("umieść na dole #app", generateFooter(pageData));
        
        log('Landing page generated successfully!', 'success');
        
        // Step 8: Apply dynamic styles
        log('Step 8: Applying styles...', 'info');
        await applyDynamicStyles();
        log('Styles applied', 'success');
        
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
        showError(error.message);
    }
}

// ============================================================================
// Data Generation (text4json simulation)
// ============================================================================

async function generatePageData() {
    // In production, this would call text4json API
    // For demo, we return structured data
    return {
        title: "CloudSync Pro",
        subtitle: "Synchronizuj swoje dane w chmurze",
        features: [
            { icon: "🚀", title: "Szybkość", description: "Błyskawiczna synchronizacja plików" },
            { icon: "🔒", title: "Bezpieczeństwo", description: "Szyfrowanie end-to-end" },
            { icon: "📱", title: "Mobilność", description: "Dostęp z każdego urządzenia" },
            { icon: "🔄", title: "Auto-sync", description: "Automatyczna synchronizacja" },
            { icon: "👥", title: "Współpraca", description: "Udostępniaj pliki zespołowi" },
            { icon: "📊", title: "Analityka", description: "Śledź wykorzystanie storage" }
        ],
        pricing: [
            { name: "Starter", price: "0 zł", period: "/miesiąc", features: ["5 GB storage", "2 urządzenia", "Email support"], cta: "Zacznij za darmo", popular: false },
            { name: "Pro", price: "29 zł", period: "/miesiąc", features: ["100 GB storage", "10 urządzeń", "Priority support", "API access"], cta: "Wybierz Pro", popular: true },
            { name: "Enterprise", price: "99 zł", period: "/miesiąc", features: ["Unlimited storage", "Unlimited urządzeń", "24/7 support", "Custom integrations", "SLA"], cta: "Kontakt", popular: false }
        ],
        testimonials: [
            { name: "Anna Kowalska", role: "CEO, TechStart", text: "CloudSync Pro zrewolucjonizował naszą pracę zdalną!", avatar: "👩‍💼" },
            { name: "Piotr Nowak", role: "Developer", text: "Najlepsze narzędzie do synchronizacji kodu.", avatar: "👨‍💻" },
            { name: "Maria Wiśniewska", role: "Designer", text: "Moje projekty zawsze pod ręką.", avatar: "👩‍🎨" }
        ],
        cta: {
            title: "Gotowy na start?",
            subtitle: "Dołącz do 10,000+ zadowolonych użytkowników",
            button: "Rozpocznij za darmo"
        },
        footer: {
            company: "CloudSync Pro",
            year: new Date().getFullYear()
        }
    };
}

// ============================================================================
// Section Generators (text4html)
// ============================================================================

async function generateFeaturesSection(features) {
    const featuresCards = features.map(f => `
        <div class="feature-card">
            <div class="feature-icon">${f.icon}</div>
            <h3>${f.title}</h3>
            <p>${f.description}</p>
        </div>
    `).join('');
    
    return `
    <section class="features-section">
        <div class="container">
            <h2>Funkcje</h2>
            <div class="features-grid">
                ${featuresCards}
            </div>
        </div>
    </section>
    <style>
        .features-section { padding: 4rem 2rem; background: #f8f9fa; }
        .features-section h2 { text-align: center; margin-bottom: 3rem; font-size: 2rem; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; max-width: 1200px; margin: 0 auto; }
        .feature-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; transition: transform 0.2s; }
        .feature-card:hover { transform: translateY(-5px); }
        .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
        .feature-card h3 { margin-bottom: 0.5rem; color: #333; }
        .feature-card p { color: #666; }
    </style>
    `;
}

async function generatePricingSection(pricing) {
    const pricingCards = pricing.map(p => `
        <div class="pricing-card ${p.popular ? 'popular' : ''}">
            ${p.popular ? '<div class="popular-badge">Popularny</div>' : ''}
            <h3>${p.name}</h3>
            <div class="price">${p.price}<span>${p.period}</span></div>
            <ul>
                ${p.features.map(f => `<li>✓ ${f}</li>`).join('')}
            </ul>
            <button class="pricing-cta ${p.popular ? 'primary' : ''}">${p.cta}</button>
        </div>
    `).join('');
    
    return `
    <section class="pricing-section">
        <div class="container">
            <h2>Cennik</h2>
            <div class="pricing-grid">
                ${pricingCards}
            </div>
        </div>
    </section>
    <style>
        .pricing-section { padding: 4rem 2rem; }
        .pricing-section h2 { text-align: center; margin-bottom: 3rem; font-size: 2rem; }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; max-width: 1000px; margin: 0 auto; }
        .pricing-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; position: relative; border: 2px solid transparent; }
        .pricing-card.popular { border-color: #667eea; transform: scale(1.05); }
        .popular-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #667eea; color: white; padding: 0.25rem 1rem; border-radius: 20px; font-size: 0.85rem; }
        .pricing-card h3 { margin-bottom: 1rem; }
        .price { font-size: 2.5rem; font-weight: bold; color: #667eea; margin-bottom: 1.5rem; }
        .price span { font-size: 1rem; color: #666; font-weight: normal; }
        .pricing-card ul { list-style: none; margin-bottom: 2rem; text-align: left; }
        .pricing-card li { padding: 0.5rem 0; border-bottom: 1px solid #eee; }
        .pricing-cta { width: 100%; padding: 1rem; border: 2px solid #667eea; background: white; color: #667eea; border-radius: 8px; cursor: pointer; font-size: 1rem; transition: all 0.2s; }
        .pricing-cta.primary { background: #667eea; color: white; }
        .pricing-cta:hover { background: #5a67d8; color: white; border-color: #5a67d8; }
    </style>
    `;
}

async function generateTestimonialsSection(testimonials) {
    const testimonialCards = testimonials.map(t => `
        <div class="testimonial-card">
            <div class="avatar">${t.avatar}</div>
            <p class="quote">"${t.text}"</p>
            <div class="author">
                <strong>${t.name}</strong>
                <span>${t.role}</span>
            </div>
        </div>
    `).join('');
    
    return `
    <section class="testimonials-section">
        <div class="container">
            <h2>Co mówią nasi użytkownicy</h2>
            <div class="testimonials-grid">
                ${testimonialCards}
            </div>
        </div>
    </section>
    <style>
        .testimonials-section { padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .testimonials-section h2 { text-align: center; margin-bottom: 3rem; font-size: 2rem; }
        .testimonials-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1200px; margin: 0 auto; }
        .testimonial-card { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 12px; backdrop-filter: blur(10px); }
        .avatar { font-size: 3rem; margin-bottom: 1rem; }
        .quote { font-style: italic; margin-bottom: 1rem; opacity: 0.95; }
        .author strong { display: block; }
        .author span { opacity: 0.8; font-size: 0.9rem; }
    </style>
    `;
}

async function generateCtaSection(pageData) {
    return `
    <section class="cta-section">
        <div class="container">
            <h2>${pageData.cta.title}</h2>
            <p>${pageData.cta.subtitle}</p>
            <button class="cta-button">${pageData.cta.button}</button>
        </div>
    </section>
    <style>
        .cta-section { padding: 4rem 2rem; text-align: center; background: #f8f9fa; }
        .cta-section h2 { font-size: 2.5rem; margin-bottom: 1rem; }
        .cta-section p { font-size: 1.25rem; color: #666; margin-bottom: 2rem; }
        .cta-button { padding: 1rem 3rem; font-size: 1.25rem; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
        .cta-button:hover { background: #5a67d8; transform: scale(1.05); }
    </style>
    `;
}

function generateFooter(pageData) {
    return `
    <footer class="footer">
        <div class="container">
            <p>&copy; ${pageData.footer.year} ${pageData.footer.company}. Wygenerowane za pomocą NLP2CMD.</p>
            <p class="tech">Powered by text4html | text4json | text4dom</p>
        </div>
    </footer>
    <style>
        .footer { padding: 2rem; text-align: center; background: #1f2937; color: #9ca3af; }
        .footer .tech { font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.7; }
    </style>
    `;
}

// ============================================================================
// Dynamic Styling (text4style)
// ============================================================================

async function applyDynamicStyles() {
    // Apply hover animations via text4style if available
    try {
        const cards = document.querySelectorAll('.feature-card, .pricing-card, .testimonial-card');
        cards.forEach(card => {
            card.style.transition = 'all 0.3s ease';
        });
    } catch (e) {
        log('Style application skipped', 'info');
    }
}

// ============================================================================
// Error Handling
// ============================================================================

function showError(message) {
    app.innerHTML = `
        <div class="error">
            <h2>⚠️ Błąd generowania</h2>
            <p>${message}</p>
            <button onclick="location.reload()">Spróbuj ponownie</button>
        </div>
    `;
}

// ============================================================================
// Initialize
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    log('DOM loaded, starting generation...', 'info');
    generateLandingPage();
});
