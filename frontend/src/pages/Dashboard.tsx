
import { useState } from 'react'
import { CodeEditor } from '../components/CodeEditor'

export const Dashboard = () => {
  const [code, setCode] = useState('')
  const [docs, setDocs] = useState('')

  const generateDocs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language: 'python' })
      })
      const data = await response.json()
      setDocs(data.documentation)
    } catch (error) {
      console.error('Error:', error)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Code Documentation Generator</h1>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <CodeEditor value={code} onChange={setCode} />
          <button 
            onClick={generateDocs}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Generate Documentation
          </button>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <pre className="whitespace-pre-wrap">{docs}</pre>
        </div>
      </div>
    </div>
  )
}