import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  GitPullRequest, Loader, ArrowLeft, CheckCircle, XCircle, AlertTriangle,
  Code, TestTube, Shield, ListChecks, FileCode, AlertCircle
} from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

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
    <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${config.bg} ${config.text} ${config.border}`}>
      <Icon className="w-5 h-5" />
      <span className="font-bold uppercase">{level}</span>
      <span className="font-mono">({score})</span>
    </div>
  );
};

const SignalBar = ({ label, value, max = 1 }) => {
  const percentage = (value / max) * 100;
  const color = percentage > 60 ? 'bg-red-500' : percentage > 30 ? 'bg-yellow-500' : 'bg-green-500';
  
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-700 font-medium">{label}</span>
        <span className="text-gray-600 font-mono">{value.toFixed(3)}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
};

const PRDetail = () => {
  const { prId } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  
  useEffect(() => {
    fetchAnalysis();
  }, [prId]);
  
  const fetchAnalysis = async () => {
    try {
      const response = await axios.get(`${API}/pr/${prId}/analysis`);
      setAnalysis(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load PR analysis');
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
  
  if (error || !analysis) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4" data-testid="error-state">
          <p className="text-red-800">{error || 'Analysis not found'}</p>
        </div>
      </div>
    );
  }
  
  const tabs = [
    { id: 'overview', label: 'Overview', icon: GitPullRequest },
    { id: 'risk', label: 'Risk Analysis', icon: Shield },
    { id: 'static', label: 'Code Quality', icon: Code },
    { id: 'tests', label: 'Generated Tests', icon: TestTube },
    { id: 'mitigations', label: 'Mitigations', icon: ListChecks },
  ];
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8" data-testid="pr-detail-page">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          data-testid="btn-back"
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4 transition"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </button>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-2" data-testid="pr-title">{analysis.title}</h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span data-testid="pr-repo">{analysis.repo_name}</span>
                <span>•</span>
                <span data-testid="pr-branch">{analysis.branch_name}</span>
                <span>•</span>
                <span data-testid="pr-author">by {analysis.author}</span>
              </div>
            </div>
            <RiskBadge 
              level={analysis.risk_score.level} 
              score={analysis.risk_score.score.toFixed(2)} 
            />
          </div>
          
          <div className="border-t pt-4">
            <p className="text-gray-700" data-testid="risk-explanation">{analysis.risk_score.explanation}</p>
            {analysis.risk_score.citations?.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {analysis.risk_score.citations.map((citation, idx) => (
                  <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded" data-testid={`citation-${idx}`}>
                    {citation}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="border-b border-gray-200 flex" data-testid="tabs-navigation">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                data-testid={`tab-${tab.id}`}
                className={`flex-1 flex items-center justify-center space-x-2 px-6 py-4 font-medium transition ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
        
        <div className="p-6" data-testid="tab-content">
          {activeTab === 'overview' && <OverviewTab analysis={analysis} />}
          {activeTab === 'risk' && <RiskTab analysis={analysis} />}
          {activeTab === 'static' && <StaticAnalysisTab analysis={analysis} />}
          {activeTab === 'tests' && <TestsTab analysis={analysis} />}
          {activeTab === 'mitigations' && <MitigationsTab analysis={analysis} prId={prId} />}
        </div>
      </div>
    </div>
  );
};

const OverviewTab = ({ analysis }) => {
  return (
    <div data-testid="overview-tab">
      <h2 className="text-xl font-bold mb-4">Analysis Summary</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Risk Level</p>
          <p className="text-2xl font-bold text-gray-900">{analysis.risk_score.level.toUpperCase()}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Code Issues</p>
          <p className="text-2xl font-bold text-gray-900">
            {analysis.static_analysis.reduce((sum, sa) => sum + sa.issues.length, 0)}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Generated Tests</p>
          <p className="text-2xl font-bold text-gray-900">{analysis.test_cases.length}</p>
        </div>
      </div>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">Execution Trace</h3>
        <p className="text-sm text-blue-800 mb-2">Trace ID: <code className="bg-blue-100 px-2 py-1 rounded">{analysis.execution_trace_id}</code></p>
        <p className="text-xs text-blue-700">All analysis steps are fully auditable and traceable for compliance.</p>
      </div>
    </div>
  );
};

const RiskTab = ({ analysis }) => {
  const signals = analysis.risk_score.signals;
  
  return (
    <div data-testid="risk-tab">
      <h2 className="text-xl font-bold mb-4">Risk Signals Breakdown</h2>
      <p className="text-gray-600 mb-6">
        Risk score is calculated using a weighted formula across multiple signals:
      </p>
      
      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <SignalBar label="Code Churn" value={signals.churn} />
        <SignalBar label="Coverage Gap" value={signals.coverage_gap} />
        <SignalBar label="Incident Hotspot" value={signals.incident_hotspot} />
        <SignalBar label="Flake Proximity" value={signals.flake_proximity} />
        <SignalBar label="Diff Risk" value={signals.diff_risk} />
        <SignalBar label="Time Pressure" value={signals.time_pressure} />
      </div>
      
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>Confidence:</strong> {(analysis.risk_score.confidence * 100).toFixed(0)}%
        </p>
        <p className="text-xs text-yellow-700 mt-1">
          Risk signals are based on historical data and heuristics. Some data sources are currently mocked for demo purposes.
        </p>
      </div>
    </div>
  );
};

const StaticAnalysisTab = ({ analysis }) => {
  if (analysis.static_analysis.length === 0) {
    return (
      <div className="text-center py-8" data-testid="no-static-analysis">
        <FileCode className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-600">No static analysis results available</p>
      </div>
    );
  }
  
  return (
    <div data-testid="static-analysis-tab">
      <h2 className="text-xl font-bold mb-4">Code Quality Analysis</h2>
      
      {analysis.static_analysis.map((file, idx) => (
        <div key={idx} className="mb-6 border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-100 px-4 py-3 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900" data-testid={`file-path-${idx}`}>{file.file_path}</h3>
            <div className="flex space-x-4 text-sm text-gray-600 mt-1">
              <span>LOC: {file.loc}</span>
              <span>Complexity: {file.complexity_score.toFixed(2)}</span>
              <span>Maintainability: {file.maintainability_index.toFixed(1)}</span>
            </div>
          </div>
          
          {file.issues.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {file.issues.map((issue, issueIdx) => {
                const severityColors = {
                  error: 'text-red-600 bg-red-50',
                  warning: 'text-yellow-600 bg-yellow-50',
                  info: 'text-blue-600 bg-blue-50'
                };
                return (
                  <div key={issueIdx} className="p-4">
                    <div className="flex items-start space-x-3">
                      <span className={`px-2 py-1 rounded text-xs font-semibold uppercase ${severityColors[issue.severity]}`}>
                        {issue.severity}
                      </span>
                      <div className="flex-1">
                        <p className="text-gray-900 font-medium">{issue.message}</p>
                        <p className="text-sm text-gray-600 mt-1">Line {issue.line} • {issue.type}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-4 text-center text-gray-600">
              <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <p>No issues found</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

const TestsTab = ({ analysis }) => {
  if (analysis.test_cases.length === 0) {
    return (
      <div className="text-center py-8" data-testid="no-tests">
        <TestTube className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-600">No test cases generated</p>
      </div>
    );
  }
  
  return (
    <div data-testid="tests-tab">
      <h2 className="text-xl font-bold mb-4">AI-Generated Unit Tests</h2>
      <p className="text-gray-600 mb-6">
        Tests generated using Azure OpenAI GPT-4o. Review and integrate into your test suite.
      </p>
      
      {analysis.test_cases.map((test, idx) => (
        <div key={test.id} className="mb-6 border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-100 px-4 py-3 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-900" data-testid={`test-file-${idx}`}>{test.file_path}</h3>
                <p className="text-sm text-gray-600 mt-1">{test.description}</p>
              </div>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{test.test_type}</span>
            </div>
          </div>
          
          <div className="bg-gray-900 overflow-x-auto">
            <SyntaxHighlighter
              language="python"
              style={vscDarkPlus}
              customStyle={{ margin: 0, padding: '1rem' }}
            >
              {test.test_code}
            </SyntaxHighlighter>
          </div>
        </div>
      ))}
    </div>
  );
};

const MitigationsTab = ({ analysis, prId }) => {
  const [mitigations, setMitigations] = useState(analysis.mitigations);
  
  const handleApproval = async (mitigationId, action) => {
    try {
      await axios.post(`${API}/mitigation/approve`, {
        trace_id: analysis.execution_trace_id,
        mitigation_id: mitigationId,
        action: action,
        approver: 'current_user',
        comment: ''
      });
      
      // Update local state
      setMitigations(mitigations.map(m => 
        m.id === mitigationId ? { ...m, status: action === 'approve' ? 'approved' : 'rejected' } : m
      ));
    } catch (err) {
      console.error('Error updating mitigation:', err);
    }
  };
  
  if (mitigations.length === 0) {
    return (
      <div className="text-center py-8" data-testid="no-mitigations">
        <ListChecks className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-600">No mitigations required</p>
      </div>
    );
  }
  
  return (
    <div data-testid="mitigations-tab">
      <h2 className="text-xl font-bold mb-4">Recommended Mitigations</h2>
      <p className="text-gray-600 mb-6">
        Review and approve recommended actions to reduce release risk. All mitigations require human approval.
      </p>
      
      <div className="space-y-4">
        {mitigations.map((mitigation, idx) => (
          <div
            key={mitigation.id}
            data-testid={`mitigation-${idx}`}
            className="border border-gray-200 rounded-lg p-4"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="font-semibold text-gray-900">{mitigation.action_type.replace('_', ' ').toUpperCase()}</span>
                  {mitigation.required && (
                    <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">REQUIRED</span>
                  )}
                  <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    Confidence: {(mitigation.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-gray-700">{mitigation.description}</p>
              </div>
              
              <div className="ml-4">
                {mitigation.status === 'draft' && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleApproval(mitigation.id, 'approve')}
                      data-testid={`btn-approve-${idx}`}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-semibold transition"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleApproval(mitigation.id, 'reject')}
                      data-testid={`btn-reject-${idx}`}
                      className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-semibold transition"
                    >
                      Reject
                    </button>
                  </div>
                )}
                {mitigation.status === 'approved' && (
                  <span className="flex items-center space-x-1 text-green-600">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-semibold">Approved</span>
                  </span>
                )}
                {mitigation.status === 'rejected' && (
                  <span className="flex items-center space-x-1 text-red-600">
                    <XCircle className="w-5 h-5" />
                    <span className="font-semibold">Rejected</span>
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PRDetail;
