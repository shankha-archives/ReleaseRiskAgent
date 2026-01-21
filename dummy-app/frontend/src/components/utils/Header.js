/**
 * Header Component
 * Risk Level: LOW - Simple presentation component
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">
          Dummy App
        </Link>
        
        <nav className="nav">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/login" className="nav-link">Login</Link>
          <Link to="/payment" className="nav-link">Payment</Link>
          <Link to="/checkout" className="nav-link">Checkout</Link>
        </nav>
      </div>
    </header>
  );
}

export default Header;
