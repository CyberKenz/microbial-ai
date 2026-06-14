<script>
  import { onMount, onDestroy } from 'svelte';

  export let file = null;
  export let previewUrl = null;

  let videoEl;
  let canvasEl;
  let stream = null;
  let cameraActive = false;
  let cameraError = null;
  let devices = [];
  let selectedDeviceId = null;

  async function enumerateCameras() {
    try {
      const list = await navigator.mediaDevices.enumerateDevices();
      devices = list.filter(d => d.kind === 'videoinput');
    } catch (e) {
      devices = [];
    }
  }

  async function startCamera() {
    cameraError = null;
    try {
      if (stream) stopCamera();
      const constraints = {
        video: selectedDeviceId
          ? { deviceId: { exact: selectedDeviceId }, width: { ideal: 1920 }, height: { ideal: 1080 } }
          : { width: { ideal: 1920 }, height: { ideal: 1080 } },
      };
      stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (videoEl) videoEl.srcObject = stream;
      cameraActive = true;
      await enumerateCameras();
    } catch (e) {
      cameraError = e.message || 'Could not access camera';
      cameraActive = false;
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
    cameraActive = false;
  }

  function capture() {
    if (!videoEl || !canvasEl) return;
    const w = videoEl.videoWidth;
    const h = videoEl.videoHeight;
    canvasEl.width = w;
    canvasEl.height = h;
    const ctx = canvasEl.getContext('2d');
    ctx.drawImage(videoEl, 0, 0, w, h);

    canvasEl.toBlob((blob) => {
      if (!blob) return;
      file = new File([blob], `camera_${Date.now()}.png`, { type: 'image/png' });
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      previewUrl = URL.createObjectURL(blob);
      stopCamera();
    }, 'image/png');
  }

  function switchCamera() {
    if (devices.length <= 1) return;
    const currentIdx = devices.findIndex(d => d.deviceId === selectedDeviceId);
    const nextIdx = (currentIdx + 1) % devices.length;
    selectedDeviceId = devices[nextIdx].deviceId;
    startCamera();
  }

  export function reset() {
    stopCamera();
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    file = null;
    previewUrl = null;
  }

  onMount(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      cameraError = 'Camera API not available in this browser';
    }
  });

  onDestroy(() => {
    stopCamera();
  });
</script>

<div class="camera">
  {#if !cameraActive && !previewUrl}
    <div class="camera-placeholder">
      <div class="camera-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
      </div>

      <button class="camera-btn" on:click={startCamera} disabled={!!cameraError && cameraError.includes('not available')}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="23 7 16 12 23 17 23 7"/>
          <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
        </svg>
        Open Camera
      </button>

      {#if devices.length > 0}
        <select bind:value={selectedDeviceId} on:change={startCamera} class="device-select">
          {#each devices as dev, i}
            <option value={dev.deviceId}>{dev.label || `Camera ${i + 1}`}</option>
          {/each}
        </select>
      {/if}

      {#if cameraError}
        <p class="cam-error">{cameraError}</p>
      {/if}
    </div>
  {/if}

  {#if cameraActive}
    <div class="camera-view">
      <video bind:this={videoEl} autoplay playsinline muted></video>
      <div class="camera-controls">
        <button class="capture-btn" on:click={capture} title="Capture">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="6"/>
          </svg>
          Capture
        </button>
        {#if devices.length > 1}
          <button class="icon-btn switch-btn" on:click={switchCamera} title="Switch camera">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="17 1 21 5 17 9"/>
              <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
              <polyline points="7 23 3 19 7 15"/>
              <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
            </svg>
          </button>
        {/if}
        <button class="icon-btn cancel-btn" on:click={stopCamera} title="Close camera">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
  {/if}

  {#if previewUrl && !cameraActive}
    <div class="captured-preview">
      <img src={previewUrl} alt="" />
      <div class="captured-actions">
        <button class="retake-btn" on:click={reset}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="1 4 1 10 7 10"/>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
          </svg>
          Retake
        </button>
        <span class="captured-badge">Captured</span>
      </div>
    </div>
  {/if}

  <canvas bind:this={canvasEl} style="display:none"></canvas>
</div>

<style>
  .camera {
    margin-top: 1rem;
  }

  .camera-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 2rem;
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border-radius: 14px;
    border: 2px dashed #cbd5e1;
  }

  .camera-icon {
    opacity: 0.4;
  }

  .camera-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.75rem;
    background: linear-gradient(135deg, #10b981, #059669);
    color: #fff;
    border: none;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  }

  .camera-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
  }

  .camera-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .device-select {
    padding: 0.45rem 0.85rem;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #475569;
    background: #fff;
    max-width: 250px;
  }

  .cam-error {
    color: #dc2626;
    font-size: 0.85rem;
    text-align: center;
    margin: 0;
  }

  .camera-view {
    position: relative;
    border-radius: 14px;
    overflow: hidden;
    background: #000;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }

  .camera-view video {
    width: 100%;
    max-height: 420px;
    object-fit: contain;
    display: block;
  }

  .camera-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem;
    background: linear-gradient(transparent, rgba(0,0,0,0.85));
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
  }

  .capture-btn {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1.35rem;
    background: #ef4444;
    color: #fff;
    border: none;
    border-radius: 9999px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
  }

  .capture-btn:hover {
    background: #dc2626;
    transform: scale(1.05);
  }

  .icon-btn {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    border: 2px solid rgba(255,255,255,0.25);
    cursor: pointer;
    color: #fff;
    transition: all 0.2s;
    background: rgba(0,0,0,0.3);
    backdrop-filter: blur(4px);
  }

  .icon-btn:hover {
    background: rgba(255,255,255,0.2);
    border-color: rgba(255,255,255,0.5);
  }

  .captured-preview {
    position: relative;
    border-radius: 14px;
    overflow: hidden;
    animation: fadeIn 0.3s ease;
  }

  .captured-preview img {
    width: 100%;
    max-height: 420px;
    object-fit: contain;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    display: block;
  }

  .captured-actions {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
  }

  .captured-badge {
    background: rgba(16, 185, 129, 0.9);
    color: #fff;
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    backdrop-filter: blur(4px);
  }

  .retake-btn {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.45rem 0.9rem;
    background: rgba(255,255,255,0.15);
    color: #fff;
    border: 1.5px solid rgba(255,255,255,0.3);
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    backdrop-filter: blur(4px);
    font-family: inherit;
  }

  .retake-btn:hover {
    background: rgba(255,255,255,0.25);
    border-color: rgba(255,255,255,0.5);
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>
