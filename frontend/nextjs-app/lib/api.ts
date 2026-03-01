/**
 * BrandKin AI - API Client
 * Handles communication with backend API Gateway with App Authentication
 */

import CryptoJS from 'crypto-js';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';
const APP_KEY = process.env.NEXT_PUBLIC_APP_KEY || '';
const APP_SECRET = process.env.NEXT_PUBLIC_APP_SECRET || '';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * Generate signature for API Gateway App Authentication
 * Uses HMAC-SHA256 with AppSecret
 */
function generateSignature(
  method: string,
  path: string,
  timestamp: string,
  nonce: string
): string {
  const stringToSign = `${method}\n${path}\n${timestamp}\n${nonce}`;
  return CryptoJS.HmacSHA256(stringToSign, APP_SECRET).toString(CryptoJS.enc.Base64);
}

/**
 * Make authenticated API request
 */
async function apiRequest<T>(
  method: string,
  endpoint: string,
  body?: object
): Promise<ApiResponse<T>> {
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_BASE_URL}${path}`;
  
  // Generate authentication headers
  const timestamp = new Date().toISOString();
  const nonce = Math.random().toString(36).substring(2, 15);
  const signature = generateSignature(method, path, timestamp, nonce);
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-App-Key': APP_KEY,
    'X-Timestamp': timestamp,
    'X-Nonce': nonce,
    'X-Signature': signature,
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
};

export default api;
