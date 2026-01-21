import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { GitPullRequest, Upload, Loader, CheckCircle, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PRSubmit = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    repo_name: '',
    branch_name: '',
    pr_number: '',
    author: '',
    title: '',
    description: '',
    diff_content: 'MOCK'
  });
  
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [prId, setPrId] = useState('');
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);
    
    try {
      // Step 1: Submit PR
      const submitResponse = await axios.post(`${API}/pr/submit`, {
        ...formData,
        pr_number: formData.pr_number ? parseInt(formData.pr_number) : null
      });
      
      const newPrId = submitResponse.data.pr_id;
      setPrId(newPrId);
      setSuccess(true);
      setLoading(false);
      setAnalyzing(true);
      
      // Step 2: Trigger analysis
      await axios.post(`${API}/pr/${newPrId}/analyze`);
      
      setAnalyzing(false);
      
      // Navigate to PR detail page
      setTimeout(() => {
        navigate(`/pr/${newPrId}`);
      }, 1500);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit PR');
      setLoading(false);
      setAnalyzing(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto px-4 py-8" data-testid="pr-submit-page">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center space-x-3 mb-6">
          <GitPullRequest className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900" data-testid="page-title">Submit Pull Request for Analysis</h1>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> Currently using mock data for demo purposes. 
            In production, this will integrate with GitHub MCP to fetch actual PR data.
          </p>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center space-x-2" data-testid="error-message">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </div>
        )}
        
        {success && !analyzing && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-center space-x-2" data-testid="success-message">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <p className="text-green-800">PR submitted and analyzed successfully! Redirecting...</p>
          </div>
        )}
        
        {analyzing && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 flex items-center space-x-2" data-testid="analyzing-message">
            <Loader className="w-5 h-5 text-yellow-600 animate-spin" />
            <p className="text-yellow-800">Running R³ Agent analysis... This may take a moment.</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="repo_name">
                Repository Name *
              </label>
              <input
                type="text"
                id="repo_name"
                name="repo_name"
                data-testid="input-repo-name"
                value={formData.repo_name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., myorg/myrepo"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="branch_name">
                Branch Name *
              </label>
              <input
                type="text"
                id="branch_name"
                name="branch_name"
                data-testid="input-branch-name"
                value={formData.branch_name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., feature/payment-gateway"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="pr_number">
                PR Number
              </label>
              <input
                type="number"
                id="pr_number"
                name="pr_number"
                data-testid="input-pr-number"
                value={formData.pr_number}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., 1234"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="author">
                Author *
              </label>
              <input
                type="text"
                id="author"
                name="author"
                data-testid="input-author"
                value={formData.author}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., @johndoe"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="title">
              PR Title *
            </label>
            <input
              type="text"
              id="title"
              name="title"
              data-testid="input-title"
              value={formData.title}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Add payment gateway integration"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              data-testid="input-description"
              value={formData.description}
              onChange={handleChange}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe the changes in this PR..."
            />
          </div>
          
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              data-testid="btn-cancel"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || analyzing}
              data-testid="btn-submit"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading || analyzing ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>{analyzing ? 'Analyzing...' : 'Submitting...'}</span>
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  <span>Submit & Analyze</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PRSubmit;
