import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import TreeView from '../components/TreeView';
import SearchBar from '../components/SearchBar';
import { getDocumentation, exportDocumentation } from '../services/api';

const Documentation = () => {
  const { id } = useParams();
  const [documentation, setDocumentation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [exportFormat, setExportFormat] = useState('html');

  useEffect(() => {
    fetchDocumentation();
  }, [id]);

  const fetchDocumentation = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/documentation/${id}`);
      const data = await response.json();
      setDocumentation(data);
    } catch (error) {
      console.error('Error fetching documentation:', error);
    }
  };

  const handleExport = async () => {
    try {
      const result = await exportDocumentation(id, exportFormat);
      // Handle export result
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-4">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
          <div className="flex items-center gap-2">
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              className="border rounded p-2"
            >
              <option value="html">HTML</option>
              <option value="pdf">PDF</option>
              <option value="md">Markdown</option>
            </select>
            <button
              onClick={handleExport}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              Export
            </button>
          </div>
        </div>
        {documentation ? (
          <div className="grid grid-cols-12 gap-4">
            <div className="col-span-3">
              <TreeView structure={documentation.structure} />
            </div>
            <div className="col-span-9 bg-white rounded-lg shadow p-6">
              <h1 className="text-3xl font-bold mb-4">{documentation.projectName}</h1>
              <div className="documentation-content">
                {documentation.content}
              </div>
            </div>
          </div>
        ) : (
          <div>Loading...</div>
        )}
      </div>
    </div>
  );
};

export default Documentation;