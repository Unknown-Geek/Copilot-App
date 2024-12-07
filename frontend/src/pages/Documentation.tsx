
import React from 'react';

export const Documentation = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Documentation</h1>
      <div className="prose max-w-none">
        <h2>Getting Started</h2>
        <p>Learn how to use the code documentation generator...</p>
        
        <h2>Features</h2>
        <ul>
          <li>Automatic code analysis</li>
          <li>Multiple language support</li>
          <li>Custom documentation templates</li>
        </ul>
        
        <h2>API Reference</h2>
        <p>Documentation for available API endpoints...</p>
      </div>
    </div>
  )
}

export default Documentation;