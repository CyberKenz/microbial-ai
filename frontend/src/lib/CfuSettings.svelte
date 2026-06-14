<script>
  export let volumePlated = 0.1;
  export let dilutionFactor = 0.00001;

  let dilutionExponent = Math.round(Math.log10(dilutionFactor));

  const dilutionPresets = [
    { label: 'No dilution (10^0)', value: 1, exp: 0 },
    { label: '10^-1', value: 0.1, exp: -1 },
    { label: '10^-2', value: 0.01, exp: -2 },
    { label: '10^-3', value: 0.001, exp: -3 },
    { label: '10^-4', value: 0.0001, exp: -4 },
    { label: '10^-5', value: 0.00001, exp: -5 },
    { label: '10^-6', value: 0.000001, exp: -6 },
    { label: '10^-7', value: 0.0000001, exp: -7 },
    { label: '10^-8', value: 0.00000001, exp: -8 },
  ];

  $: selectedPresetIndex = dilutionPresets.findIndex(p => p.value === dilutionFactor);

  function onPresetChange() {
    const preset = dilutionPresets[selectedPresetIndex];
    if (preset) {
      dilutionFactor = preset.value;
      dilutionExponent = preset.exp;
    }
  }

  function onExponentChange() {
    dilutionFactor = Math.pow(10, dilutionExponent);
  }
</script>

<div class="cfu-settings">
  <h3>CFU/ml Parameters</h3>

  <div class="settings-grid">
    <div class="field">
      <label for="volume">Volume Plated (ml)</label>
      <input
        id="volume"
        type="number"
        bind:value={volumePlated}
        min="0.001"
        step="0.01"
        class="input"
      />
    </div>

    <div class="field">
      <label for="dilution">Dilution Factor</label>
      <div class="dilution-row">
        <select bind:value={selectedPresetIndex} on:change={onPresetChange} class="input preset-select">
          {#each dilutionPresets as preset, i}
            <option value={i}>{preset.label}</option>
          {/each}
        </select>
        <div class="custom-exp">
          <span>10^</span>
          <input
            type="number"
            bind:value={dilutionExponent}
            on:input={onExponentChange}
            min="-12"
            max="0"
            class="input exp-input"
          />
        </div>
      </div>
    </div>
  </div>

  <div class="formula-info">
    <span class="formula-label">Formula:</span>
    <code>CFU/ml = total colonies / (volume x dilution)</code>
  </div>
</div>

<style>
  .cfu-settings {
    background: linear-gradient(135deg, #f0f9ff 0%, #fdf4ff 100%);
    border: 1px solid #e0e7ff;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    transition: box-shadow 0.2s;
  }

  .cfu-settings:hover {
    box-shadow: 0 2px 12px rgba(99, 102, 241, 0.08);
  }

  .cfu-settings h3 {
    margin: 0 0 0.75rem;
    font-size: 1rem;
    font-weight: 700;
    color: #4338ca;
    letter-spacing: -0.01em;
  }

  .settings-grid {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: 1rem;
  }

  @media (max-width: 500px) {
    .settings-grid {
      grid-template-columns: 1fr;
    }
  }

  .field label {
    display: block;
    font-size: 0.78rem;
    font-weight: 700;
    color: #4f46e5;
    margin-bottom: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .input {
    width: 100%;
    padding: 0.5rem 0.7rem;
    border: 1.5px solid #e0e7ff;
    border-radius: 8px;
    font-size: 0.9rem;
    color: #1e293b;
    background: #fff;
    transition: all 0.2s;
  }

  .input:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  }

  .dilution-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .preset-select {
    flex: 1;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
    background-position: right 0.5rem center;
    background-repeat: no-repeat;
    background-size: 1.25rem;
    padding-right: 2rem;
  }

  .custom-exp {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.9rem;
    color: #4f46e5;
    white-space: nowrap;
    font-weight: 600;
  }

  .exp-input {
    width: 60px !important;
    text-align: center;
  }

  .formula-info {
    margin-top: 0.85rem;
    padding-top: 0.85rem;
    border-top: 1.5px solid #e0e7ff;
    font-size: 0.82rem;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .formula-label {
    font-weight: 700;
    color: #4f46e5;
  }

  code {
    background: #e0e7ff;
    padding: 0.15rem 0.6rem;
    border-radius: 6px;
    font-size: 0.82rem;
    color: #3730a3;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  }
</style>
