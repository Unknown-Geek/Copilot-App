
import React from 'react';
import ReactMarkdown from 'react-markdown';

interface DocPreviewProps {
  documentation: {
    title: string;
    description: string;
    codeBlocks: Array<{
      content: string;
      language: string;
      lineNumber: number;
    }>;
  };
}

const DocPreview: React.FC<DocPreviewProps> = ({ documentation }) => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">{documentation.title}</h1>
      <ReactMarkdown className="prose">
        {documentation.description}
      </ReactMarkdown>
      {documentation.codeBlocks.map((block, index) => (
        <pre key={index} className="bg-gray-800 p-4 rounded-lg mt-4">
          <code className={`language-${block.language}`}>
            {block.content}
          </code>
        </pre>
      ))}
    </div>
  );
};

export default DocPreview;