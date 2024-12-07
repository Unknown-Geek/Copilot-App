
import React from 'react';
import { Link } from 'react-router-dom';

const ProjectCard = ({ project }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-2">{project.name}</h2>
      <p className="text-gray-600 mb-4">{project.description}</p>
      <div className="flex justify-between items-center">
        <span className="text-sm text-gray-500">
          Last updated: {new Date(project.updatedAt).toLocaleDateString()}
        </span>
        <Link
          to={`/documentation/${project.id}`}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          View Docs
        </Link>
      </div>
    </div>
  );
};

export default ProjectCard;