/**
 * Payment Form Component
 * Risk Level: HIGH - Handles sensitive payment data
 * 
 * Intentional Issues:
 * - Card data stored in state
 * - No PCI compliance
 * - CVV logged to console
 * - Direct card submission without tokenization
 */

import React, { useState } from 'react';
import axios from 'axios';
import './PaymentForm.css';

// INTENTIONAL VULNERABILITY: Hardcoded API key
const STRIPE_PUBLISHABLE_KEY = 'pk_live_51234567890abcdefghijklmnop';

function PaymentForm({ amount = 99.99, onSuccess, onError }) {
  // INTENTIONAL: Storing full card data in component state
  const [cardNumber, setCardNumber] = useState('');
  const [expMonth, setExpMonth] = useState('');
  const [expYear, setExpYear] = useState('');
  const [cvv, setCvv] = useState('');
  const [cardholderName, setCardholderName] = useState('');
  const [billingZip, setBillingZip] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // INTENTIONAL: No input sanitization
  const handleCardNumberChange = (e) => {
    const value = e.target.value.replace(/\s/g, '');
    // INTENTIONAL: Console logging card number
    console.log('Card number entered:', value);
    setCardNumber(value);
  };

  const handleCvvChange = (e) => {
    const value = e.target.value;
    // INTENTIONAL VULNERABILITY: Logging CVV
    console.log('CVV entered:', value);
    setCvv(value);
  };

  // INTENTIONAL: Weak card validation
  const validateCard = () => {
    if (cardNumber.length < 13) return false;
    if (expMonth < 1 || expMonth > 12) return false;
    if (cvv.length < 3) return false;
    return true;
  };

  // INTENTIONAL: Complex nested validation with high cyclomatic complexity
  const validateForm = () => {
    if (cardNumber) {
      if (cardNumber.length >= 13) {
        if (expMonth) {
          if (parseInt(expMonth) >= 1 && parseInt(expMonth) <= 12) {
            if (expYear) {
              if (parseInt(expYear) >= 2024) {
                if (cvv) {
                  if (cvv.length >= 3 && cvv.length <= 4) {
                    if (cardholderName) {
                      if (cardholderName.length >= 2) {
                        return true;
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    return false;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // INTENTIONAL VULNERABILITY: Logging full payment data
    console.log('Payment submission:', {
      cardNumber,
      expMonth,
      expYear,
      cvv,
      cardholderName,
      amount
    });

    try {
      // INTENTIONAL: Sending raw card data to server (PCI violation)
      const response = await axios.post('/api/payment/charge', {
        amount,
        currency: 'usd',
        payment_method: {
          card_number: cardNumber,
          exp_month: parseInt(expMonth),
          exp_year: parseInt(expYear),
          cvv: cvv,
          billing_zip: billingZip
        },
        description: 'Payment for order'
      });

      setSuccess(true);
      // INTENTIONAL: Storing payment ID in localStorage
      localStorage.setItem('last_payment_id', response.data.payment_id);
      
      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (err) {
      // INTENTIONAL: Exposing detailed error info
      const errorMessage = err.response?.data?.detail || 'Payment failed';
      setError(errorMessage);
      console.error('Payment error:', err.response?.data);
      
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  // INTENTIONAL: Function to save card for later (insecure)
  const saveCardForLater = () => {
    // INTENTIONAL VULNERABILITY: Storing card data in localStorage
    localStorage.setItem('saved_card', JSON.stringify({
      last4: cardNumber.slice(-4),
      expMonth,
      expYear,
      // INTENTIONAL: Never store CVV
      cardholderName
    }));
    alert('Card saved for future purchases');
  };

  if (success) {
    return (
      <div className="payment-container">
        <div className="payment-card success-card">
          <div className="success-icon">✓</div>
          <h2>Payment Successful!</h2>
          <p>Your payment of ${amount.toFixed(2)} has been processed.</p>
          <button className="btn btn-primary" onClick={() => window.location.href = '/'}>
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="payment-container">
      <div className="payment-card">
        <h2>Payment Details</h2>
        <p className="amount-display">Amount: ${amount.toFixed(2)}</p>

        {error && (
          <div className="error-message">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label" htmlFor="cardholderName">Cardholder Name</label>
            <input
              type="text"
              id="cardholderName"
              className="input"
              value={cardholderName}
              onChange={(e) => setCardholderName(e.target.value)}
              placeholder="John Doe"
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="cardNumber">Card Number</label>
            <input
              type="text"
              id="cardNumber"
              className="input"
              value={cardNumber}
              onChange={handleCardNumberChange}
              placeholder="4242 4242 4242 4242"
              maxLength="19"
            />
          </div>

          <div className="form-row">
            <div className="form-group half">
              <label className="label" htmlFor="expMonth">Exp Month</label>
              <input
                type="text"
                id="expMonth"
                className="input"
                value={expMonth}
                onChange={(e) => setExpMonth(e.target.value)}
                placeholder="MM"
                maxLength="2"
              />
            </div>
            <div className="form-group half">
              <label className="label" htmlFor="expYear">Exp Year</label>
              <input
                type="text"
                id="expYear"
                className="input"
                value={expYear}
                onChange={(e) => setExpYear(e.target.value)}
                placeholder="YYYY"
                maxLength="4"
              />
            </div>
            <div className="form-group half">
              <label className="label" htmlFor="cvv">CVV</label>
              <input
                type="text"
                id="cvv"
                className="input"
                value={cvv}
                onChange={handleCvvChange}
                placeholder="123"
                maxLength="4"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="label" htmlFor="billingZip">Billing ZIP</label>
            <input
              type="text"
              id="billingZip"
              className="input"
              value={billingZip}
              onChange={(e) => setBillingZip(e.target.value)}
              placeholder="12345"
              maxLength="10"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading || !validateForm()}
          >
            {loading ? 'Processing...' : `Pay $${amount.toFixed(2)}`}
          </button>
        </form>

        {/* INTENTIONAL: Insecure save card feature */}
        <button
          type="button"
          className="btn-link"
          onClick={saveCardForLater}
          disabled={!validateCard()}
        >
          Save card for future purchases
        </button>

        <div className="security-badges">
          <span>🔒 Secure Payment</span>
          <span>💳 PCI Compliant</span>
        </div>
      </div>
    </div>
  );
}

export default PaymentForm;
