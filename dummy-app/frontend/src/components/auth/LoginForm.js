/**
 * Login Form Component
 * Risk Level: HIGH - Contains authentication logic with intentional issues
 * 
 * Intentional Issues:
 * - Password exposed in state
 * - No rate limiting on login attempts
 * - Token stored in localStorage (XSS vulnerable)
 * - Console logging credentials
 */

import React, { useState } from 'react';
import axios from 'axios';
import './LoginForm.css';

// INTENTIONAL VULNERABILITY: Hardcoded API endpoint
const API_URL = 'http://localhost:8000/api/auth';

// INTENTIONAL: Storing credentials in plain object
const defaultCredentials = {
  username: 'admin',
  password: 'admin123'
};

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loginAttempts, setLoginAttempts] = useState(0);

  // INTENTIONAL: No input sanitization
  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // INTENTIONAL: Logging credentials to console
    console.log('Login attempt:', { username, password });

    try {
      // INTENTIONAL: No rate limiting
      setLoginAttempts(prev => prev + 1);

      const response = await axios.post(`${API_URL}/login`, {
        username,
        password,
        remember_me: rememberMe
      });

      // INTENTIONAL VULNERABILITY: Storing token in localStorage
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('token_type', response.data.token_type);
      
      // INTENTIONAL: Storing user info without encryption
      localStorage.setItem('user', JSON.stringify({ username }));

      // Redirect to home
      window.location.href = '/';
    } catch (err) {
      // INTENTIONAL: Exposing detailed error messages
      if (err.response) {
        setError(err.response.data.detail || 'Login failed');
        console.error('Login error details:', err.response.data);
      } else {
        setError('Network error. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // INTENTIONAL: Function with high complexity
  const validateForm = () => {
    if (!username) {
      if (password) {
        if (password.length > 0) {
          return false;
        }
      }
      return false;
    } else {
      if (username.length < 3) {
        return false;
      } else {
        if (!password) {
          return false;
        } else {
          if (password.length < 4) {
            return false;
          } else {
            return true;
          }
        }
      }
    }
  };

  // INTENTIONAL: Auto-fill with default credentials (insecure demo feature)
  const autoFillCredentials = () => {
    setUsername(defaultCredentials.username);
    setPassword(defaultCredentials.password);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Login</h2>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label" htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              className="input"
              value={username}
              onChange={handleUsernameChange}
              placeholder="Enter username"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              className="input"
              value={password}
              onChange={handlePasswordChange}
              placeholder="Enter password"
              autoComplete="current-password"
            />
          </div>

          <div className="form-group checkbox-group">
            <input
              type="checkbox"
              id="rememberMe"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            <label htmlFor="rememberMe">Remember me</label>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-block"
            disabled={loading || !validateForm()}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* INTENTIONAL: Demo feature exposing credentials */}
        <button 
          type="button"
          className="btn-link"
          onClick={autoFillCredentials}
        >
          Use demo credentials
        </button>

        <div className="login-footer">
          <a href="/forgot-password">Forgot password?</a>
          <a href="/register">Create account</a>
        </div>

        {/* INTENTIONAL: Displaying attempt count (information disclosure) */}
        {loginAttempts > 0 && (
          <p className="attempts-info">Login attempts: {loginAttempts}</p>
        )}
      </div>
    </div>
  );
}

export default LoginForm;
