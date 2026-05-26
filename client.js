/**
 * SSEAR - Cliente JavaScript
 * Interfaz con el backend Flask
 */

// Prefer same-origin API when served from HTTP(S); fallback to localhost when opened via file://
const API_URL = (window.location.protocol && window.location.protocol.startsWith('http'))
    ? window.location.origin + '/api'
    : 'http://localhost:5000/api';

// Estado de la aplicación
const appState = {
    isEvaluating: false,
    lastResults: null,
    modelReady: false
};

// Helper: fetch with timeout + retries (exponential backoff)
async function fetchWithRetry(url, options = {}, retries = 3, backoff = 500, timeout = 5000) {
    for (let attempt = 0; attempt <= retries; attempt++) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);
        try {
            const response = await fetch(url, { ...options, signal: controller.signal });
            clearTimeout(id);
            if (!response.ok && attempt < retries) {
                await new Promise(r => setTimeout(r, backoff * Math.pow(2, attempt)));
                continue;
            }
            return response;
        } catch (err) {
            clearTimeout(id);
            if (attempt < retries) {
                await new Promise(r => setTimeout(r, backoff * Math.pow(2, attempt)));
                continue;
            }
            throw err;
        }
    }
}

// ============================================
// Inicialización
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Iniciando SSEAR...');
    await checkServerStatus();
    setupEventListeners();
});

// ============================================
// Verificación del Servidor
// ============================================

async function checkServerStatus() {
    try {
        console.log('Verificando conexión con servidor...');
        const response = await fetchWithRetry(`${API_URL}/health`, { method: 'GET' }, 3, 500, 5000);

        if (response.ok) {
            const data = await response.json();
            console.log('Servidor conectado:', data);
            updateStatusBadge('connected', 'Conectado');
            appState.modelReady = true;
            
            // Obtener información de modelos
            await getModelsInfo();
        }
    } catch (error) {
        console.error('Error conectando con servidor:', error);
        updateStatusBadge('error', 'Error de Conexión');
        showError('No se pudo conectar con el servidor. Asegúrate que el servidor está corriendo y accesible');
    }
}

async function getModelsInfo() {
    try {
        const response = await fetchWithRetry(`${API_URL}/models-info`, { method: 'GET' }, 2, 300, 5000);
        const data = response.ok ? await response.json() : null;
        console.log('Información de modelos:', data);
    } catch (error) {
        console.error('Error obteniendo info de modelos:', error);
    }
}

function updateStatusBadge(status, message) {
    const badge = document.getElementById('modelStatus');
    badge.textContent = message;
    badge.className = `status-badge ${status}`;
    
    if (status === 'connected') {
        badge.textContent = 'Conectado - Listo';
    } else if (status === 'error') {
        badge.textContent = 'Error: ' + message;
    } else if (status === 'loading') {
        badge.textContent = message;
    }
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Enter en textareas (Ctrl+Enter para evaluar)
    document.getElementById('studentAnswer').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            evaluateAnswer();
        }
    });

    // Tecla Escape para limpiar
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // Puedes agregar acción aquí si lo deseas
        }
    });
}

// ============================================
// Funciones Principales
// ============================================

async function evaluateAnswer() {
    if (!appState.modelReady) {
        showError('El servidor aún no está listo. Espera a que se conecte antes de evaluar.');
        return;
    }
    const referenceAnswer = document.getElementById('referenceAnswer').value.trim();
    const studentAnswer = document.getElementById('studentAnswer').value.trim();
    const question = document.getElementById('question').value.trim();

    // Validaciones
    if (!referenceAnswer || !studentAnswer || !question) {
        showError('Por favor completa la pregunta, la respuesta de referencia y la respuesta del estudiante');
        return;
    }

    // Mostrar indicador de carga
    showLoading(true);
    appState.isEvaluating = true;
    updateStatusBadge('loading', 'Evaluando...');

    try {
        const response = await fetchWithRetry(`${API_URL}/evaluate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                reference_answer: referenceAnswer,
                student_answer: studentAnswer,
                question: question
            })
        }, 2, 500, 10000);

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const result = await response.json();
        
        console.log('Evaluación completada:', result);
        
        // Guardar resultados
        appState.lastResults = result;
        
        // Mostrar resultados
        displayResults(result);
        
        updateStatusBadge('connected', 'Evaluación Completada');

    } catch (error) {
        console.error('Error en evaluación:', error);
        showError(`Error evaluando respuesta: ${error.message}`);
        updateStatusBadge('error', 'Error en Evaluación');
    } finally {
        showLoading(false);
        appState.isEvaluating = false;
    }
}

// ============================================
// Mostrar Resultados
// ============================================

function displayResults(data) {
    const scores = data.scores;
    const analysis = data.analysis;
    const feedback = data.feedback;
    const metadata = data.metadata;

    // Mostrar/ocultar secciones
    document.getElementById('noResults').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';
    document.getElementById('feedbackSection').style.display = 'block';
    document.getElementById('detailsSection').style.display = 'block';

    // ===== Actualizar Puntuaciones =====
    updateScore('semanticScore', scores.semantic);
    updateScore('lexicalScore', scores.lexical);
    updateScore('overallScore', scores.overall);

    updateProgressBar('semanticBar', scores.semantic);
    updateProgressBar('lexicalBar', scores.lexical);
    updateProgressBar('overallBar', scores.overall);

    // ===== Actualizar Metadatos =====
    document.getElementById('refWordCount').textContent = metadata.reference_words;
    document.getElementById('stuWordCount').textContent = metadata.student_words;
    document.getElementById('keywordMatch').textContent = 
        ((metadata.matched_terms.length / (metadata.reference_words || 1)) * 100).toFixed(1) + '%';

    // ===== Feedback Personalizado =====
    displayFeedback(feedback);

    // ===== Análisis Detallado =====
    displayDetailedAnalysis(metadata);

    // Scroll hacia resultados
    setTimeout(() => {
        document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
    }, 300);
}

function updateScore(elementId, score) {
    const element = document.getElementById(elementId);
    element.textContent = score.toFixed(1) + '%';
    
    // Agregar color según puntuación
    element.style.color = getScoreColor(score);
}

function updateProgressBar(elementId, score) {
    const element = document.getElementById(elementId);
    element.style.width = score + '%';
}

function getScoreColor(score) {
    if (score >= 80) return '#10b981';      // Verde
    if (score >= 60) return '#f59e0b';      // Naranja
    if (score >= 40) return '#ef4444';      // Rojo claro
    return '#ef4444';                       // Rojo
}

// ============================================
// Mostrar Retroalimentación
// ============================================

function displayFeedback(feedback) {
    // Summary
    const summary = feedback.summary;
    const summaryContainer = document.getElementById('summaryContainer');
    summaryContainer.innerHTML = `
        <div class="feedback-summary">
            <div class="summary-rating">${summary.rating}</div>
            <div class="summary-message">${summary.message}</div>
        </div>
    `;

    // Strengths
    displayStrengths(feedback.strengths);

    // Weaknesses
    displayWeaknesses(feedback.weaknesses);

    // Suggestions
    displaySuggestions(feedback.suggestions);

    // Action Items
    displayActionItems(feedback.action_items);
}

function displayStrengths(strengths) {
    const container = document.getElementById('strengthsList');
    container.innerHTML = strengths.map(strength => `
        <div class="list-item">
            <div class="item-title">
                ${strength.title}
                ${strength.score !== undefined ? `<span class="item-score">${strength.score.toFixed(1)}%</span>` : ''}
            </div>
                <div class="item-description">${strength.description}</div>
        </div>
    `).join('');
}

function displayWeaknesses(weaknesses) {
    const container = document.getElementById('weaknessList');
    container.innerHTML = weaknesses.map(weakness => `
        <div class="list-item" style="border-left-color: #ef4444;">
            <div class="item-title">
                ${weakness.title}
                ${weakness.score !== undefined ? `<span class="item-score" style="background: #ef4444;">${weakness.score.toFixed(1)}%</span>` : ''}
            </div>
            <div class="item-description">${weakness.description}</div>
            ${weakness.count ? `<div class="item-description">${weakness.count} elementos</div>` : ''}
            ${weakness.severity ? `<span class="priority-badge ${weakness.severity}">Severidad: ${weakness.severity}</span>` : ''}
        </div>
    `).join('');
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('suggestionsList');
    container.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item">
            <div class="suggestion-title">${suggestion.title}</div>
            <div class="suggestion-description">${suggestion.description}</div>
            <span class="priority-badge ${suggestion.priority}">Prioridad: ${suggestion.priority}</span>
        </div>
    `).join('');
}

function displayActionItems(actions) {
    const container = document.getElementById('actionsList');
    container.innerHTML = actions.map((action, index) => `
        <div class="action-item" style="border-left-color: #10b981;">
            <div class="action-text">
                <strong>${action.priority}.</strong> ${action.action}
            </div>
        </div>
    `).join('');
}

// ============================================
// Análisis Detallado
// ============================================

function displayDetailedAnalysis(metadata) {
    // Términos Encontrados
    const matchedContainer = document.getElementById('matchedTerms');
    matchedContainer.innerHTML = metadata.matched_terms.length > 0 
        ? metadata.matched_terms.map(term => `<span class="term-badge">${term}</span>`).join('')
        : '<p style="color: #999;">Sin términos coincidentes</p>';

    // Términos Faltantes
    const missingContainer = document.getElementById('missingTerms');
    missingContainer.innerHTML = metadata.missing_terms.length > 0
        ? metadata.missing_terms.map(term => `<span class="term-badge missing">${term}</span>`).join('')
        : '<p style="color: #999;">Todos los términos están presentes</p>';

    // Términos Extra
    const extraContainer = document.getElementById('extraTerms');
    extraContainer.innerHTML = metadata.extra_terms.length > 0
        ? metadata.extra_terms.map(term => `<span class="term-badge extra">+ ${term}</span>`).join('')
        : '<p style="color: #999;">Sin términos extra</p>';

    // Análisis Específicos
    displaySpecificFeedback(appState.lastResults.feedback.specific_feedback);
}

function displaySpecificFeedback(specificFeedback) {
    const container = document.getElementById('specificFeedback');
    
    container.innerHTML = `
        <div class="feedback-item">
            <div class="feedback-score">${specificFeedback.semantic_analysis.score.toFixed(1)}%</div>
            <div class="feedback-label">Análisis Semántico</div>
            <div class="feedback-message">${specificFeedback.semantic_analysis.message}</div>
            <div style="font-size: 0.85rem; margin-top: 8px; color: #666;">
                ${specificFeedback.semantic_analysis.details}
            </div>
        </div>
        <div class="feedback-item">
            <div class="feedback-score">${specificFeedback.lexical_analysis.score.toFixed(1)}%</div>
            <div class="feedback-label">Análisis Léxico</div>
            <div class="feedback-message">${specificFeedback.lexical_analysis.message}</div>
            <div style="font-size: 0.85rem; margin-top: 8px; color: #666;">
                ${specificFeedback.lexical_analysis.details}
            </div>
        </div>
    `;
}

// ============================================
// Utilidades
// ============================================

function clearAll() {
    if (!confirm('¿Estás seguro de que quieres limpiar todo?')) return;

    document.getElementById('referenceAnswer').value = '';
    document.getElementById('studentAnswer').value = '';
    document.getElementById('question').value = '';

    document.getElementById('noResults').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('feedbackSection').style.display = 'none';
    document.getElementById('detailsSection').style.display = 'none';

    appState.lastResults = null;
    updateStatusBadge('connected', 'Conectado - Listo');

    document.getElementById('referenceAnswer').focus();
}

function showLoading(show) {
    document.getElementById('loadingIndicator').style.display = show ? 'flex' : 'none';
}

function showError(message) {
    // Crear notificación de error
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.innerHTML = `
        <div style="
            background: #fee2e2;
            color: #991b1b;
            padding: 16px 20px;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: slideInDown 0.3s ease;
        ">
            
            <span>${message}</span>
        </div>
    `;

    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(notification, mainContent.firstChild);

    // Auto eliminar después de 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideInUp 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// ============================================
// Exportar Resultados (opcional)
// ============================================

function exportResults() {
    if (!appState.lastResults) {
        showError('No hay resultados para exportar');
        return;
    }

    const json = JSON.stringify(appState.lastResults, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ssear-results-${Date.now()}.json`;
    link.click();
}

// ============================================
// Debug
// ============================================

console.log('Cliente SSEAR cargado');
