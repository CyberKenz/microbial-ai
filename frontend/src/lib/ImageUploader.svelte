<script>
  export let file = null;
  export let previewUrl = null;

  let dragOver = false;
  let fileInput;

  function handleFiles(files) {
    if (files && files.length > 0) {
      const f = files[0];
      if (f.type.startsWith('image/')) {
        file = f;
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = URL.createObjectURL(f);
      }
    }
  }

  function onDrop(e) {
    dragOver = false;
    handleFiles(e.dataTransfer.files);
  }

  function onDragOver() {
    dragOver = true;
  }

  function onDragLeave() {
    dragOver = false;
  }

  function onClick() {
    fileInput.click();
  }

  function onInputChange(e) {
    handleFiles(e.target.files);
  }

  export function reset() {
    file = null;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
    fileInput.value = '';
  }
</script>

<div
  class="uploader {dragOver ? 'drag-over' : ''} {previewUrl ? 'has-preview' : ''}"
  on:drop|preventDefault={onDrop}
  on:dragover|preventDefault={onDragOver}
  on:dragleave={onDragLeave}
  on:click={onClick}
  role="button"
  tabindex="0"
  on:keydown={(e) => e.key === 'Enter' && onClick()}
>
  <input
    bind:this={fileInput}
    type="file"
    accept="image/*"
    hidden
    on:change={onInputChange}
  />

  {#if previewUrl}
    <img src={previewUrl} alt="Preview" class="preview-img" />
    <div class="preview-overlay">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
      <span>Click to change</span>
    </div>
  {:else}
    <div class="placeholder">
      <div class="placeholder-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
      </div>
      <p class="placeholder-text">Drag &amp; drop an image here, or <span>click to browse</span></p>
      <p class="placeholder-hint">Supports JPG, PNG, BMP, TIFF</p>
    </div>
  {/if}
</div>

<style>
  .uploader {
    position: relative;
    border: 2px dashed #cbd5e1;
    border-radius: 14px;
    padding: 2.5rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s ease;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    min-height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .uploader::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 14px;
    background: linear-gradient(135deg, transparent, transparent, transparent);
    transition: all 0.3s ease;
    z-index: 0;
  }

  .uploader:hover,
  .uploader.drag-over {
    border-color: #6366f1;
    background: linear-gradient(135deg, #eef2ff 0%, #f0f0ff 100%);
  }

  .uploader.drag-over {
    border-color: #4f46e5;
    transform: scale(1.01);
    background: linear-gradient(135deg, #e0e7ff 0%, #eef2ff 100%);
  }

  .uploader:focus-visible {
    outline: 2px solid #6366f1;
    outline-offset: 2px;
  }

  .uploader.has-preview {
    padding: 0.5rem;
    border-style: solid;
    border-color: #e2e8f0;
    background: #fff;
    min-height: auto;
  }

  .preview-img {
    max-width: 100%;
    max-height: 420px;
    border-radius: 10px;
    object-fit: contain;
    position: relative;
    z-index: 1;
  }

  .preview-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.6));
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: #fff;
    font-size: 0.82rem;
    font-weight: 500;
    opacity: 0;
    transition: opacity 0.25s;
    border-radius: 0 0 10px 10px;
  }

  .uploader:hover .preview-overlay {
    opacity: 1;
  }

  .placeholder {
    position: relative;
    z-index: 1;
    color: #64748b;
  }

  .placeholder-icon {
    margin-bottom: 1rem;
    opacity: 0.4;
    transition: opacity 0.25s, transform 0.25s;
  }

  .uploader:hover .placeholder-icon {
    opacity: 0.7;
    transform: translateY(-2px);
  }

  .placeholder-text {
    margin: 0.5rem 0;
    font-size: 1rem;
    font-weight: 500;
    color: #475569;
  }

  .placeholder-text span {
    color: #6366f1;
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 2px;
  }

  .placeholder-hint {
    color: #94a3b8;
    font-size: 0.82rem;
    margin: 0.35rem 0 0;
  }
</style>
