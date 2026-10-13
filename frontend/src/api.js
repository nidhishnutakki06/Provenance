const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function ask(question, role = 'analyst') {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, role }),
  });
  if (!res.ok) {
    throw new Error(`API error (/ask): ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

export async function getOnboarding(jobRole = 'QA', role = 'analyst') {
  const params = new URLSearchParams({ job_role: jobRole, role });
  const res = await fetch(`${BASE_URL}/onboarding?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`API error (/onboarding): ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

export async function getExperts(topic = 'deviation', role = 'analyst') {
  const params = new URLSearchParams({ topic, role });
  const res = await fetch(`${BASE_URL}/experts?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`API error (/experts): ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

export async function getGaps() {
  const res = await fetch(`${BASE_URL}/gaps`);
  if (!res.ok) {
    throw new Error(`API error (/gaps): ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

export async function getStats() {
  const res = await fetch(`${BASE_URL}/stats`);
  if (!res.ok) {
    throw new Error(`API error (/stats): ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

export async function getHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`API error (/health): ${res.status} ${res.statusText}`);
  }
  return await res.json();
}
