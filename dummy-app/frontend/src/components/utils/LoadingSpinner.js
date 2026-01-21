/**
 * Loading Spinner Component
 * Risk Level: LOW - Simple UI component
 */

import React from 'react';
import './LoadingSpinner.css';

function LoadingSpinner({ size = 'medium', message = 'Loading...' }) {
  const sizeClasses = {
    small: 'spinner-small',
    medium: 'spinner-medium',
    large: 'spinner-large'
  };

  return (
    <div className="spinner-container">
      <div className={`spinner ${sizeClasses[size] || sizeClasses.medium}`}></div>
      {message && <p className="spinner-message">{message}</p>}
    </div>
  );
}

export default LoadingSpinner;
