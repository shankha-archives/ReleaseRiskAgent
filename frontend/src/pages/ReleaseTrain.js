import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Workflow, TrendingUp, GitBranch, AlertTriangle, CheckCircle, XCircle, Plus, Loader } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReleaseTrain = () => {
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    release_version: '',
    branch: '',
    pr_ids: []
  });
  
  useEffect(() => {
    fetchReleases();
  }, []);
  
  const fetchReleases = async () => {
    try {
      const response = await axios.get(`${API}/release/list`);
      setReleases(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load releases:', err);
      setLoading(false);
    }
  };
  
  const handleCreateRelease = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/release/create`, {
        ...formData,
        cumulative_risk_score: 0,
        status: 'planning'
      });
      setShowCreateForm(false);
      setFormData({ release_version: '', branch: '', pr_ids: [] });
      fetchReleases();
    } catch (err) {
      console.error('Failed to create release:', err);
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen" data-testid="loading-state">
        <Loader className="w-12 h-12 text-blue-600 animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8" data-testid="release-train-page">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900" data-testid="page-title">Release Train Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor cumulative risk across release branches</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          data-testid="btn-create-release"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition"
        >
          <Plus className="w-5 h-5" />
          <span>New Release Train</span>
        </button>
      </div>
      
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8" data-testid="create-form">
          <h2 className="text-xl font-bold mb-4">Create Release Train</h2>
          <form onSubmit={handleCreateRelease} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Release Version
              </label>
              <input
                type="text"
                value={formData.release_version}
                onChange={(e) => setFormData({ ...formData, release_version: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., v2.5.0"
                data-testid="input-version"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Branch Name
              </label>
              <input
                type="text"
                value={formData.branch}
                onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., release/2.5"
                data-testid="input-branch"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                data-testid="btn-submit-release"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold"
              >
                Create Release
              </button>
            </div>
          </form>
        </div>
      )}
      
      {releases.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center" data-testid="empty-state">
          <Workflow className="w-20 h-20 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Release Trains Yet</h2>
          <p className="text-gray-600 mb-6">Create your first release train to track cumulative PR risk</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold inline-flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Create Release Train</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {releases.map((release, idx) => (
            <ReleaseCard key={release.id} release={release} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
};

const ReleaseCard = ({ release, index }) => {
  const [details, setDetails] = useState(null);
  const [expanded, setExpanded] = useState(false);
  
  const fetchDetails = async () => {
    if (details) {
      setExpanded(!expanded);
      return;
    }
    
    try {
      const response = await axios.get(`${API}/release/${release.id}`);
      setDetails(response.data);
      setExpanded(true);
    } catch (err) {
      console.error('Failed to load release details:', err);
    }
  };
  
  const getRiskLevel = (score) => {
    if (score < 0.3) return { level: 'low', color: 'green', icon: CheckCircle };
    if (score < 0.6) return { level: 'medium', color: 'yellow', icon: AlertTriangle };
    return { level: 'high', color: 'red', icon: XCircle };
  };
  
  const risk = getRiskLevel(release.cumulative_risk_score || 0);
  const RiskIcon = risk.icon;
  
  const statusColors = {
    planning: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-green-100 text-green-800'
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden" data-testid={`release-card-${index}`}>
      <div 
        className="p-6 cursor-pointer hover:bg-gray-50 transition"
        onClick={fetchDetails}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <Workflow className="w-6 h-6 text-blue-600" />
              <h3 className="text-xl font-bold text-gray-900" data-testid={`release-version-${index}`}>
                {release.release_version}
              </h3>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColors[release.status]}`}>
                {release.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <GitBranch className="w-4 h-4" />
                <span>{release.branch}</span>
              </div>
              <span>•</span>
              <span>{release.pr_ids?.length || 0} PRs</span>
              <span>•</span>
              <span>Created {new Date(release.created_at).toLocaleDateString()}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600 mb-1">Cumulative Risk</p>
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg bg-${risk.color}-100 text-${risk.color}-800`}>
                <RiskIcon className="w-5 h-5" />
                <span className="font-bold">{(release.cumulative_risk_score || 0).toFixed(3)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {expanded && details && (
        <div className="border-t border-gray-200 p-6 bg-gray-50" data-testid={`release-details-${index}`}>
          <h4 className="font-semibold text-gray-900 mb-4">PR Risk Breakdown</h4>
          {details.pr_analyses?.length === 0 ? (
            <p className="text-gray-600 text-center py-4">No PRs in this release yet</p>
          ) : (
            <div className="space-y-3">
              {details.pr_analyses?.map((pr, prIdx) => {
                const prRisk = getRiskLevel(pr.risk_score.score);
                const PRIcon = prRisk.icon;
                return (
                  <div key={pr.pr_id} className="bg-white rounded p-4 flex items-center justify-between">
                    <span className="text-gray-900">PR #{pr.pr_id.slice(0, 8)}</span>
                    <div className={`flex items-center space-x-2 px-3 py-1 rounded bg-${prRisk.color}-100 text-${prRisk.color}-800`}>
                      <PRIcon className="w-4 h-4" />
                      <span className="font-semibold text-sm">{pr.risk_score.score.toFixed(3)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ReleaseTrain;
