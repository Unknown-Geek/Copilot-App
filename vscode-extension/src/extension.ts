import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('docgen.generateDocs', async () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const code = editor.document.getText();
            try {
                const response = await fetch('http://localhost:5000/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        code,
                        language: editor.document.languageId
                    })
                });
                const data = await response.json();
                
                // Show documentation in a new editor
                const doc = await vscode.workspace.openTextDocument({
                    content: data.documentation,
                    language: 'markdown'
                });
                await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            } catch (error) {
                vscode.window.showErrorMessage('Failed to generate documentation');
                console.error('Error generating documentation:', error);
            }
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}