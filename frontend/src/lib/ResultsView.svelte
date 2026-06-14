<script>
  import ColonyCharts from './ColonyCharts.svelte';

  export let results = null;
  export let annotatedUrl = null;

  $: detections = results?.detections || [];
  $: summary = results?.summary || {};
  $: inferenceTime = results?.inference_time_ms || 0;
  $: imageSize = results?.image_size || {};
  $: cfu = results?.cfu_calculation || null;
</script>

{#if results}
  <div class="results">
    {#if cfu}
      <div class="cfu-card">
        <div class="cfu-header">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20V10"/>
            <path d="M18 20V4"/>
            <path d="M6 20v-4"/>
          </svg>
          <h3>CFU/ml Calculation</h3>
        </div>
        <div class="cfu-main">
          <div class="cfu-value">{cfu.cfu_per_ml_scientific}</div>
          <div class="cfu-unit">CFU/ml</div>
        </div>
        <div class="cfu-breakdown">
          <div class="cfu-row">
            <span class="cfu-key">Formula</span>
            <code>{cfu.formula}</code>
          </div>
          <div class="cfu-row">
            <span class="cfu-key">Values</span>
            <code>{cfu.formula_values}</code>
          </div>
          <div class="cfu-params">
            <span class="cfu-param">
              <span class="param-value">{cfu.total_colonies}</span>
              <span class="param-label">Colonies</span>
            </span>
            <span class="cfu-param">
              <span class="param-value">{cfu.volume_plated_ml} ml</span>
              <span class="param-label">Volume</span>
            </span>
            <span class="cfu-param">
              <span class="param-value">{cfu.dilution_display}</span>
              <span class="param-label">Dilution</span>
            </span>
          </div>
        </div>
      </div>
    {/if}

    {#if annotatedUrl}
      <div class="annotated-section">
        <div class="section-header">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
          <h3>Annotated Result</h3>
        </div>
        <img src={annotatedUrl} alt="Annotated prediction" class="annotated-img" />
      </div>
    {/if}

    <div class="summary-cards">
      <div class="card total">
        <div class="card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div class="card-value">{summary.total_detections || 0}</div>
        <div class="card-label">Total Detections</div>
      </div>
      <div class="card isolated">
        <div class="card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
        <div class="card-value">{summary.isolated_microba || 0}</div>
        <div class="card-label">Isolated</div>
      </div>
      <div class="card clustered">
        <div class="card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <path d="M2 12L22 12"/>
            <path d="M12 2L12 22"/>
          </svg>
        </div>
        <div class="card-value">{summary.clustered_microba || 0}</div>
        <div class="card-label">Clustered</div>
      </div>
      <div class="card info">
        <div class="card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="card-value">{inferenceTime}ms</div>
        <div class="card-label">Inf. Time</div>
      </div>
    </div>

    {#if imageSize.width}
      <p class="meta">
        Image: {imageSize.width} &times; {imageSize.height}px
      </p>
    {/if}

    <ColonyCharts {summary} {detections} {imageSize} />

    {#if detections.length > 0}
      <div class="section-header">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
        </svg>
        <h3>Detection Details</h3>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Class</th>
              <th>Confidence</th>
              <th>Area (px&sup2;)</th>
              <th>Bounding Box</th>
            </tr>
          </thead>
          <tbody>
            {#each detections as det, i}
              {@const w = det.bbox[2] - det.bbox[0]}
              {@const h = det.bbox[3] - det.bbox[1]}
              {@const area = Math.round(w * h)}
              <tr>
                <td class="row-num">{i + 1}</td>
                <td>
                  <span class="badge {det.class === 'isolated_microba' ? 'iso' : 'clu'}">
                    {det.class === 'isolated_microba' ? 'Isolated' : 'Clustered'}
                  </span>
                </td>
                <td class="mono">{(det.confidence * 100).toFixed(1)}%</td>
                <td class="mono">{area.toLocaleString()}</td>
                <td class="mono bbox">
                  [{det.bbox.map(v => v.toFixed(1)).join(', ')}]
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="no-detections">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          <line x1="8" y1="11" x2="14" y2="11"/>
        </svg>
        <p>No microba detected in this image.</p>
      </div>
    {/if}
  </div>
{/if}

<style>
  .results {
    margin-top: 1rem;
    animation: slideUp 0.35s ease;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    color: #1e293b;
  }

  .section-header h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: #1e293b;
  }

  .section-header svg {
    color: #6366f1;
  }

  /* CFU/ml Card */
  .cfu-card {
    background: linear-gradient(135deg, #eef2ff 0%, #ecfdf5 100%);
    border: 1.5px solid #c7d2fe;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.06);
    animation: slideUp 0.35s ease;
  }

  .cfu-header {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin-bottom: 0.75rem;
    color: #4338ca;
  }

  .cfu-header h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: #4338ca;
  }

  .cfu-header svg {
    color: #6366f1;
  }

  .cfu-main {
    text-align: center;
    padding: 0.5rem 0 1rem;
  }

  .cfu-value {
    font-size: 2.75rem;
    font-weight: 800;
    color: #0f172a;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .cfu-unit {
    font-size: 0.85rem;
    color: #6366f1;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.35rem;
  }

  .cfu-breakdown {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(8px);
    border-radius: 10px;
    padding: 0.85rem 1rem;
  }

  .cfu-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.4rem;
    font-size: 0.85rem;
  }

  .cfu-key {
    font-weight: 700;
    color: #4f46e5;
    min-width: 65px;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .cfu-row code {
    background: #e0e7ff;
    padding: 0.1rem 0.5rem;
    border-radius: 6px;
    font-size: 0.8rem;
    color: #3730a3;
    word-break: break-all;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  }

  .cfu-params {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1.5px solid #c7d2fe;
    flex-wrap: wrap;
  }

  .cfu-param {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
  }

  .param-value {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1e293b;
  }

  .param-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
  }

  .annotated-section {
    margin-bottom: 1.5rem;
    animation: slideUp 0.35s ease;
  }

  .annotated-img {
    max-width: 100%;
    max-height: 520px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    object-fit: contain;
    display: block;
    width: 100%;
  }

  .summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .card {
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.2s ease;
    cursor: default;
  }

  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  }

  .card.total {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 1px solid #bae6fd;
  }

  .card.isolated {
    background: linear-gradient(135deg, #eef2ff, #e0e7ff);
    border: 1px solid #c7d2fe;
  }

  .card.clustered {
    background: linear-gradient(135deg, #fdf2f8, #fce7f3);
    border: 1px solid #fbcfe8;
  }

  .card.info {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 1px solid #bbf7d0;
  }

  .card-icon {
    margin-bottom: 0.35rem;
    opacity: 0.6;
  }

  .card-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1;
  }

  .card-label {
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 0.3rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .meta {
    color: #64748b;
    font-size: 0.82rem;
    margin-bottom: 1rem;
    font-weight: 500;
  }

  .table-wrapper {
    overflow-x: auto;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }

  thead {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  }

  th {
    text-align: left;
    padding: 0.75rem 1rem;
    color: #475569;
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1.5px solid #e2e8f0;
  }

  td {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b;
  }

  tbody tr:hover {
    background: #f8fafc;
  }

  tbody tr:last-child td {
    border-bottom: none;
  }

  .row-num {
    color: #94a3b8;
    font-weight: 600;
  }

  .mono {
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.82rem;
    color: #475569;
  }

  .bbox {
    font-size: 0.75rem;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
  }

  .badge.iso {
    background: #e0e7ff;
    color: #4338ca;
  }

  .badge.clu {
    background: #fce7f3;
    color: #be185d;
  }

  .no-detections {
    text-align: center;
    color: #94a3b8;
    padding: 2.5rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }

  .no-detections p {
    margin: 0;
    font-size: 0.95rem;
    font-style: italic;
  }

  .no-detections svg {
    opacity: 0.4;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
