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
    throw new Error(`Chat API error: ${res.statusText}`);
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
    throw new Error(`Analyze API error: ${res.statusText}`);
  }
  return res.json();
}

export async function getSources(): Promise<{ sources: SourceItem[]; total: number }> {
  const res = await fetch(`${API_BASE}/sources`);
  if (!res.ok) {
    throw new Error(`Failed to load sources: ${res.statusText}`);
  }
  return res.json();
}

export async function getEvaluationTelemetry(): Promise<Record<string, any>> {
  const res = await fetch(`${API_BASE}/evaluation`);
  if (!res.ok) {
    throw new Error(`Failed to load evaluation metrics: ${res.statusText}`);
  }
  return res.json();
}
