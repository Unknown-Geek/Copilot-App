"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/extension.ts
var extension_exports = {};
__export(extension_exports, {
  activate: () => activate,
  deactivate: () => deactivate
});
module.exports = __toCommonJS(extension_exports);
var vscode3 = __toESM(require("vscode"));
var path = __toESM(require("path"));
var fs = __toESM(require("fs"));

// src/api.ts
var vscode = __toESM(require("vscode"));
function getConfig() {
  const config = vscode.workspace.getConfiguration("docgen");
  return {
    backendUrl: config.get("backendUrl", "http://localhost:5001"),
    defaultTargetLanguage: config.get("defaultTargetLanguage", "es"),
    defaultExportFormat: config.get("defaultExportFormat", "markdown"),
    showStatusBar: config.get("showStatusBar", true)
  };
}
async function apiRequest(endpoint, method = "GET", body) {
  const config = getConfig();
  const url = `${config.backendUrl}${endpoint}`;
  const options = {
    method,
    headers: {
      "Content-Type": "application/json"
    }
  };
  if (body) {
    options.body = JSON.stringify(body);
  }
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error(`Cannot connect to backend at ${config.backendUrl}. Is the server running?`);
    }
    throw error;
  }
}
async function generateDocumentation(code, language, options) {
  return apiRequest("/api/analyze/documentation/generate", "POST", {
    code,
    language,
    title: options?.title,
    description: options?.description,
    template: options?.template || "default",
    format: options?.format || "markdown"
  });
}
async function analyzeCode(code, language) {
  return apiRequest("/api/analyze", "POST", {
    code,
    language
  });
}
async function translateText(text, targetLanguage) {
  return apiRequest("/api/translate", "POST", {
    text,
    target_language: targetLanguage
  });
}

// src/webview.ts
var vscode2 = __toESM(require("vscode"));
var currentPanel;
var currentDocumentation;
function showDocumentationPreview(context, content, title = "Documentation Preview") {
  const column = vscode2.ViewColumn.Beside;
  if (currentPanel) {
    currentPanel.reveal(column);
  } else {
    currentPanel = vscode2.window.createWebviewPanel(
      "docgenPreview",
      title,
      column,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: []
      }
    );
    currentPanel.onDidDispose(
      () => {
        currentPanel = void 0;
        currentDocumentation = void 0;
      },
      null,
      context.subscriptions
    );
  }
  let documentationHtml;
  if (typeof content === "string") {
    documentationHtml = formatMarkdownContent(content);
    currentDocumentation = content;
  } else {
    documentationHtml = formatDocumentation(content);
    currentDocumentation = documentationToMarkdown(content);
  }
  currentPanel.webview.html = getWebviewContent(documentationHtml, title);
  currentPanel.title = title;
  return currentPanel;
}
function getCurrentDocumentation() {
  return currentDocumentation;
}
function formatDocumentation(doc) {
  let html = `<h1>${escapeHtml(doc.title)}</h1>`;
  html += `<p class="description">${escapeHtml(doc.description)}</p>`;
  html += `<p class="meta">Language: ${escapeHtml(doc.language)} | Generated: ${escapeHtml(doc.generated_at)}</p>`;
  if (doc.metrics) {
    html += '<div class="metrics">';
    html += "<h3>Metrics</h3>";
    html += "<ul>";
    for (const [key, value] of Object.entries(doc.metrics)) {
      html += `<li><strong>${escapeHtml(key.replace(/_/g, " "))}:</strong> ${escapeHtml(String(value))}</li>`;
    }
    html += "</ul></div>";
  }
  if (doc.code_blocks && doc.code_blocks.length > 0) {
    html += "<h2>Code Blocks</h2>";
    for (const block of doc.code_blocks) {
      html += formatCodeBlock(block);
    }
  }
  return html;
}
function formatCodeBlock(block) {
  return `
        <div class="code-block">
            <div class="code-header">
                <span class="language">${escapeHtml(block.language)}</span>
                <span class="line-number">Line ${block.line_number}</span>
            </div>
            <pre><code class="language-${escapeHtml(block.language)}">${escapeHtml(block.content)}</code></pre>
        </div>
    `;
}
function formatMarkdownContent(markdown) {
  let html = markdown.replace(/^### (.*$)/gim, "<h3>$1</h3>").replace(/^## (.*$)/gim, "<h2>$1</h2>").replace(/^# (.*$)/gim, "<h1>$1</h1>").replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/\*(.*?)\*/g, "<em>$1</em>").replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>').replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\n/g, "<br>");
  return `<div class="markdown-content">${html}</div>`;
}
function documentationToMarkdown(doc) {
  let md = `# ${doc.title}

`;
  md += `${doc.description}

`;
  md += `**Language:** ${doc.language}
`;
  md += `**Generated:** ${doc.generated_at}

`;
  if (doc.metrics) {
    md += "## Metrics\n\n";
    for (const [key, value] of Object.entries(doc.metrics)) {
      md += `- **${key.replace(/_/g, " ")}:** ${value}
`;
    }
    md += "\n";
  }
  if (doc.code_blocks && doc.code_blocks.length > 0) {
    md += "## Code Blocks\n\n";
    for (const block of doc.code_blocks) {
      md += `\`\`\`${block.language}
${block.content}
\`\`\`

`;
    }
  }
  return md;
}
function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}
function getWebviewContent(content, title) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(title)}</title>
    <style>
        :root {
            --bg-color: var(--vscode-editor-background);
            --text-color: var(--vscode-editor-foreground);
            --border-color: var(--vscode-panel-border);
            --code-bg: var(--vscode-textCodeBlock-background);
            --accent-color: var(--vscode-textLink-foreground);
            --header-bg: var(--vscode-sideBarSectionHeader-background);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
        }

        h1, h2, h3 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.3em;
        }

        h1 { font-size: 2em; color: var(--accent-color); }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; }

        p { margin-bottom: 1em; }

        .description {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .meta {
            font-size: 0.9em;
            opacity: 0.7;
            font-style: italic;
        }

        .metrics {
            background: var(--header-bg);
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }

        .metrics h3 {
            margin-top: 0;
            border-bottom: none;
        }

        .metrics ul {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }

        .metrics li {
            padding: 5px 10px;
            background: var(--bg-color);
            border-radius: 4px;
        }

        .code-block {
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }

        .code-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: var(--header-bg);
            font-size: 0.85em;
        }

        .language {
            font-weight: 600;
            color: var(--accent-color);
        }

        .line-number {
            opacity: 0.6;
        }

        pre {
            margin: 0;
            padding: 15px;
            overflow-x: auto;
            background: var(--code-bg);
        }

        code {
            font-family: var(--vscode-editor-font-family);
            font-size: var(--vscode-editor-font-size);
        }

        .markdown-content code {
            background: var(--code-bg);
            padding: 2px 6px;
            border-radius: 3px;
        }

        .markdown-content pre code {
            background: transparent;
            padding: 0;
        }

        strong { font-weight: 600; }
        em { font-style: italic; }
    </style>
</head>
<body>
    ${content}
</body>
</html>`;
}

// src/types.ts
var SUPPORTED_LANGUAGES = [
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
  { code: "ru", name: "Russian" }
];
var EXPORT_FORMATS = [
  { id: "markdown", label: "Markdown (.md)" },
  { id: "html", label: "HTML (.html)" },
  { id: "json", label: "JSON (.json)" }
];

// src/extension.ts
var statusBarItem;
var outputChannel;
function activate(context) {
  outputChannel = vscode3.window.createOutputChannel("DocGen");
  log("DocGen extension activated");
  const config = getConfig();
  if (config.showStatusBar) {
    statusBarItem = vscode3.window.createStatusBarItem(vscode3.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(book) DocGen";
    statusBarItem.tooltip = "Generate Documentation";
    statusBarItem.command = "docgen.generateDocs";
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
  }
  context.subscriptions.push(
    vscode3.commands.registerCommand("docgen.generateDocs", () => generateDocsCommand(context)),
    vscode3.commands.registerCommand("docgen.translateDocs", () => translateDocsCommand(context)),
    vscode3.commands.registerCommand("docgen.exportDocs", () => exportDocsCommand(context)),
    vscode3.commands.registerCommand("docgen.analyzeCode", () => analyzeCodeCommand(context))
  );
  log("All commands registered");
}
async function generateDocsCommand(context) {
  const editor = vscode3.window.activeTextEditor;
  if (!editor) {
    vscode3.window.showWarningMessage("No active editor. Open a file to generate documentation.");
    return;
  }
  const document = editor.document;
  const code = document.getText();
  const language = document.languageId;
  const fileName = path.basename(document.fileName);
  if (!code.trim()) {
    vscode3.window.showWarningMessage("The current file is empty.");
    return;
  }
  log(`Generating documentation for ${fileName} (${language})`);
  setStatus("$(sync~spin) Generating...");
  try {
    const response = await generateDocumentation(code, language, {
      title: `Documentation: ${fileName}`,
      format: "markdown"
    });
    if (response.status === "error") {
      throw new Error(response.error || "Unknown error occurred");
    }
    log("Documentation generated successfully");
    setStatus("$(check) Generated");
    const content = typeof response.documentation === "string" ? response.documentation : response.documentation;
    showDocumentationPreview(context, content, `Docs: ${fileName}`);
    vscode3.window.showInformationMessage("Documentation generated successfully!");
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to generate documentation";
    log(`Error: ${message}`, "error");
    setStatus("$(error) Error");
    vscode3.window.showErrorMessage(`DocGen: ${message}`);
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  }
}
async function translateDocsCommand(context) {
  const currentDoc = getCurrentDocumentation();
  if (!currentDoc) {
    const editor = vscode3.window.activeTextEditor;
    if (!editor) {
      vscode3.window.showWarningMessage("No documentation to translate. Generate documentation first or open a file.");
      return;
    }
  }
  const languageItems = SUPPORTED_LANGUAGES.map((lang) => ({
    label: lang.name,
    description: lang.code,
    code: lang.code
  }));
  const selected = await vscode3.window.showQuickPick(languageItems, {
    placeHolder: "Select target language for translation",
    title: "Translate Documentation"
  });
  if (!selected) {
    return;
  }
  log(`Translating to ${selected.label}`);
  setStatus("$(sync~spin) Translating...");
  try {
    const textToTranslate = currentDoc || vscode3.window.activeTextEditor?.document.getText() || "";
    const response = await translateText(textToTranslate, selected.code);
    if (response.status === "error") {
      throw new Error(response.error || "Translation failed");
    }
    log(`Translation completed (confidence: ${response.confidence})`);
    setStatus("$(check) Translated");
    if (response.translated_text) {
      showDocumentationPreview(context, response.translated_text, `Translated (${selected.label})`);
    }
    vscode3.window.showInformationMessage(
      `Documentation translated to ${selected.label}` + (response.detected_language ? ` (from ${response.detected_language})` : "")
    );
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Translation failed";
    log(`Error: ${message}`, "error");
    setStatus("$(error) Error");
    vscode3.window.showErrorMessage(`DocGen: ${message}`);
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  }
}
async function exportDocsCommand(context) {
  const currentDoc = getCurrentDocumentation();
  if (!currentDoc) {
    vscode3.window.showWarningMessage("No documentation to export. Generate documentation first.");
    return;
  }
  const formatItems = EXPORT_FORMATS.map((f) => ({
    label: f.label,
    id: f.id
  }));
  const selected = await vscode3.window.showQuickPick(formatItems, {
    placeHolder: "Select export format",
    title: "Export Documentation"
  });
  if (!selected) {
    return;
  }
  const extension = selected.id === "markdown" ? "md" : selected.id;
  const defaultUri = vscode3.Uri.file(
    path.join(
      vscode3.workspace.workspaceFolders?.[0]?.uri.fsPath || "",
      `documentation.${extension}`
    )
  );
  const saveUri = await vscode3.window.showSaveDialog({
    defaultUri,
    filters: {
      [selected.label]: [extension]
    },
    title: "Save Documentation"
  });
  if (!saveUri) {
    return;
  }
  log(`Exporting documentation as ${selected.id}`);
  setStatus("$(sync~spin) Exporting...");
  try {
    let content = currentDoc;
    if (selected.id === "html") {
      content = convertToHtml(currentDoc);
    } else if (selected.id === "json") {
      content = JSON.stringify({
        documentation: currentDoc,
        exported_at: (/* @__PURE__ */ new Date()).toISOString(),
        format: "json"
      }, null, 2);
    }
    fs.writeFileSync(saveUri.fsPath, content, "utf8");
    log(`Exported to ${saveUri.fsPath}`);
    setStatus("$(check) Exported");
    const openFile = await vscode3.window.showInformationMessage(
      `Documentation exported to ${path.basename(saveUri.fsPath)}`,
      "Open File"
    );
    if (openFile === "Open File") {
      vscode3.window.showTextDocument(saveUri);
    }
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Export failed";
    log(`Error: ${message}`, "error");
    setStatus("$(error) Error");
    vscode3.window.showErrorMessage(`DocGen: ${message}`);
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  }
}
async function analyzeCodeCommand(context) {
  const editor = vscode3.window.activeTextEditor;
  if (!editor) {
    vscode3.window.showWarningMessage("No active editor. Open a file to analyze.");
    return;
  }
  const document = editor.document;
  const selection = editor.selection;
  const code = selection.isEmpty ? document.getText() : document.getText(selection);
  const language = document.languageId;
  const fileName = path.basename(document.fileName);
  if (!code.trim()) {
    vscode3.window.showWarningMessage("No code to analyze.");
    return;
  }
  log(`Analyzing code in ${fileName}`);
  setStatus("$(sync~spin) Analyzing...");
  try {
    const response = await analyzeCode(code, language);
    if (response.status === "error") {
      throw new Error(response.error || "Analysis failed");
    }
    log("Code analysis completed");
    setStatus("$(check) Analyzed");
    const analysisContent = formatAnalysisResult(response, fileName);
    showDocumentationPreview(context, analysisContent, `Analysis: ${fileName}`);
    vscode3.window.showInformationMessage("Code analysis completed!");
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Analysis failed";
    log(`Error: ${message}`, "error");
    setStatus("$(error) Error");
    vscode3.window.showErrorMessage(`DocGen: ${message}`);
    setTimeout(() => setStatus("$(book) DocGen"), 3e3);
  }
}
function formatAnalysisResult(response, fileName) {
  let md = `# Code Analysis: ${fileName}

`;
  if (response.sentiment) {
    md += `## Sentiment

`;
    md += `**Overall:** ${response.sentiment}

`;
    if (response.confidence_scores) {
      md += `### Confidence Scores

`;
      md += `- Positive: ${(response.confidence_scores.positive * 100).toFixed(1)}%
`;
      md += `- Neutral: ${(response.confidence_scores.neutral * 100).toFixed(1)}%
`;
      md += `- Negative: ${(response.confidence_scores.negative * 100).toFixed(1)}%

`;
    }
  }
  if (response.language) {
    md += `## Detected Language

`;
    md += `${response.language}

`;
  }
  for (const [key, value] of Object.entries(response)) {
    if (!["status", "sentiment", "confidence_scores", "language", "error"].includes(key)) {
      md += `## ${key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}

`;
      md += `${JSON.stringify(value, null, 2)}

`;
    }
  }
  return md;
}
function convertToHtml(markdown) {
  const bodyContent = markdown.replace(/^### (.*$)/gim, "<h3>$1</h3>").replace(/^## (.*$)/gim, "<h2>$1</h2>").replace(/^# (.*$)/gim, "<h1>$1</h1>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/\*(.*?)\*/g, "<em>$1</em>").replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>').replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\n/g, "<br>\n");
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { margin-top: 1.5em; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        pre code { background: transparent; padding: 0; }
    </style>
</head>
<body>
${bodyContent}
</body>
</html>`;
}
function setStatus(text) {
  if (statusBarItem) {
    statusBarItem.text = text;
  }
}
function log(message, level = "info") {
  const timestamp = (/* @__PURE__ */ new Date()).toISOString();
  const prefix = level === "error" ? "[ERROR]" : level === "warn" ? "[WARN]" : "[INFO]";
  outputChannel.appendLine(`${timestamp} ${prefix} ${message}`);
}
function deactivate() {
  if (outputChannel) {
    outputChannel.dispose();
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  activate,
  deactivate
});
//# sourceMappingURL=extension.js.map
