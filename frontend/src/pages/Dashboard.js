import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle, XCircle, GitPullRequest, Loader, ExternalLink } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RiskBadge = ({ level, score }) => {
  const configs = {
    high: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300', icon: XCircle },
    medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300', icon: AlertTriangle },
    low: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300', icon: CheckCircle }
  };
  
  const config = configs[level] || configs.low;
  const Icon = config.icon;
  
  return (
    <div className={`flex items-center space-x-2 px-3 py-1 rounded-full border ${config.bg} ${config.text} ${config.border}`} data-testid={`risk-badge-${level}`}>
      <Icon className="w-4 h-4" />
      <span className="font-semibold uppercase text-xs">{level}</span>
      <span className="text-xs">({score})</span>
    </div>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    fetchDashboardData();
  }, []);
  
  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load dashboard data');
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen" data-testid="loading-state">
        <Loader className="w-12 h-12 text-blue-600 animate-spin" />
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4" data-testid="error-state">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }
  
  const riskDistribution = stats?.risk_distribution || { high: 0, medium: 0, low: 0 };
  const total = stats?.total_prs || 0;
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8" data-testid="dashboard-page">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900" data-testid="page-title">PR Analysis Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor risk across all analyzed pull requests</p>
        </div>
        <button
          onClick={() => navigate('/submit-pr')}
          data-testid="btn-new-pr"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition"
        >
          <GitPullRequest className="w-5 h-5" />
          <span>New PR Analysis</span>
        </button>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8" data-testid="stats-cards">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Total PRs</p>
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900" data-testid="stat-total-prs">{total}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">High Risk</p>
            <XCircle className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-3xl font-bold text-red-600" data-testid="stat-high-risk">{riskDistribution.high}</p>
          <p className="text-xs text-gray-500 mt-1">{total > 0 ? Math.round((riskDistribution.high / total) * 100) : 0}% of total</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Medium Risk</p>
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-yellow-600" data-testid="stat-medium-risk">{riskDistribution.medium}</p>
          <p className="text-xs text-gray-500 mt-1">{total > 0 ? Math.round((riskDistribution.medium / total) * 100) : 0}% of total</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Low Risk</p>
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-600" data-testid="stat-low-risk">{riskDistribution.low}</p>
          <p className="text-xs text-gray-500 mt-1">{total > 0 ? Math.round((riskDistribution.low / total) * 100) : 0}% of total</p>
        </div>
      </div>
      
      {/* Recent PRs */}
      <div className="bg-white rounded-lg shadow" data-testid="recent-prs-section">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Recent Analyses</h2>
        </div>
        
        {stats?.recent_analyses?.length === 0 ? (
          <div className="p-8 text-center" data-testid="empty-state">
            <GitPullRequest className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">No PRs analyzed yet</p>
            <button
              onClick={() => navigate('/submit-pr')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition"
            >
              Submit Your First PR
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {stats?.recent_analyses?.map((pr, idx) => (
              <div
                key={pr.pr_id}
                data-testid={`pr-item-${idx}`}
                className="p-6 hover:bg-gray-50 transition cursor-pointer"
                onClick={() => navigate(`/pr/${pr.pr_id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900" data-testid={`pr-title-${idx}`}>{pr.title}</h3>
                      <RiskBadge level={pr.risk_score.level} score={pr.risk_score.score.toFixed(2)} />
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{pr.repo_name}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(pr.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <ExternalLink className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
