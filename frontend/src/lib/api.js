const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function predictImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Prediction failed');
  }
  return res.json();
}

export async function predictAnnotated(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/predict-annotated`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Annotated prediction failed');
  }
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function fetchCfuDefaults() {
  const res = await fetch(`${API_BASE}/api/cfu-defaults`);
  if (!res.ok) throw new Error('Failed to fetch CFU defaults');
  return res.json();
}

export async function calculateCfu(file, volumePlatedMl, dilutionFactor) {
  const formData = new FormData();
  formData.append('file', file);
  const params = new URLSearchParams();
  if (volumePlatedMl != null) params.set('volume_plated_ml', String(volumePlatedMl));
  if (dilutionFactor != null) params.set('dilution_factor', String(dilutionFactor));
  const res = await fetch(`${API_BASE}/api/calculate-cfu?${params}`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'CFU calculation failed');
  }
  return res.json();
}
