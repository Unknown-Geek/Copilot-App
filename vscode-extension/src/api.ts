/**
 * API client for communicating with the DocGen backend
 */

import * as vscode from "vscode";
import {
  DocumentationResponse,
  TranslationResponse,
  AnalysisResponse,
  ExtensionConfig,
} from "./types";

/**
 * Get extension configuration
 */
export function getConfig(): ExtensionConfig {
  const config = vscode.workspace.getConfiguration("docgen");
  return {
    backendUrl: config.get<string>(
      "backendUrl",
      "https://codedoc-vscode-extension.onrender.com"
    ),
    defaultTargetLanguage: config.get<string>("defaultTargetLanguage", "es"),
    defaultExportFormat: config.get<string>("defaultExportFormat", "markdown"),
    showStatusBar: config.get<boolean>("showStatusBar", true),
  };
}

/**
 * Check if localhost server is running
 */
async function isLocalhostRunning(): Promise<boolean> {
  try {
    const response = await fetch("http://localhost:5001/api/analyze", {
      method: "HEAD",
      signal: AbortSignal.timeout(1000), // 1 second timeout
    });
    return response.ok || response.status === 405; // 405 means endpoint exists but HEAD not allowed
  } catch {
    return false;
  }
}

/**
 * Get the appropriate backend URL (prioritize localhost if running)
 */
async function getBackendUrl(): Promise<string> {
  const config = getConfig();
  
  // Check if localhost is running
  if (await isLocalhostRunning()) {
    return "http://localhost:5001";
  }
  
  // Fallback to configured backend URL (Render)
  return config.backendUrl;
}

/**
 * Make an API request to the backend
 */
async function apiRequest<T>(
  endpoint: string,
  method: string = "GET",
  body?: object
): Promise<T> {
  const baseUrl = await getBackendUrl();
  const url = `${baseUrl}${endpoint}`;

  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error(
        `Cannot connect to backend at ${config.backendUrl}. Is the server running?`
      );
    }
    throw error;
  }
}

/**
 * Generate documentation for the given code
 */
export async function generateDocumentation(
  code: string,
  language: string,
  options?: {
    title?: string;
    description?: string;
    template?: string;
    format?: string;
  }
): Promise<DocumentationResponse> {
  return apiRequest<DocumentationResponse>(
    "/api/analyze/documentation/generate",
    "POST",
    {
      code,
      language,
      title: options?.title,
      description: options?.description,
      template: options?.template || "default",
      format: options?.format || "markdown",
    }
  );
}

/**
 * Analyze code sentiment and metrics
 */
export async function analyzeCode(
  code: string,
  language: string
): Promise<AnalysisResponse> {
  return apiRequest<AnalysisResponse>("/api/analyze", "POST", {
    code,
    language,
  });
}

/**
 * Translate text to target language
 */
export async function translateText(
  text: string,
  targetLanguage: string
): Promise<TranslationResponse> {
  return apiRequest<TranslationResponse>("/api/translate", "POST", {
    text,
    target_language: targetLanguage,
  });
}

/**
 * Get basic documentation (without generation/export options)
 */
export async function getDocumentation(
  code: string,
  language: string
): Promise<DocumentationResponse> {
  return apiRequest<DocumentationResponse>(
    "/api/analyze/documentation",
    "POST",
    {
      code,
      language,
    }
  );
}

/**
 * Get GitHub repository information
 */
export async function getGitHubRepoInfo(
  owner: string,
  repo: string
): Promise<any> {
  return apiRequest<any>(`/github/${owner}/${repo}`, "GET");
}

/**
 * Analyze GitHub repository
 */
export async function analyzeGitHubRepo(
  owner: string,
  repo: string
): Promise<any> {
  return apiRequest<any>(`/github/${owner}/${repo}/analyze`, "GET");
}

/**
 * Get GitHub OAuth URL
 */
export async function getGitHubAuthUrl(): Promise<any> {
  return apiRequest<any>("/auth/github", "GET");
}
