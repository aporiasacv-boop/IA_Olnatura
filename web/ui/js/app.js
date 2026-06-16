(function () {
  'use strict';

  const STORAGE_KEY = 'olnatura_assistant_history';
  const MAX_HISTORY = 20;
  const API_ENDPOINT = '/assistant';

  const questionInput = document.getElementById('question-input');
  const askButton = document.getElementById('ask-button');
  const charCount = document.getElementById('char-count');
  const errorAlert = document.getElementById('error-alert');
  const errorMessage = document.getElementById('error-message');
  const loadingState = document.getElementById('loading-state');
  const responseSection = document.getElementById('response-section');
  const sourceBadge = document.getElementById('source-badge');
  const responseTime = document.getElementById('response-time');
  const answerText = document.getElementById('answer-text');
  const historyList = document.getElementById('history-list');
  const historyEmpty = document.getElementById('history-empty');
  const clearHistoryButton = document.getElementById('clear-history-button');

  const SOURCE_LABELS = {
    analytics: 'Analytics',
    documents: 'Documentos',
    hybrid: 'Híbrido',
  };

  function loadHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function saveHistory(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items.slice(0, MAX_HISTORY)));
  }

  function formatTimestamp(iso) {
    const date = new Date(iso);
    return date.toLocaleString('es-MX', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function formatDuration(ms) {
    if (ms < 1000) {
      return Math.round(ms) + ' ms';
    }
    return (ms / 1000).toFixed(2) + ' s';
  }

  function hideError() {
    errorAlert.classList.add('d-none');
    errorMessage.textContent = '';
  }

  function showError(message) {
    errorMessage.textContent = message;
    errorAlert.classList.remove('d-none');
    responseSection.classList.add('d-none');
  }

  function setLoading(isLoading) {
    askButton.disabled = isLoading;
    loadingState.classList.toggle('d-none', !isLoading);
    if (isLoading) {
      responseSection.classList.add('d-none');
      hideError();
    }
  }

  function applySourceBadge(source) {
    const label = SOURCE_LABELS[source] || source;
    sourceBadge.textContent = label;
    sourceBadge.className = 'badge rounded-pill badge-source-' + (SOURCE_LABELS[source] ? source : 'unknown');
  }

  function showResponse(data, elapsedMs) {
    applySourceBadge(data.source);
    responseTime.textContent = formatDuration(elapsedMs);
    answerText.textContent = data.answer || '';
    responseSection.classList.remove('d-none');
  }

  function renderHistory() {
    const items = loadHistory();
    historyList.innerHTML = '';
    historyEmpty.classList.toggle('d-none', items.length > 0);

    items.forEach(function (item, index) {
      const li = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'history-item w-100 text-start border-0';
      button.setAttribute('aria-label', 'Recuperar consulta: ' + item.question);

      const questionEl = document.createElement('div');
      questionEl.className = 'history-item-question';
      questionEl.textContent = item.question;

      const metaEl = document.createElement('div');
      metaEl.className = 'history-item-meta';
      metaEl.textContent =
        (SOURCE_LABELS[item.source] || item.source) +
        ' · ' +
        formatDuration(item.responseTimeMs) +
        ' · ' +
        formatTimestamp(item.timestamp);

      button.appendChild(questionEl);
      button.appendChild(metaEl);
      button.addEventListener('click', function () {
        questionInput.value = item.question;
        updateCharCount();
        showResponse({ source: item.source, answer: item.answer }, item.responseTimeMs);
        hideError();
      });

      li.appendChild(button);
      historyList.appendChild(li);
    });
  }

  function addToHistory(entry) {
    const items = loadHistory();
    items.unshift(entry);
    saveHistory(items);
    renderHistory();
  }

  function updateCharCount() {
    const length = questionInput.value.length;
    charCount.textContent = length + ' / 2000';
  }

  function parseErrorResponse(status, body) {
    if (body && typeof body.detail === 'string') {
      return body.detail;
    }
    if (body && Array.isArray(body.detail)) {
      return body.detail.map(function (item) {
        return item.msg || JSON.stringify(item);
      }).join('. ');
    }
    if (status === 503) {
      return 'El servicio de IA no está disponible. Verifica que Ollama esté en ejecución.';
    }
    if (status === 422) {
      return 'La pregunta no es válida. Escribe al menos un carácter.';
    }
    if (status === 404) {
      return 'No se encontró el endpoint del asistente. Verifica la configuración del servidor.';
    }
    return 'Error del servidor (código ' + status + ').';
  }

  async function askAssistant() {
    const question = questionInput.value.trim();
    if (!question) {
      showError('Escribe una pregunta antes de consultar.');
      questionInput.focus();
      return;
    }

    setLoading(true);
    const startedAt = performance.now();

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question }),
      });

      const elapsedMs = performance.now() - startedAt;
      let body = null;

      try {
        body = await response.json();
      } catch {
        body = null;
      }

      if (!response.ok) {
        showError(parseErrorResponse(response.status, body));
        return;
      }

      showResponse(body, elapsedMs);
      addToHistory({
        question: question,
        source: body.source,
        answer: body.answer,
        responseTimeMs: elapsedMs,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      showError(
        'No se pudo conectar con la API. Verifica que el backend esté activo y que accedas al portal desde el mismo origen (ej. /ui).'
      );
    } finally {
      setLoading(false);
    }
  }

  questionInput.addEventListener('input', updateCharCount);
  questionInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      askAssistant();
    }
  });
  askButton.addEventListener('click', askAssistant);
  clearHistoryButton.addEventListener('click', function () {
    localStorage.removeItem(STORAGE_KEY);
    renderHistory();
  });

  updateCharCount();
  renderHistory();
})();
