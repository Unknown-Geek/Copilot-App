
import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-gray-800 text-white">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="text-xl font-bold">
            Code Documentation Generator
          </Link>
          <div className="flex space-x-4">
            <Link to="/" className="hover:text-gray-300">
              Dashboard
            </Link>
            <button className="hover:text-gray-300">
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;