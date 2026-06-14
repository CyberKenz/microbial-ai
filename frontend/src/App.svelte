<script>
  import { onMount } from 'svelte';
  import ImageUploader from './lib/ImageUploader.svelte';
  import CameraCapture from './lib/CameraCapture.svelte';
  import CfuSettings from './lib/CfuSettings.svelte';
  import ResultsView from './lib/ResultsView.svelte';
  import { checkHealth, predictImage, predictAnnotated, calculateCfu, fetchCfuDefaults } from './lib/api.js';

  let file = null;
  let previewUrl = null;
  let results = null;
  let annotatedUrl = null;
  let loading = false;
  let error = null;
  let apiStatus = null;
  let uploader;
  let camera;

  let inputSource = 'upload';
  let cfuEnabled = true;
  let volumePlated = 0.1;
  let dilutionFactor = 0.00001;
  let showCfuSettings = true;

  onMount(async () => {
    try {
      apiStatus = await checkHealth();
    } catch (e) {
      apiStatus = { status: 'unreachable', error: e.message };
    }

    try {
      const defaults = await fetchCfuDefaults();
      volumePlated = defaults.default_volume_plated_ml;
      dilutionFactor = defaults.default_dilution_factor;
    } catch (e) {
      // Use local defaults
    }
  });

  async function analyze() {
    if (!file) return;
    loading = true;
    error = null;
    results = null;

    if (annotatedUrl) {
      URL.revokeObjectURL(annotatedUrl);
      annotatedUrl = null;
    }

    try {
      if (cfuEnabled) {
        const [cfuResult, annotatedBlobUrl] = await Promise.all([
          calculateCfu(file, volumePlated, dilutionFactor),
          predictAnnotated(file),
        ]);
        results = cfuResult;
        annotatedUrl = annotatedBlobUrl;
      } else {
        const [jsonResult, annotatedBlobUrl] = await Promise.all([
          predictImage(file),
          predictAnnotated(file),
        ]);
        results = jsonResult;
        annotatedUrl = annotatedBlobUrl;
      }
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function reset() {
    if (inputSource === 'upload') {
      uploader.reset();
    } else {
      camera.reset();
    }
    file = null;
    previewUrl = null;
    results = null;
    error = null;
    if (annotatedUrl) {
      URL.revokeObjectURL(annotatedUrl);
      annotatedUrl = null;
    }
  }

  $: apiOnline = apiStatus?.status === 'healthy';
</script>

<div class="app">
  <!-- Background decoration -->
  <div class="bg-deco">
    <div class="bg-circle bg-circle-1"></div>
    <div class="bg-circle bg-circle-2"></div>
    <div class="bg-circle bg-circle-3"></div>
  </div>

  <header>
    <div class="header-icon">
      <svg width="32" height="32" viewBox="0 0 100 100" fill="none">
        <defs>
          <linearGradient id="icon-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#6366f1"/>
            <stop offset="100%" stop-color="#ec4899"/>
          </linearGradient>
        </defs>
        <circle cx="50" cy="50" r="45" fill="url(#icon-grad)" opacity="0.15"/>
        <circle cx="35" cy="35" r="8" fill="#6366f1" opacity="0.6"/>
        <circle cx="60" cy="40" r="5" fill="#ec4899" opacity="0.8"/>
        <circle cx="45" cy="65" r="12" fill="#6366f1" opacity="0.4"/>
        <circle cx="70" cy="70" r="6" fill="#ec4899" opacity="0.5"/>
      </svg>
    </div>
    <h1>Microba Segmentation</h1>
    <p class="subtitle">YOLO-based detection &amp; CFU/ml calculation</p>

    <div class="api-status {apiOnline ? 'online' : 'offline'}">
      <span class="dot"></span>
      {#if apiStatus === null}
        Checking API...
      {:else if apiOnline}
        API Online &middot; Model loaded
      {:else}
        API Offline &middot; {apiStatus?.error || 'Model not ready'}
      {/if}
    </div>
  </header>

  <main>
    <div class="tabs">
      <button
        class="tab {inputSource === 'upload' ? 'active' : ''}"
        on:click={() => { inputSource = 'upload'; }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        Upload Image
      </button>
      <button
        class="tab {inputSource === 'camera' ? 'active' : ''}"
        on:click={() => { inputSource = 'camera'; }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        Camera
      </button>
    </div>

    <section class="input-section">
      {#if inputSource === 'upload'}
        <ImageUploader bind:file bind:previewUrl bind:this={uploader} />
      {:else}
        <CameraCapture bind:file bind:previewUrl bind:this={camera} />
      {/if}

      <div class="cfu-section">
        <button class="cfu-toggle" on:click={() => showCfuSettings = !showCfuSettings}>
          <input type="checkbox" bind:checked={cfuEnabled} on:click|stopPropagation />
          <span>Enable CFU/ml Calculation</span>
          <svg class="chevron {showCfuSettings ? 'open' : ''}" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>
        {#if showCfuSettings && cfuEnabled}
          <CfuSettings bind:volumePlated bind:dilutionFactor />
        {/if}
      </div>

      <div class="actions">
        <button
          class="btn primary"
          on:click={analyze}
          disabled={!file || loading || !apiOnline}
        >
          {#if loading}
            <span class="spinner"></span>
            Analyzing...
          {:else}
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            {cfuEnabled ? 'Analyze & Calculate CFU/ml' : 'Analyze Image'}
          {/if}
        </button>

        {#if file || results}
          <button class="btn secondary" on:click={reset}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="1 4 1 10 7 10"/>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
            </svg>
            Clear
          </button>
        {/if}
      </div>
    </section>

    {#if error}
      <div class="error-banner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <div>
          <strong>Error:</strong> {error}
        </div>
      </div>
    {/if}

    {#if loading}
      <div class="loading-card">
        <div class="loader-ring">
          <div class="loader-spinner"></div>
        </div>
        <p>Running segmentation model...</p>
        <div class="loader-bar">
          <div class="loader-bar-fill"></div>
        </div>
      </div>
    {/if}

    {#if results}
      <div class="results-divider">
        <span>Results</span>
      </div>
    {/if}

    <ResultsView {results} {annotatedUrl} />
  </main>

  <footer>
    <p>Powered by <strong>YOLO11</strong> &middot; <strong>FastAPI</strong> &middot; <strong>Svelte</strong></p>
  </footer>
</div>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f8fafc;
    color: #0f172a;
    -webkit-font-smoothing: antialiased;
  }

  .app {
    position: relative;
    max-width: 960px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem;
    min-height: 100vh;
  }

  /* Background decoration */
  .bg-deco {
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: -1;
  }

  .bg-circle {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.15;
  }

  .bg-circle-1 {
    width: 500px;
    height: 500px;
    background: #6366f1;
    top: -150px;
    right: -100px;
    animation: float 20s ease-in-out infinite;
  }

  .bg-circle-2 {
    width: 400px;
    height: 400px;
    background: #ec4899;
    bottom: -100px;
    left: -100px;
    animation: float 25s ease-in-out infinite reverse;
  }

  .bg-circle-3 {
    width: 300px;
    height: 300px;
    background: #06b6d4;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation: float 18s ease-in-out infinite 5s;
  }

  @keyframes float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -30px) scale(1.05); }
    66% { transform: translate(-20px, 20px) scale(0.95); }
  }

  header {
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
  }

  .header-icon {
    margin-bottom: 0.75rem;
    display: inline-block;
  }

  .header-icon svg {
    width: 48px;
    height: 48px;
  }

  h1 {
    font-size: 2.25rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
    line-height: 1.2;
  }

  .subtitle {
    color: #64748b;
    margin: 0.35rem 0 1.25rem;
    font-size: 1rem;
    font-weight: 450;
  }

  .api-status {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 0.35rem 0.9rem;
    border-radius: 9999px;
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  .api-status.online {
    background: #ecfdf5;
    color: #065f46;
    border-color: #a7f3d0;
  }

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #ef4444;
    display: inline-block;
    animation: pulse-dot 2s infinite;
  }

  .api-status.online .dot {
    background: #10b981;
  }

  @keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  main {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 2rem;
    box-shadow:
      0 1px 3px rgba(0,0,0,0.04),
      0 8px 32px rgba(0,0,0,0.06);
    border: 1px solid rgba(255,255,255,0.8);
    position: relative;
  }

  /* Tabs */
  .tabs {
    display: flex;
    gap: 0;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #e2e8f0;
  }

  .tab {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.7rem 1.35rem;
    border: none;
    background: none;
    font-size: 0.9rem;
    font-weight: 600;
    color: #94a3b8;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s ease;
    position: relative;
  }

  .tab:hover {
    color: #64748b;
  }

  .tab.active {
    color: #6366f1;
    border-bottom-color: #6366f1;
  }

  .tab.active::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 2px;
    background: #6366f1;
    border-radius: 2px;
  }

  .input-section {
    margin-bottom: 1rem;
  }

  /* CFU Settings */
  .cfu-section {
    margin-top: 1.25rem;
  }

  .cfu-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.65rem 0.75rem;
    border: 1.5px solid #e2e8f0;
    background: #f8fafc;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
    color: #334155;
    border-radius: 10px;
    transition: all 0.2s;
  }

  .cfu-toggle:hover {
    border-color: #c7d2fe;
    background: #f0f0ff;
  }

  .cfu-toggle input[type="checkbox"] {
    width: 17px;
    height: 17px;
    accent-color: #6366f1;
    cursor: pointer;
  }

  .chevron {
    margin-left: auto;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    color: #94a3b8;
  }

  .chevron.open {
    transform: rotate(180deg);
    color: #6366f1;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    margin-top: 1.25rem;
    flex-wrap: wrap;
  }

  .btn {
    padding: 0.7rem 1.5rem;
    border: none;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
    font-family: inherit;
  }

  .btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  .btn.primary {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
  }

  .btn.primary:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  }

  .btn.primary:active:not(:disabled) {
    transform: translateY(0);
  }

  .btn.secondary {
    background: #f1f5f9;
    color: #475569;
    border: 1.5px solid #e2e8f0;
  }

  .btn.secondary:hover {
    background: #e2e8f0;
    border-color: #cbd5e1;
  }

  .spinner {
    display: inline-block;
    width: 17px;
    height: 17px;
    border: 2.5px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: linear-gradient(135deg, #fef2f2, #fff1f2);
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    color: #991b1b;
    font-size: 0.9rem;
    margin-top: 1rem;
    animation: slideUp 0.3s ease;
  }

  .error-banner svg {
    flex-shrink: 0;
    color: #ef4444;
  }

  .loading-card {
    text-align: center;
    padding: 2.5rem 2rem;
    color: #475569;
    margin-top: 1rem;
    animation: fadeIn 0.3s ease;
  }

  .loader-ring {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
  }

  .loader-spinner {
    width: 44px;
    height: 44px;
    border: 3px solid #e0e7ff;
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 0.7s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  }

  .loading-card p {
    margin: 0.5rem 0 1rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: #64748b;
  }

  .loader-bar {
    width: 200px;
    height: 4px;
    background: #e2e8f0;
    border-radius: 999px;
    overflow: hidden;
    margin: 0 auto;
  }

  .loader-bar-fill {
    height: 100%;
    width: 30%;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 999px;
    animation: loaderSlide 1.5s ease-in-out infinite;
  }

  @keyframes loaderSlide {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(400%); }
  }

  .results-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1.5rem 0 0.5rem;
    color: #94a3b8;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .results-divider::before,
  .results-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  footer {
    text-align: center;
    margin-top: 2.5rem;
    color: #94a3b8;
    font-size: 0.85rem;
  }

  footer p {
    margin: 0;
  }

  footer strong {
    color: #64748b;
    font-weight: 600;
  }
</style>
