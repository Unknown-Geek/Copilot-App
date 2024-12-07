import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { Documentation } from './pages/Documentation'
import { Login } from './pages/Login'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-3">
            <div className="flex gap-4">
              <Link to="/" className="text-gray-700 hover:text-blue-600">Dashboard</Link>
              <Link to="/docs" className="text-gray-700 hover:text-blue-600">Documentation</Link>
              <Link to="/login" className="text-gray-700 hover:text-blue-600">Login</Link>
            </div>
          </div>
        </nav>

        <main className="container mx-auto py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/docs" element={<Documentation />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App