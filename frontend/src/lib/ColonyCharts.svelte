<script>
  export let summary = {};
  export let detections = [];
  export let imageSize = {};

  $: isolated = summary?.isolated_microba || 0;
  $: clustered = summary?.clustered_microba || 0;
  $: total = summary?.total_detections || 0;

  const barW = 280, barH = 200;
  const barPad = { top: 20, right: 20, bottom: 50, left: 50 };
  $: barData = [
    { label: 'Isolated', value: isolated, color: '#6366f1' },
    { label: 'Clustered', value: clustered, color: '#ec4899' },
  ];
  $: barMax = Math.max(...barData.map(d => d.value), 1);
  $: barInnerW = barW - barPad.left - barPad.right;
  $: barInnerH = barH - barPad.top - barPad.bottom;
  $: barSlotW = barInnerW / barData.length;
  $: barBarW = barSlotW * 0.55;
  $: yTicks = generateTicks(barMax, 4);

  const donutSize = 200;
  const donutR = 75;
  const donutInner = 45;
  $: donutCx = donutSize / 2;
  $: donutCy = donutSize / 2;
  $: donutSlices = buildDonutSlices(isolated, clustered);

  const scatW = 400, scatH = 250;
  const scatPad = { top: 25, right: 25, bottom: 50, left: 55 };
  $: scatDetections = detections.map((d, i) => {
    const [x1, y1, x2, y2] = d.bbox;
    const w = x2 - x1;
    const h = y2 - y1;
    const area = w * h;
    const cx = x1 + w / 2;
    const cy = y1 + h / 2;
    return { ...d, area, cx, cy, idx: i };
  });
  $: scatImgW = imageSize?.width || 1;
  $: scatImgH = imageSize?.height || 1;
  $: scatMaxArea = Math.max(...scatDetections.map(d => d.area), 1);
  $: scatInnerW = scatW - scatPad.left - scatPad.right;
  $: scatInnerH = scatH - scatPad.top - scatPad.bottom;
  $: xScatTicks = generateTicks(scatImgW, 5);
  $: yScatTicks = generateTicks(scatImgH, 4);

  const areaW = 400, areaH = 200;
  const areaPad = { top: 20, right: 20, bottom: 50, left: 50 };
  $: areaBins = buildAreaBins(scatDetections);
  $: areaMaxBin = Math.max(...areaBins.map(b => b.count), 1);
  $: areaInnerW = areaW - areaPad.left - areaPad.right;
  $: areaInnerH = areaH - areaPad.top - areaPad.bottom;
  $: areaBinW = areaInnerW / Math.max(areaBins.length, 1);
  $: areaYTicks = generateTicks(areaMaxBin, 4);

  function generateTicks(maxVal, count) {
    if (maxVal <= 0) return [0];
    const step = Math.ceil(maxVal / count);
    const ticks = [];
    for (let i = 0; i <= count; i++) {
      ticks.push(Math.min(i * step, maxVal));
    }
    return ticks;
  }

  function buildDonutSlices(iso, clu) {
    const total = iso + clu;
    if (total === 0) return [];
    const slices = [];
    let startAngle = -Math.PI / 2;
    const data = [
      { label: 'Isolated', value: iso, color: '#6366f1' },
      { label: 'Clustered', value: clu, color: '#ec4899' },
    ];
    for (const d of data) {
      if (d.value === 0) continue;
      const angle = (d.value / total) * Math.PI * 2;
      const endAngle = startAngle + angle;
      slices.push({
        ...d,
        path: arcPath(donutCx, donutCy, donutR, donutInner, startAngle, endAngle),
        pct: ((d.value / total) * 100).toFixed(1),
      });
      startAngle = endAngle;
    }
    return slices;
  }

  function arcPath(cx, cy, outerR, innerR, startAngle, endAngle) {
    const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;
    const sx1 = cx + outerR * Math.cos(startAngle);
    const sy1 = cy + outerR * Math.sin(startAngle);
    const ex1 = cx + outerR * Math.cos(endAngle);
    const ey1 = cy + outerR * Math.sin(endAngle);
    const sx2 = cx + innerR * Math.cos(endAngle);
    const sy2 = cy + innerR * Math.sin(endAngle);
    const ex2 = cx + innerR * Math.cos(startAngle);
    const ey2 = cy + innerR * Math.sin(startAngle);
    return [
      `M ${sx1} ${sy1}`,
      `A ${outerR} ${outerR} 0 ${largeArc} 1 ${ex1} ${ey1}`,
      `L ${sx2} ${sy2}`,
      `A ${innerR} ${innerR} 0 ${largeArc} 0 ${ex2} ${ey2}`,
      'Z',
    ].join(' ');
  }

  function buildAreaBins(dets) {
    if (dets.length === 0) return [];
    const areas = dets.map(d => d.area).sort((a, b) => a - b);
    const minA = areas[0];
    const maxA = areas[areas.length - 1];
    const binCount = Math.min(8, Math.max(3, Math.ceil(Math.sqrt(dets.length))));
    const step = (maxA - minA) / binCount || 1;
    const bins = [];
    for (let i = 0; i < binCount; i++) {
      const lo = minA + i * step;
      const hi = lo + step;
      const count = dets.filter(d => d.area >= lo && (i === binCount - 1 ? d.area <= hi + 1 : d.area < hi)).length;
      const isoCount = dets.filter(d => d.area >= lo && (i === binCount - 1 ? d.area <= hi + 1 : d.area < hi) && d.class === 'isolated_microba').length;
      const cluCount = count - isoCount;
      bins.push({
        label: `${Math.round(lo)}-${Math.round(hi)}`,
        count,
        isoCount,
        cluCount,
        lo,
        hi,
      });
    }
    return bins;
  }

  function formatNum(n) {
    if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
    return String(Math.round(n));
  }
</script>

{#if total > 0}
  <div class="charts-section">
    <div class="section-header">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"/>
        <line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/>
      </svg>
      <h3>Colony Analysis Charts</h3>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <h4>Colony Type Counts</h4>
        <svg viewBox="0 0 {barW} {barH}" class="chart-svg">
          {#each yTicks as tick}
            {@const y = barPad.top + barInnerH - (tick / barMax) * barInnerH}
            <line x1={barPad.left} y1={y} x2={barPad.left + barInnerW} y2={y} stroke="#e2e8f0" stroke-width="1" />
            <text x={barPad.left - 8} y={y + 4} text-anchor="end" class="axis-label">{tick}</text>
          {/each}
          {#each barData as d, i}
            {@const x = barPad.left + i * barSlotW + (barSlotW - barBarW) / 2}
            {@const h = (d.value / barMax) * barInnerH}
            {@const y = barPad.top + barInnerH - h}
            <rect x={x} y={y} width={barBarW} height={h} fill={d.color} rx="6" opacity="0.85">
              <title>{d.label}: {d.value}</title>
            </rect>
            <text x={x + barBarW / 2} y={y - 8} text-anchor="middle" class="bar-value">{d.value}</text>
            <text x={x + barBarW / 2} y={barPad.top + barInnerH + 18} text-anchor="middle" class="axis-label bar-label">{d.label}</text>
          {/each}
          <line x1={barPad.left} y1={barPad.top + barInnerH} x2={barPad.left + barInnerW} y2={barPad.top + barInnerH} stroke="#94a3b8" stroke-width="1.5" />
        </svg>
      </div>

      <div class="chart-card">
        <h4>Colony Distribution</h4>
        <svg viewBox="0 0 {donutSize} {donutSize}" class="chart-svg donut">
          {#each donutSlices as slice}
            <path d={slice.path} fill={slice.color} opacity="0.85" stroke="#fff" stroke-width="2.5">
              <title>{slice.label}: {slice.pct}% ({slice.value})</title>
            </path>
          {/each}
          <text x={donutCx} y={donutCy - 6} text-anchor="middle" class="donut-total">{total}</text>
          <text x={donutCx} y={donutCy + 14} text-anchor="middle" class="donut-sublabel">Total</text>
          {#each donutSlices as slice, i}
            {@const ly = donutSize - 25}
            {@const lx = 20 + i * 100}
            <rect x={lx} y={ly} width="10" height="10" fill={slice.color} rx="3" />
            <text x={lx + 14} y={ly + 9} class="legend-text">{slice.label} ({slice.pct}%)</text>
          {/each}
        </svg>
      </div>
    </div>

    <div class="chart-card wide">
      <h4>Colony Spatial Distribution (Position &amp; Size)</h4>
      <svg viewBox="0 0 {scatW} {scatH}" class="chart-svg scatter">
        {#each xScatTicks as tick}
          {@const x = scatPad.left + (tick / scatImgW) * scatInnerW}
          <line x1={x} y1={scatPad.top} x2={x} y2={scatPad.top + scatInnerH} stroke="#f1f5f9" stroke-width="1" />
          <text x={x} y={scatPad.top + scatInnerH + 18} text-anchor="middle" class="axis-label sm">{formatNum(tick)}</text>
        {/each}
        {#each yScatTicks as tick}
          {@const y = scatPad.top + scatInnerH - (tick / scatImgH) * scatInnerH}
          <line x1={scatPad.left} y1={y} x2={scatPad.left + scatInnerW} y2={y} stroke="#f1f5f9" stroke-width="1" />
          <text x={scatPad.left - 8} y={y + 4} text-anchor="end" class="axis-label sm">{formatNum(tick)}</text>
        {/each}
        {#each scatDetections as d}
          {@const sx = scatPad.left + (d.cx / scatImgW) * scatInnerW}
          {@const sy = scatPad.top + scatInnerH - (d.cy / scatImgH) * scatInnerH}
          {@const r = 3 + (d.area / scatMaxArea) * 10}
          {@const fill = d.class === 'isolated_microba' ? '#6366f1' : '#ec4899'}
          <circle cx={sx} cy={sy} r={r} fill={fill} opacity="0.6" stroke={fill} stroke-width="1.5">
            <title>#{d.idx + 1} {d.class === 'isolated_microba' ? 'Isolated' : 'Clustered'} | Area: {Math.round(d.area)}px&sup2; | Conf: {(d.confidence * 100).toFixed(1)}%</title>
          </circle>
        {/each}
        <line x1={scatPad.left} y1={scatPad.top + scatInnerH} x2={scatPad.left + scatInnerW} y2={scatPad.top + scatInnerH} stroke="#94a3b8" stroke-width="1.5" />
        <line x1={scatPad.left} y1={scatPad.top} x2={scatPad.left} y2={scatPad.top + scatInnerH} stroke="#94a3b8" stroke-width="1.5" />
        <text x={scatPad.left + scatInnerW / 2} y={scatH - 5} text-anchor="middle" class="axis-title">X Position (px)</text>
        <text x={12} y={scatPad.top + scatInnerH / 2} text-anchor="middle" class="axis-title" transform="rotate(-90, 12, {scatPad.top + scatInnerH / 2})">Y Position (px)</text>
        <circle cx={scatW - 130} cy={scatPad.top + 10} r="5" fill="#6366f1" opacity="0.7" />
        <text x={scatW - 120} y={scatPad.top + 14} class="legend-text">Isolated</text>
        <circle cx={scatW - 55} cy={scatPad.top + 10} r="5" fill="#ec4899" opacity="0.7" />
        <text x={scatW - 45} y={scatPad.top + 14} class="legend-text">Clustered</text>
      </svg>
    </div>

    {#if areaBins.length > 1}
      <div class="chart-card wide">
        <h4>Colony Area Distribution (px&sup2;)</h4>
        <svg viewBox="0 0 {areaW} {areaH}" class="chart-svg">
          {#each areaYTicks as tick}
            {@const y = areaPad.top + areaInnerH - (tick / areaMaxBin) * areaInnerH}
            <line x1={areaPad.left} y1={y} x2={areaPad.left + areaInnerW} y2={y} stroke="#e2e8f0" stroke-width="1" />
            <text x={areaPad.left - 8} y={y + 4} text-anchor="end" class="axis-label">{tick}</text>
          {/each}
          {#each areaBins as bin, i}
            {@const x = areaPad.left + i * areaBinW + 2}
            {@const bw = areaBinW - 4}
            {@const totalH = (bin.count / areaMaxBin) * areaInnerH}
            {@const isoH = bin.count > 0 ? (bin.isoCount / bin.count) * totalH : 0}
            {@const cluH = totalH - isoH}
            {@const y = areaPad.top + areaInnerH - totalH}
            {#if bin.count > 0}
              <rect x={x} y={y} width={bw} height={cluH} fill="#ec4899" rx="2" opacity="0.8">
                <title>Clustered: {bin.cluCount}</title>
              </rect>
              <rect x={x} y={y + cluH} width={bw} height={isoH} fill="#6366f1" rx="2" opacity="0.8">
                <title>Isolated: {bin.isoCount}</title>
              </rect>
              <text x={x + bw / 2} y={y - 5} text-anchor="middle" class="bar-value sm">{bin.count}</text>
            {/if}
            <text x={x + bw / 2} y={areaPad.top + areaInnerH + 16} text-anchor="middle" class="axis-label sm" transform="rotate(-30, {x + bw / 2}, {areaPad.top + areaInnerH + 16})">{bin.label}</text>
          {/each}
          <line x1={areaPad.left} y1={areaPad.top + areaInnerH} x2={areaPad.left + areaInnerW} y2={areaPad.top + areaInnerH} stroke="#94a3b8" stroke-width="1.5" />
          <text x={areaPad.left + areaInnerW / 2} y={areaH - 4} text-anchor="middle" class="axis-title">Colony Area (px&sup2;)</text>
        </svg>
      </div>
    {/if}
  </div>
{/if}

<style>
  .charts-section {
    margin-top: 1.5rem;
    animation: slideUp 0.35s ease;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
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

  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  @media (max-width: 600px) {
    .charts-grid {
      grid-template-columns: 1fr;
    }
  }

  .chart-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem;
    transition: all 0.2s ease;
  }

  .chart-card:hover {
    border-color: #c7d2fe;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.05);
  }

  .chart-card.wide {
    margin-bottom: 1rem;
  }

  .chart-card h4 {
    margin: 0 0 0.75rem;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 700;
  }

  .chart-svg {
    width: 100%;
    height: auto;
    display: block;
  }

  .chart-svg.donut {
    max-width: 250px;
    margin: 0 auto;
  }

  :global(.axis-label) {
    font-size: 9px;
    fill: #64748b;
    font-family: inherit;
  }

  :global(.axis-label.sm) {
    font-size: 7.5px;
  }

  :global(.bar-value) {
    font-size: 11px;
    font-weight: 700;
    fill: #1e293b;
    font-family: inherit;
  }

  :global(.bar-value.sm) {
    font-size: 9px;
  }

  :global(.bar-label) {
    font-size: 10px;
    font-weight: 600;
  }

  :global(.donut-total) {
    font-size: 26px;
    font-weight: 800;
    fill: #0f172a;
    font-family: inherit;
  }

  :global(.donut-sublabel) {
    font-size: 10px;
    fill: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
  }

  :global(.legend-text) {
    font-size: 9px;
    fill: #475569;
    font-weight: 500;
    font-family: inherit;
  }

  :global(.axis-title) {
    font-size: 9px;
    fill: #475569;
    font-weight: 600;
    font-family: inherit;
  }

  circle:hover, rect:hover {
    opacity: 1 !important;
    cursor: pointer;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
