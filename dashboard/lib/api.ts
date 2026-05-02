const DEFAULT_BROWSER_API = "http://localhost:8080";
const DEFAULT_SERVER_API = "http://server:8080";

function getBaseUrl(): string {
  return process.env.AGENTSPINE_API_URL || process.env.NEXT_PUBLIC_API_URL || DEFAULT_SERVER_API || DEFAULT_BROWSER_API;
}

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${getBaseUrl()}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}
