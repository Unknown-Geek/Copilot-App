/**
 * Type definitions for the DocGen extension
 */

export interface CodeBlock {
  content: string;
  language: string;
  line_number: number;
}

export interface DocumentationMetrics {
  total_lines: number;
  code_blocks_count: number;
  complexity?: number;
  functions_count?: number;
  classes_count?: number;
}

export interface Documentation {
  title: string;
  description: string;
  code_blocks: CodeBlock[];
  language: string;
  generated_at: string;
  metrics: DocumentationMetrics;
}

export interface DocumentationResponse {
  status: "success" | "error";
  documentation?: Documentation | string;
  format?: string;
  template?: string;
  error?: string;
}

export interface TranslationResponse {
  status: "success" | "error";
  translated_text?: string;
  detected_language?: string;
  confidence?: number;
  metrics?: {
    input_length: number;
    translation_length: number;
  };
  error?: string;
}

export interface AnalysisResponse {
  status: "success" | "error";
  sentiment?: string;
  confidence_scores?: {
    positive: number;
    neutral: number;
    negative: number;
  };
  language?: string;
  error?: string;
}

export interface ExtensionConfig {
  backendUrl: string;
  defaultTargetLanguage: string;
  defaultExportFormat: string;
  showStatusBar: boolean;
}

export interface LanguageOption {
  code: string;
  name: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "it", name: "Italian" },
  { code: "pt", name: "Portuguese" },
  { code: "zh", name: "Chinese" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "ar", name: "Arabic" },
  { code: "hi", name: "Hindi" },
  { code: "ru", name: "Russian" },
];

export const EXPORT_FORMATS = [
  { id: "markdown", label: "Markdown (.md)" },
  { id: "html", label: "HTML (.html)" },
  { id: "json", label: "JSON (.json)" },
];

export interface GitHubRepoInfo {
  name: string;
  full_name: string;
  description: string;
  language: string;
  stars: number;
  forks: number;
  open_issues: number;
  topics: string[];
  license: string | null;
  created_at: string;
  updated_at: string;
  homepage: string;
  default_branch: string;
}

export interface GitHubAnalysis {
  repository: string;
  info: GitHubRepoInfo;
  metrics?: {
    total_files?: number;
    code_quality?: string;
    documentation_coverage?: number;
  };
}

export interface GitHubResponse {
  repo?: string;
  info?: GitHubRepoInfo;
  auth_url?: string;
  error?: string;
}
