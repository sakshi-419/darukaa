import { ChatResponse, SourceItem } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

export async function sendChatMessage(
  message: string,
  conversationId?: string,
  geoCoords?: { latitude: number; longitude: number }
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
      geo_coords: geoCoords,
    }),
  });
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${errText || res.statusText || 'Request failed'}`);
  }
  return res.json();
}

export async function analyzeEnvironmentJson(jsonData: Record<string, any>): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/environment/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jsonData),
  });
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${errText || res.statusText || 'Request failed'}`);
  }
  return res.json();
}

export async function getSources(): Promise<{ sources: SourceItem[]; total: number }> {
  const res = await fetch(`${API_BASE}/sources`);
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${errText || res.statusText || 'Failed to load sources'}`);
  }
  return res.json();
}

export async function getEvaluationTelemetry(): Promise<Record<string, any>> {
  const res = await fetch(`${API_BASE}/evaluation`);
  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${errText || res.statusText || 'Failed to load telemetry'}`);
  }
  return res.json();
}
