import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, GitPullRequest, BarChart3, CheckCircle, AlertTriangle, XCircle, Zap, Target } from 'lucide-react';

const HomePage = () => {
  const navigate = useNavigate();
  
  const features = [
    {
      icon: GitPullRequest,
      title: 'PR Risk Analysis',
      description: 'Automated static code analysis and risk scoring for every pull request',
      color: 'blue'
    },
    {
      icon: Zap,
      title: 'AI-Powered Test Generation',
      description: 'Generate comprehensive unit tests using GPT-4o for better coverage',
      color: 'yellow'
    },
    {
      icon: Target,
      title: 'Smart Mitigations',
      description: 'Context-aware recommendations with human-in-the-loop approvals',
      color: 'green'
    },
    {
      icon: BarChart3,
      title: 'Release Train Tracking',
      description: 'Monitor cumulative risk across release branches',
      color: 'purple'
    }
  ];
  
  const stats = [
    { label: 'Fewer Incidents', value: '15-25%', icon: CheckCircle, color: 'text-green-500' },
    { label: 'Time Saved', value: '40%', icon: Zap, color: 'text-yellow-500' },
    { label: 'CI Efficiency', value: '30%', icon: Target, color: 'text-blue-500' },
  ];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 py-20" data-testid="hero-section">
        <div className="text-center mb-16">
          <div className="flex items-center justify-center space-x-3 mb-6">
            <Shield className="w-16 h-16 text-blue-400" data-testid="hero-logo" />
            <h1 className="text-6xl font-bold text-white" data-testid="hero-title">
              Release Risk Radar
            </h1>
          </div>
          <div className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg text-lg mb-6">
            R³ Agent - Predict & Mitigate Release Risk
          </div>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8" data-testid="hero-description">
            An engineering productivity agent that analyzes code changes, generates tests, 
            and recommends targeted actions to reduce release risk. Built with LangGraph and Azure OpenAI.
          </p>
          
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/submit-pr')}
              data-testid="cta-submit-pr"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold flex items-center space-x-2 transition shadow-lg"
            >
              <GitPullRequest className="w-6 h-6" />
              <span>Submit a PR</span>
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              data-testid="cta-view-dashboard"
              className="bg-gray-700 hover:bg-gray-600 text-white px-8 py-4 rounded-lg text-lg font-semibold flex items-center space-x-2 transition"
            >
              <BarChart3 className="w-6 h-6" />
              <span>View Dashboard</span>
            </button>
          </div>
        </div>
        
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20" data-testid="stats-section">
          {stats.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <div key={idx} className="bg-gray-800 bg-opacity-50 backdrop-blur-sm rounded-xl p-6 text-center border border-gray-700">
                <Icon className={`w-12 h-12 mx-auto mb-3 ${stat.color}`} />
                <div className="text-4xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-gray-300">{stat.label}</div>
              </div>
            );
          })}
        </div>
        
        {/* Features */}
        <div className="mb-20" data-testid="features-section">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Core Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div key={idx} className="bg-gray-800 bg-opacity-50 backdrop-blur-sm rounded-xl p-8 border border-gray-700 hover:border-blue-500 transition">
                  <Icon className={`w-12 h-12 mb-4 text-${feature.color}-400`} />
                  <h3 className="text-2xl font-bold text-white mb-3">{feature.title}</h3>
                  <p className="text-gray-300 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
        
        {/* How it Works */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm rounded-xl p-8 border border-gray-700" data-testid="how-it-works">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">How R³ Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div className="text-center">
              <div className="bg-blue-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-white font-bold">1</div>
              <p className="text-gray-300 text-sm">Submit PR</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-white font-bold">2</div>
              <p className="text-gray-300 text-sm">Analyze Code</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-white font-bold">3</div>
              <p className="text-gray-300 text-sm">Score Risk</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-white font-bold">4</div>
              <p className="text-gray-300 text-sm">Generate Tests</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-white font-bold">5</div>
              <p className="text-gray-300 text-sm">Recommend Actions</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-white font-bold">6</div>
              <p className="text-gray-300 text-sm">Human Approval</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
