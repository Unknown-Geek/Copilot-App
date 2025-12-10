/**
 * Webview panel management for documentation preview
 */

import * as vscode from 'vscode';
import { Documentation, CodeBlock } from './types';

let currentPanel: vscode.WebviewPanel | undefined;
let currentDocumentation: string | undefined;

/**
 * Show documentation in a webview panel
 */
export function showDocumentationPreview(
    context: vscode.ExtensionContext,
    content: string | Documentation,
    title: string = 'Documentation Preview'
): vscode.WebviewPanel {
    const column = vscode.ViewColumn.Beside;

    // Reuse existing panel if available
    if (currentPanel) {
        currentPanel.reveal(column);
    } else {
        currentPanel = vscode.window.createWebviewPanel(
            'docgenPreview',
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
                currentPanel = undefined;
                currentDocumentation = undefined;
            },
            null,
            context.subscriptions
        );
    }

    // Handle string or Documentation object
    let documentationHtml: string;
    if (typeof content === 'string') {
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

/**
 * Get the current documentation content
 */
export function getCurrentDocumentation(): string | undefined {
    return currentDocumentation;
}

/**
 * Update the webview with new content
 */
export function updateDocumentationPreview(content: string | Documentation, title?: string): void {
    if (!currentPanel) {
        return;
    }

    let documentationHtml: string;
    if (typeof content === 'string') {
        documentationHtml = formatMarkdownContent(content);
        currentDocumentation = content;
    } else {
        documentationHtml = formatDocumentation(content);
        currentDocumentation = documentationToMarkdown(content);
    }

    currentPanel.webview.html = getWebviewContent(documentationHtml, title || currentPanel.title);
    if (title) {
        currentPanel.title = title;
    }
}

/**
 * Format a Documentation object to HTML
 */
function formatDocumentation(doc: Documentation): string {
    let html = `<h1>${escapeHtml(doc.title)}</h1>`;
    html += `<p class="description">${escapeHtml(doc.description)}</p>`;
    html += `<p class="meta">Language: ${escapeHtml(doc.language)} | Generated: ${escapeHtml(doc.generated_at)}</p>`;

    if (doc.metrics) {
        html += '<div class="metrics">';
        html += '<h3>Metrics</h3>';
        html += '<ul>';
        for (const [key, value] of Object.entries(doc.metrics)) {
            html += `<li><strong>${escapeHtml(key.replace(/_/g, ' '))}:</strong> ${escapeHtml(String(value))}</li>`;
        }
        html += '</ul></div>';
    }

    if (doc.code_blocks && doc.code_blocks.length > 0) {
        html += '<h2>Code Blocks</h2>';
        for (const block of doc.code_blocks) {
            html += formatCodeBlock(block);
        }
    }

    return html;
}

/**
 * Format a code block to HTML with syntax highlighting placeholder
 */
function formatCodeBlock(block: CodeBlock): string {
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

/**
 * Format markdown content to HTML
 */
function formatMarkdownContent(markdown: string): string {
    // Basic markdown to HTML conversion
    let html = markdown
        // Headers
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // Bold and italic
        .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Code blocks
        .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
        // Inline code
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Line breaks
        .replace(/\n/g, '<br>');

    return `<div class="markdown-content">${html}</div>`;
}

/**
 * Convert Documentation object to markdown string
 */
function documentationToMarkdown(doc: Documentation): string {
    let md = `# ${doc.title}\n\n`;
    md += `${doc.description}\n\n`;
    md += `**Language:** ${doc.language}\n`;
    md += `**Generated:** ${doc.generated_at}\n\n`;

    if (doc.metrics) {
        md += '## Metrics\n\n';
        for (const [key, value] of Object.entries(doc.metrics)) {
            md += `- **${key.replace(/_/g, ' ')}:** ${value}\n`;
        }
        md += '\n';
    }

    if (doc.code_blocks && doc.code_blocks.length > 0) {
        md += '## Code Blocks\n\n';
        for (const block of doc.code_blocks) {
            md += `\`\`\`${block.language}\n${block.content}\n\`\`\`\n\n`;
        }
    }

    return md;
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text: string): string {
    const map: { [key: string]: string } = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
}

/**
 * Generate the complete webview HTML
 */
function getWebviewContent(content: string, title: string): string {
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
