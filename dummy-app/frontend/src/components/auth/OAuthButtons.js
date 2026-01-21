/**
 * OAuth Buttons Component
 * Risk Level: HIGH - OAuth authentication with intentional issues
 * 
 * Intentional Issues:
 * - State parameter not validated
 * - Redirect URI manipulation possible
 * - Token exposed in URL
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './OAuthButtons.css';

// INTENTIONAL VULNERABILITY: Hardcoded client IDs
const GOOGLE_CLIENT_ID = '123456789-abcdefghij.apps.googleusercontent.com';
const GITHUB_CLIENT_ID = 'Iv1.abc123def456';

// INTENTIONAL: Insecure redirect URI
const REDIRECT_URI = window.location.origin + '/oauth/callback';

function OAuthButtons() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [oauthState, setOauthState] = useState(null);

  useEffect(() => {
    // Check for OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const token = urlParams.get('token'); // INTENTIONAL: Token in URL

    if (code) {
      handleOAuthCallback(code, state);
    }

    // INTENTIONAL: Token exposed in URL hash
    if (window.location.hash) {
      const hashParams = new URLSearchParams(window.location.hash.substring(1));
      const accessToken = hashParams.get('access_token');
      if (accessToken) {
        // INTENTIONAL: Storing token without validation
        localStorage.setItem('oauth_token', accessToken);
        console.log('OAuth token received:', accessToken);
      }
    }
  }, []);

  const handleOAuthCallback = async (code, state) => {
    setLoading(true);
    
    // INTENTIONAL: State not properly validated
    console.log('OAuth callback with state:', state);
    
    try {
      // INTENTIONAL: Sending code to backend without proper validation
      const response = await axios.get('/api/oauth/callback', {
        params: { code, state }
      });

      // Store token insecurely
      localStorage.setItem('oauth_token', response.data.access_token);
      
      // INTENTIONAL: Redirect without sanitization
      const returnUrl = urlParams.get('return_url') || '/';
      window.location.href = returnUrl;
    } catch (err) {
      setError('OAuth authentication failed');
      console.error('OAuth error:', err);
    } finally {
      setLoading(false);
    }
  };

  const initiateGoogleOAuth = () => {
    // INTENTIONAL: Weak state generation
    const state = Math.random().toString(36).substring(7);
    setOauthState(state);
    
    // INTENTIONAL: Storing state in localStorage (can be accessed by XSS)
    localStorage.setItem('oauth_state', state);

    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    authUrl.searchParams.append('client_id', GOOGLE_CLIENT_ID);
    authUrl.searchParams.append('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.append('response_type', 'code');
    authUrl.searchParams.append('scope', 'email profile');
    authUrl.searchParams.append('state', state);
    
    // INTENTIONAL: Access type offline exposes refresh token
    authUrl.searchParams.append('access_type', 'offline');

    window.location.href = authUrl.toString();
  };

  const initiateGitHubOAuth = () => {
    const state = Math.random().toString(36).substring(7);
    localStorage.setItem('oauth_state', state);

    const authUrl = new URL('https://github.com/login/oauth/authorize');
    authUrl.searchParams.append('client_id', GITHUB_CLIENT_ID);
    authUrl.searchParams.append('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.append('scope', 'user:email');
    authUrl.searchParams.append('state', state);

    window.location.href = authUrl.toString();
  };

  // INTENTIONAL: Function to extract token from URL (insecure)
  const extractTokenFromUrl = () => {
    const hash = window.location.hash;
    if (hash) {
      const params = new URLSearchParams(hash.substring(1));
      return params.get('access_token');
    }
    return null;
  };

  if (loading) {
    return (
      <div className="oauth-container">
        <div className="oauth-card">
          <div className="loading-spinner"></div>
          <p>Authenticating...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="oauth-container">
      <div className="oauth-card">
        <h2>Sign in with</h2>

        {error && (
          <div className="error-message">{error}</div>
        )}

        <div className="oauth-buttons">
          <button 
            className="oauth-btn google-btn"
            onClick={initiateGoogleOAuth}
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>

          <button 
            className="oauth-btn github-btn"
            onClick={initiateGitHubOAuth}
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            Continue with GitHub
          </button>
        </div>

        <div className="divider">
          <span>or</span>
        </div>

        <a href="/login" className="btn btn-secondary btn-block">
          Sign in with email
        </a>
      </div>
    </div>
  );
}

export default OAuthButtons;
