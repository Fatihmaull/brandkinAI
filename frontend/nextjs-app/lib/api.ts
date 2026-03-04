/**
 * BrandKin AI - API Client
 * Handles communication with backend API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * Make API request (no client-side auth — handled by API Gateway)
 */
async function apiRequest<T>(
  method: string,
  endpoint: string,
  body?: object
): Promise<ApiResponse<T>> {
  // If API_BASE_URL is set (e.g., local dev), use it. Otherwise, use relative path for Vercel proxy.
  // Ensure we don't end up with //api/v1/projects
  const baseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${path}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    const data = await response.json();

    if (!response.ok) {
      return { error: data.error || `HTTP ${response.status}` };
    }

    return { data };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Network error' };
  }
}

// API Methods
export const api = {
  // Stage 0: Create project
  createProject: (brandBrief: object) =>
    apiRequest('POST', '/api/v1/projects', { brand_brief: brandBrief }),

  // Get project status
  getProject: (projectId: string) =>
    apiRequest('GET', `/api/v1/projects/${projectId}`),

  // Get project assets
  getAssets: (projectId: string) =>
    apiRequest('GET', `/api/v1/projects/${projectId}/assets`),

  // Stage 3: Select character
  selectCharacter: (projectId: string, assetId: string, type: string) =>
    apiRequest('POST', `/api/v1/projects/${projectId}/select`, { asset_id: assetId, type }),

  // Stage 6: Request revision
  requestRevision: (projectId: string, assetId: string, feedback: string, type: string) =>
    apiRequest('POST', `/api/v1/projects/${projectId}/revise`, { asset_id: assetId, feedback, type }),

  // Stage 7: Finalize brand kit
  finalizeProject: (projectId: string) =>
    apiRequest('POST', `/api/v1/projects/${projectId}/finalize`, { project_id: projectId }),

  // Get code exports
  getCodeExports: (projectId: string) =>
    apiRequest('GET', `/api/v1/projects/${projectId}/code`),

  // Health check
  health: () =>
    apiRequest('GET', '/health'),
};

export default api;
