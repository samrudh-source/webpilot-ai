export type Workflow = { id: number; name: string; target_url: string; task: string; status: string; created_at: string }

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } })
  if (!res.ok) throw new Error((await res.json()).detail || `Request failed (${res.status})`)
  return res.json()
}
