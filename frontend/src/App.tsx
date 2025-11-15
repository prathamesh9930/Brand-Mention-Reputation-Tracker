import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'
import BrandManagement from './components/BrandManagement'
import AlertsPanel from './components/AlertsPanel'
import { useWebSocket } from './hooks/useWebSocket'

function App() {
  const [selectedBrandId, setSelectedBrandId] = useState<number | null>(null)
  
  // Initialize WebSocket connection
  useWebSocket(selectedBrandId)

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route 
              path="/" 
              element={
                <Dashboard 
                  selectedBrandId={selectedBrandId} 
                  setSelectedBrandId={setSelectedBrandId} 
                />
              } 
            />
            <Route path="/brands" element={<BrandManagement />} />
            <Route 
              path="/alerts" 
              element={
                <AlertsPanel 
                  selectedBrandId={selectedBrandId}
                  setSelectedBrandId={setSelectedBrandId}
                />
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App