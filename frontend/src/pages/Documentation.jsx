
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';

const Documentation = () => {
  const { id } = useParams();
  const [documentation, setDocumentation] = useState(null);

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

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        {documentation ? (
          <div className="bg-white rounded-lg shadow p-6">
            <h1 className="text-3xl font-bold mb-4">{documentation.projectName}</h1>
            <div className="documentation-content">
              {/* Render documentation content here */}
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