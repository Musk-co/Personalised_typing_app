/**
 * Root App component
 */

import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@hooks/useAuth'

// Pages
import Home from '@pages/Home'
import TypingTest from '@pages/TypingTest'
import Dashboard from '@pages/Dashboard'
import Settings from '@pages/Settings'
import Login from '@pages/Login'
import Register from '@pages/Register'

// Components
import Header from '@components/Common/Header'
import Navbar from '@components/Common/Navbar'

import './styles/globals.css'

function App() {
  const { isAuthenticated, checkAuth } = useAuth()

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <Header />
        <Navbar />

        <main className="flex-1 container mx-auto px-4 py-8">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
            <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />

            {/* Protected routes */}
            <Route
              path="/typing-test"
              element={isAuthenticated ? <TypingTest /> : <Navigate to="/login" />}
            />
            <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
            <Route path="/settings" element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
