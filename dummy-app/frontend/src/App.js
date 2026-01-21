/**
 * Main Application Component
 * Risk Level: LOW - Simple routing configuration
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Auth Components (HIGH RISK)
import LoginForm from './components/auth/LoginForm';
import OAuthButtons from './components/auth/OAuthButtons';

// Payment Components (HIGH RISK)
import PaymentForm from './components/payment/PaymentForm';
import CheckoutPage from './components/payment/CheckoutPage';

// Utility Components (LOW RISK)
import Header from './components/utils/Header';
import Footer from './components/utils/Footer';
import LoadingSpinner from './components/utils/LoadingSpinner';

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginForm />} />
            <Route path="/oauth" element={<OAuthButtons />} />
            <Route path="/payment" element={<PaymentForm />} />
            <Route path="/checkout" element={<CheckoutPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

function HomePage() {
  return (
    <div className="container">
      <div className="hero">
        <h1>Dummy App</h1>
        <p>A test application for R3 Agent E2E testing</p>
        <div className="hero-links">
          <Link to="/login" className="btn btn-primary">Login</Link>
          <Link to="/payment" className="btn btn-primary">Payment</Link>
          <Link to="/checkout" className="btn btn-primary">Checkout</Link>
        </div>
      </div>
    </div>
  );
}

export default App;
