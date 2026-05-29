// ============================================================
// SSEAR - Cliente JavaScript
// Sistema Semántico de Evaluación Automatizada de Respuestas
// ============================================================

const API_URL = (window.location.protocol && window.location.protocol.startsWith('http'))
    ? window.location.origin + '/api'
    : 'http://localhost:5000/api';

const appState = {
    isEvaluating: false,
    lastResults:  null,
    modelReady:   false
};

// ============================================================
// Helper: fetch con timeout y reintentos
// ============================================================
async function fetchWithRetry(url, options = {}, retries = 3, backoff = 500, timeout = 10000) {
    for (let attempt = 0; attempt <= retries; attempt++) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);
        try {
            const response = await fetch(url, { ...options, signal: controller.signal });
            clearTimeout(id);
            return response;
        } catch (err) {
            clearTimeout(id);
            if (attempt === retries) throw err;
            await new Promise(r => setTimeout(r, backoff * Math.pow(2, attempt)));
        }
    }
}

// ============================================================
// Inicialización
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Iniciando SSEAR...');
    await checkServerStatus();
    setupEventListeners();
});

// ============================================================
// Verificación del Servidor
// ============================================================
async function checkServerStatus() {
    try {
        updateStatusBadge('loading', 'Conectando...');
        const response = await fetchWithRetry(`${API_URL}/health`, { method: 'GET' }, 3, 500, 5000);

        if (response.ok) {
            const data = await response.json();
            console.log('Servidor conectado:', data);
            updateStatusBadge('connected', 'Conectado - Listo');
            appState.modelReady = true;
            await getModelsInfo();
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Error conectando con servidor:', error);
        updateStatusBadge('error', 'Error de Conexión');
        showError('No se pudo conectar con el servidor. Asegúrate que app.py está ejecutándose.');
        setTimeout(checkServerStatus, 5000);
    }
}

async function getModelsInfo() {
    try {
        const response = await fetchWithRetry(`${API_URL}/models-info`, { method: 'GET' }, 2, 300, 5000);
        if (response.ok) {
            const data = await response.json();
            console.log('Información de modelos:', data);
        }
    } catch (error) {
        console.error('Error obteniendo info de modelos:', error);
    }
}

function updateStatusBadge(status, message) {
    const badge     = document.getElementById('modelStatus');
    const modeBadge = document.getElementById('modeIndicator');

    if (badge) {
        badge.textContent = message;
        badge.className   = `status-badge ${status}`;
    }

    if (modeBadge) {
        if (status === 'connected') {
            modeBadge.textContent = 'ONLINE';
            modeBadge.className   = 'mode-badge online';
        } else if (status === 'error') {
            modeBadge.textContent = 'OFFLINE';
            modeBadge.className   = 'mode-badge';
        } else {
            modeBadge.textContent = 'PROCESANDO';
            modeBadge.className   = 'mode-badge';
        }
    }
}

// ============================================================
// Event Listeners
// ============================================================
function setupEventListeners() {
    const studentTA = document.getElementById('studentAnswer');
    if (studentTA) {
        studentTA.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') evaluateAnswer();
        });
    }
}

// ============================================================
// Evaluación Principal
// ============================================================
async function evaluateAnswer() {
    if (!appState.modelReady) {
        showError('El servidor aún no está listo. Espera a que se conecte antes de evaluar.');
        return;
    }

    if (appState.isEvaluating) return;

    const question        = (document.getElementById('question')?.value        || '').trim();
    const referenceAnswer = (document.getElementById('referenceAnswer')?.value || '').trim();
    const studentAnswer   = (document.getElementById('studentAnswer')?.value   || '').trim();

    if (!referenceAnswer || !studentAnswer) {
        showError('Por favor ingresa la respuesta de referencia y la respuesta del estudiante.');
        return;
    }

    showLoading(true);
    appState.isEvaluating = true;
    updateStatusBadge('loading', 'Evaluando...');

    try {
        const response = await fetchWithRetry(`${API_URL}/evaluate`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                question,
                reference_answer: referenceAnswer,
                student_answer:   studentAnswer
            })
        }, 2, 500, 30000);

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.error || `HTTP ${response.status}`);
        }

        const result = await response.json();
        console.log('Evaluación completada:', result);

        appState.lastResults = result;
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

// ============================================================
// Mostrar Resultados
// ============================================================
function displayResults(data) {
    const scores   = data.scores   || {};
    const feedback = data.feedback || {};
    const metadata = data.metadata || {};

    const noResults = document.getElementById('noResults');
    const resCont   = document.getElementById('resultsContainer');
    const fbSec     = document.getElementById('feedbackSection');
    const detSec    = document.getElementById('detailsSection');

    if (noResults) noResults.style.display = 'none';
    if (resCont)   resCont.style.display   = 'block';
    if (fbSec)     fbSec.style.display     = 'block';
    if (detSec)    detSec.style.display    = 'block';

    // ---- Puntuaciones ----
    const semanticPct = (scores.semantic ?? 0) * 100;
    const lexicalPct  = (scores.lexical  ?? 0) * 100;
    const overallPct  = scores.percentage ?? scores.overall ?? 0;

    updateScore('semanticScore', semanticPct);
    updateScore('lexicalScore',  lexicalPct);
    updateScore('overallScore',  overallPct);

    updateProgressBar('semanticBar', semanticPct);
    updateProgressBar('lexicalBar',  lexicalPct);
    updateProgressBar('overallBar',  overallPct);

    const overallEl = document.getElementById('overallScore');
if (overallEl) overallEl.textContent = `${overallPct.toFixed(1)}%`;
    // ---- Metadatos ----
    setText('refWordCount', metadata.reference_words ?? metadata.reference_length ?? '—');
    setText('stuWordCount', metadata.student_words   ?? metadata.student_length   ?? '—');
    setText('keywordMatch', metadata.term_coverage   ?? '—');

    // ---- Feedback ----
    displayFeedback(feedback);

    // ---- Análisis Detallado (términos) ----
    displayDetailedAnalysis(metadata);

    // ✅ CORREGIDO: usar analysis_breakdown
    displaySpecificFeedback(feedback.analysis_breakdown || {});
}

// ============================================================
// Feedback
// ============================================================
function displayFeedback(feedback) {
    const summary = feedback.summary || {};

    const summaryContainer = document.getElementById('summaryContainer');
    if (summaryContainer) {
        summaryContainer.innerHTML = `
            <div class="feedback-summary">
                <div class="summary-message">${summary.message ?? ''}</div>
                <div class="summary-encouragement">${summary.encouragement ?? ''}</div>
            </div>
        `;
    }

    displayStrengths(feedback.strengths || []);
    displayWeaknesses(feedback.weaknesses || []);
    displaySuggestions(feedback.suggestions || []);
    displayActionItems(feedback.action_items || []);
}

function displayStrengths(strengths) {
    const container = document.getElementById('strengthsList');
    if (!container) return;
    if (!strengths.length) {
        container.innerHTML = '<p style="color:#999;">Sin fortalezas identificadas</p>';
        return;
    }
    container.innerHTML = strengths.map(s => `
        <div class="list-item">
            <div class="item-description">✅ ${typeof s === 'string' ? s : (s.description || s.title || '')}</div>
        </div>
    `).join('');
}

function displayWeaknesses(weaknesses) {
    const container = document.getElementById('weaknessList');
    if (!container) return;
    if (!weaknesses.length) {
        container.innerHTML = '<p style="color:#999;">Sin áreas de mejora identificadas</p>';
        return;
    }
    container.innerHTML = weaknesses.map(w => `
        <div class="list-item" style="border-left-color: #ef4444;">
            <div class="item-description">⚠️ ${typeof w === 'string' ? w : (w.description || w.title || '')}</div>
        </div>
    `).join('');
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('suggestionsList');
    if (!container) return;
    if (!suggestions.length) {
        container.innerHTML = '<p style="color:#999;">Sin sugerencias disponibles</p>';
        return;
    }
    container.innerHTML = suggestions.map(s => {
        if (typeof s === 'string') return `<div class="suggestion-item">${s}</div>`;
        return `
            <div class="suggestion-item">
                <div class="suggestion-title">${s.area ?? ''}</div>
                <div class="suggestion-description">${s.suggestion ?? ''}</div>
                <span class="priority-badge">${s.priority ?? ''}</span>
            </div>
        `;
    }).join('');
}

function displayActionItems(actions) {
    const container = document.getElementById('actionsList');
    if (!container) return;
    if (!actions.length) {
        container.innerHTML = '<p style="color:#999;">Sin puntos de acción</p>';
        return;
    }
    container.innerHTML = actions.map(action => `
        <div class="action-item" style="border-left-color: #10b981;">
            <div class="action-text">${typeof action === 'string' ? action : (action.action ?? '')}</div>
        </div>
    `).join('');
}

// ============================================================
// Análisis Detallado (términos)
// ============================================================
function displayDetailedAnalysis(metadata) {
    const matchedTerms = metadata.matched_terms || [];
    const missingTerms = metadata.missing_terms || [];
    const extraTerms   = metadata.extra_terms   || [];

    const matchedContainer = document.getElementById('matchedTerms');
    if (matchedContainer) {
        matchedContainer.innerHTML = matchedTerms.length
            ? matchedTerms.map(t => `<span class="term-badge">${t}</span>`).join('')
            : '<p style="color:#999;">Sin términos coincidentes</p>';
    }

    const missingContainer = document.getElementById('missingTerms');
    if (missingContainer) {
        missingContainer.innerHTML = missingTerms.length
            ? missingTerms.map(t => `<span class="term-badge missing">${t}</span>`).join('')
            : '<p style="color:#999;">Todos los términos están presentes</p>';
    }

    const extraContainer = document.getElementById('extraTerms');
    if (extraContainer) {
        extraContainer.innerHTML = extraTerms.length
            ? extraTerms.map(t => `<span class="term-badge extra">+ ${t}</span>`).join('')
            : '<p style="color:#999;">Sin términos extra</p>';
    }
}

// ============================================================
// Análisis Específico ✅ CORREGIDO
// ============================================================
function displaySpecificFeedback(breakdown) {
    const container = document.getElementById('specificFeedback');
    if (!container) return;

    if (!breakdown || Object.keys(breakdown).length === 0) {
        container.innerHTML = '<p style="color:#999;">Sin análisis específico disponible.</p>';
        return;
    }

    const sem = breakdown.semantic || {};
    const lex = breakdown.lexical  || {};

    container.innerHTML = `
        <div class="feedback-item">
            <div class="feedback-score">${(sem.score ?? 0).toFixed(1)}%</div>
            <div class="feedback-label">Análisis Semántico (peso ${sem.weight ?? '85%'})</div>
            <div class="feedback-message">${sem.interpretation ?? ''}</div>
        </div>
        <div class="feedback-item">
            <div class="feedback-score">${(lex.score ?? 0).toFixed(1)}%</div>
            <div class="feedback-label">Análisis Léxico (peso ${lex.weight ?? '15%'})</div>
            <div class="feedback-message">${lex.interpretation ?? ''}</div>
        </div>
    `;
}

// ============================================================
// Utilidades de UI
// ============================================================
function updateScore(id, percentage) {
    const el = document.getElementById(id);
    if (el) el.textContent = `${percentage.toFixed(1)}%`;
}

function updateProgressBar(id, percentage) {
    const el = document.getElementById(id);
    if (el) el.style.width = `${Math.min(percentage, 100)}%`;
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function showLoading(show) {
    const loader = document.getElementById('loadingIndicator');
    if (loader) loader.style.display = show ? 'flex' : 'none';

    const btn = document.getElementById('evaluateBtn');
    if (btn) {
        btn.disabled    = show;
        btn.textContent = show ? 'Evaluando...' : 'Evaluar Respuesta';
    }
}

function showError(message) {
    console.error(message);
    alert(message);
}

function clearAll() {
    if (!confirm('¿Estás seguro de que quieres limpiar todo?')) return;

    ['question', 'referenceAnswer', 'studentAnswer'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    const noResults = document.getElementById('noResults');
    const resCont   = document.getElementById('resultsContainer');
    const fbSec     = document.getElementById('feedbackSection');
    const detSec    = document.getElementById('detailsSection');

    if (noResults) noResults.style.display = 'block';
    if (resCont)   resCont.style.display   = 'none';
    if (fbSec)     fbSec.style.display     = 'none';
    if (detSec)    detSec.style.display    = 'none';

    appState.lastResults = null;
    updateStatusBadge('connected', 'Conectado - Listo');

    const refTA = document.getElementById('referenceAnswer');
    if (refTA) refTA.focus();
}

// ============================================================
// Exportar Resultados
// ============================================================
function exportResults() {
    if (!appState.lastResults) {
        showError('No hay resultados para exportar');
        return;
    }

    const json = JSON.stringify(appState.lastResults, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href     = url;
    link.download = `ssear-results-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
}