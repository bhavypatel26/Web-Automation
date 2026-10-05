export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch('/api' + path, options);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(typeof error.detail === 'string' ? error.detail : 'Request failed');
  }
  return response.json();
}
export function jsonRequest<T>(path: string, body: unknown, method = 'POST') {
  return request<T>(path, {method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
}
export async function upload(file: File, category: 'recordings' | 'uploads') {
  const body = new FormData(); body.append('file', file);
  return (await request<{file: string}>('/uploads/' + category, {method: 'POST', body})).file;
}
