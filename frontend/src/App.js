import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Shield, GitPullRequest, BarChart3, Workflow, Home } from 'lucide-react';
import '@/App.css';

import Dashboard from './pages/Dashboard';
import PRSubmit from './pages/PRSubmit';
import PRDetail from './pages/PRDetail';
import ReleaseTrain from './pages/ReleaseTrain';
import HomePage from './pages/HomePage';

const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/dashboard', icon: BarChart3, label: 'Dashboard' },
    { path: '/submit-pr', icon: GitPullRequest, label: 'Submit PR' },
    { path: '/release-train', icon: Workflow, label: 'Release Train' },
  ];
  
  return (
    <nav className="bg-gray-900 text-white shadow-lg" data-testid="main-navigation">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <Shield className="w-8 h-8 text-blue-400" data-testid="app-logo" />
            <span className="text-xl font-bold" data-testid="app-title">Release Risk Radar</span>
            <span className="text-xs text-blue-300 bg-blue-900 px-2 py-1 rounded">R³</span>
          </div>
          
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`nav-link-${item.label.toLowerCase().replace(' ', '-')}`}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

function App() {
  return (
    <div className="App min-h-screen bg-gray-50">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/submit-pr" element={<PRSubmit />} />
          <Route path="/pr/:prId" element={<PRDetail />} />
          <Route path="/release-train" element={<ReleaseTrain />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
