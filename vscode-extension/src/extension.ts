/**
 * DocGen - Code Multilingual Documentation Generator
 * VS Code Extension Entry Point
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { generateDocumentation, translateText, analyzeCode, getConfig } from './api';
import { showDocumentationPreview, getCurrentDocumentation, updateDocumentationPreview } from './webview';
import { SUPPORTED_LANGUAGES, EXPORT_FORMATS, Documentation } from './types';

let statusBarItem: vscode.StatusBarItem;
let outputChannel: vscode.OutputChannel;

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('DocGen');
    log('DocGen extension activated');

    // Create status bar item
    const config = getConfig();
    if (config.showStatusBar) {
        statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        statusBarItem.text = '$(book) DocGen';
        statusBarItem.tooltip = 'Generate Documentation';
        statusBarItem.command = 'docgen.generateDocs';
        statusBarItem.show();
        context.subscriptions.push(statusBarItem);
    }

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('docgen.generateDocs', () => generateDocsCommand(context)),
        vscode.commands.registerCommand('docgen.translateDocs', () => translateDocsCommand(context)),
        vscode.commands.registerCommand('docgen.exportDocs', () => exportDocsCommand(context)),
        vscode.commands.registerCommand('docgen.analyzeCode', () => analyzeCodeCommand(context))
    );

    log('All commands registered');
}

/**
 * Generate Documentation command
 */
async function generateDocsCommand(context: vscode.ExtensionContext) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor. Open a file to generate documentation.');
        return;
    }

    const document = editor.document;
    const code = document.getText();
    const language = document.languageId;
    const fileName = path.basename(document.fileName);

    if (!code.trim()) {
        vscode.window.showWarningMessage('The current file is empty.');
        return;
    }

    log(`Generating documentation for ${fileName} (${language})`);
    setStatus('$(sync~spin) Generating...');

    try {
        const response = await generateDocumentation(code, language, {
            title: `Documentation: ${fileName}`,
            format: 'markdown'
        });

        if (response.status === 'error') {
            throw new Error(response.error || 'Unknown error occurred');
        }

        log('Documentation generated successfully');
        setStatus('$(check) Generated');

        // Show in webview
        const content = typeof response.documentation === 'string' 
            ? response.documentation 
            : response.documentation as Documentation;
        
        showDocumentationPreview(context, content, `Docs: ${fileName}`);

        vscode.window.showInformationMessage('Documentation generated successfully!');

        // Reset status after delay
        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    } catch (error) {
        const message = error instanceof Error ? error.message : 'Failed to generate documentation';
        log(`Error: ${message}`, 'error');
        setStatus('$(error) Error');
        vscode.window.showErrorMessage(`DocGen: ${message}`);
        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    }
}

/**
 * Translate Documentation command
 */
async function translateDocsCommand(context: vscode.ExtensionContext) {
    const currentDoc = getCurrentDocumentation();
    
    if (!currentDoc) {
        // If no doc in preview, use current editor content
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No documentation to translate. Generate documentation first or open a file.');
            return;
        }
    }

    // Show language picker
    const languageItems = SUPPORTED_LANGUAGES.map(lang => ({
        label: lang.name,
        description: lang.code,
        code: lang.code
    }));

    const selected = await vscode.window.showQuickPick(languageItems, {
        placeHolder: 'Select target language for translation',
        title: 'Translate Documentation'
    });

    if (!selected) {
        return; // User cancelled
    }

    log(`Translating to ${selected.label}`);
    setStatus('$(sync~spin) Translating...');

    try {
        const textToTranslate = currentDoc || vscode.window.activeTextEditor?.document.getText() || '';
        
        const response = await translateText(textToTranslate, selected.code);

        if (response.status === 'error') {
            throw new Error(response.error || 'Translation failed');
        }

        log(`Translation completed (confidence: ${response.confidence})`);
        setStatus('$(check) Translated');

        // Update or show webview with translated content
        if (response.translated_text) {
            showDocumentationPreview(context, response.translated_text, `Translated (${selected.label})`);
        }

        vscode.window.showInformationMessage(
            `Documentation translated to ${selected.label}` +
            (response.detected_language ? ` (from ${response.detected_language})` : '')
        );

        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    } catch (error) {
        const message = error instanceof Error ? error.message : 'Translation failed';
        log(`Error: ${message}`, 'error');
        setStatus('$(error) Error');
        vscode.window.showErrorMessage(`DocGen: ${message}`);
        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    }
}

/**
 * Export Documentation command
 */
async function exportDocsCommand(context: vscode.ExtensionContext) {
    const currentDoc = getCurrentDocumentation();
    
    if (!currentDoc) {
        vscode.window.showWarningMessage('No documentation to export. Generate documentation first.');
        return;
    }

    // Show format picker
    const formatItems = EXPORT_FORMATS.map(f => ({
        label: f.label,
        id: f.id
    }));

    const selected = await vscode.window.showQuickPick(formatItems, {
        placeHolder: 'Select export format',
        title: 'Export Documentation'
    });

    if (!selected) {
        return; // User cancelled
    }

    // Get save location
    const extension = selected.id === 'markdown' ? 'md' : selected.id;
    const defaultUri = vscode.Uri.file(
        path.join(
            vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '',
            `documentation.${extension}`
        )
    );

    const saveUri = await vscode.window.showSaveDialog({
        defaultUri,
        filters: {
            [selected.label]: [extension]
        },
        title: 'Save Documentation'
    });

    if (!saveUri) {
        return; // User cancelled
    }

    log(`Exporting documentation as ${selected.id}`);
    setStatus('$(sync~spin) Exporting...');

    try {
        let content = currentDoc;

        // Convert content based on format
        if (selected.id === 'html') {
            content = convertToHtml(currentDoc);
        } else if (selected.id === 'json') {
            content = JSON.stringify({ 
                documentation: currentDoc,
                exported_at: new Date().toISOString(),
                format: 'json'
            }, null, 2);
        }

        // Write file
        fs.writeFileSync(saveUri.fsPath, content, 'utf8');

        log(`Exported to ${saveUri.fsPath}`);
        setStatus('$(check) Exported');

        const openFile = await vscode.window.showInformationMessage(
            `Documentation exported to ${path.basename(saveUri.fsPath)}`,
            'Open File'
        );

        if (openFile === 'Open File') {
            vscode.window.showTextDocument(saveUri);
        }

        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    } catch (error) {
        const message = error instanceof Error ? error.message : 'Export failed';
        log(`Error: ${message}`, 'error');
        setStatus('$(error) Error');
        vscode.window.showErrorMessage(`DocGen: ${message}`);
        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    }
}

/**
 * Analyze Code command
 */
async function analyzeCodeCommand(context: vscode.ExtensionContext) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor. Open a file to analyze.');
        return;
    }

    const document = editor.document;
    const selection = editor.selection;
    
    // Use selection if available, otherwise entire document
    const code = selection.isEmpty 
        ? document.getText() 
        : document.getText(selection);
    
    const language = document.languageId;
    const fileName = path.basename(document.fileName);

    if (!code.trim()) {
        vscode.window.showWarningMessage('No code to analyze.');
        return;
    }

    log(`Analyzing code in ${fileName}`);
    setStatus('$(sync~spin) Analyzing...');

    try {
        const response = await analyzeCode(code, language);

        if (response.status === 'error') {
            throw new Error(response.error || 'Analysis failed');
        }

        log('Code analysis completed');
        setStatus('$(check) Analyzed');

        // Format and show results
        const analysisContent = formatAnalysisResult(response, fileName);
        showDocumentationPreview(context, analysisContent, `Analysis: ${fileName}`);

        vscode.window.showInformationMessage('Code analysis completed!');
        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    } catch (error) {
        const message = error instanceof Error ? error.message : 'Analysis failed';
        log(`Error: ${message}`, 'error');
        setStatus('$(error) Error');
        vscode.window.showErrorMessage(`DocGen: ${message}`);
        setTimeout(() => setStatus('$(book) DocGen'), 3000);
    }
}

/**
 * Format analysis result for display
 */
function formatAnalysisResult(response: any, fileName: string): string {
    let md = `# Code Analysis: ${fileName}\n\n`;
    
    if (response.sentiment) {
        md += `## Sentiment\n\n`;
        md += `**Overall:** ${response.sentiment}\n\n`;
        
        if (response.confidence_scores) {
            md += `### Confidence Scores\n\n`;
            md += `- Positive: ${(response.confidence_scores.positive * 100).toFixed(1)}%\n`;
            md += `- Neutral: ${(response.confidence_scores.neutral * 100).toFixed(1)}%\n`;
            md += `- Negative: ${(response.confidence_scores.negative * 100).toFixed(1)}%\n\n`;
        }
    }

    if (response.language) {
        md += `## Detected Language\n\n`;
        md += `${response.language}\n\n`;
    }

    // Add any additional metrics
    for (const [key, value] of Object.entries(response)) {
        if (!['status', 'sentiment', 'confidence_scores', 'language', 'error'].includes(key)) {
            md += `## ${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}\n\n`;
            md += `${JSON.stringify(value, null, 2)}\n\n`;
        }
    }

    return md;
}

/**
 * Convert markdown to basic HTML
 */
function convertToHtml(markdown: string): string {
    const bodyContent = markdown
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>\n');

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

/**
 * Update status bar
 */
function setStatus(text: string) {
    if (statusBarItem) {
        statusBarItem.text = text;
    }
}

/**
 * Log to output channel
 */
function log(message: string, level: 'info' | 'error' | 'warn' = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = level === 'error' ? '[ERROR]' : level === 'warn' ? '[WARN]' : '[INFO]';
    outputChannel.appendLine(`${timestamp} ${prefix} ${message}`);
}

/**
 * Extension deactivation
 */
export function deactivate() {
    if (outputChannel) {
        outputChannel.dispose();
    }
}