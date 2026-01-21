/**
 * Checkout Page Component
 * Risk Level: HIGH - Full checkout flow with payment processing
 * 
 * Intentional Issues:
 * - Price manipulation possible
 * - No CSRF protection
 * - Order data exposed in console
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PaymentForm from './PaymentForm';
import './CheckoutPage.css';

// INTENTIONAL: Sample products with prices that can be manipulated
const SAMPLE_PRODUCTS = [
  { id: 1, name: 'Premium Plan', price: 99.99, description: 'Full access to all features' },
  { id: 2, name: 'Basic Plan', price: 29.99, description: 'Limited features' },
  { id: 3, name: 'Enterprise Plan', price: 299.99, description: 'Custom solutions' }
];

function CheckoutPage() {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [promoCode, setPromoCode] = useState('');
  const [discount, setDiscount] = useState(0);
  const [step, setStep] = useState('select'); // select, review, payment, complete
  const [orderData, setOrderData] = useState(null);
  const [error, setError] = useState(null);

  // INTENTIONAL: Load price from URL parameter (allows manipulation)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const productId = params.get('product');
    const priceOverride = params.get('price'); // INTENTIONAL VULNERABILITY
    
    if (productId) {
      const product = SAMPLE_PRODUCTS.find(p => p.id === parseInt(productId));
      if (product) {
        setSelectedProduct({
          ...product,
          // INTENTIONAL: Price can be overridden from URL
          price: priceOverride ? parseFloat(priceOverride) : product.price
        });
        setStep('review');
      }
    }
  }, []);

  // INTENTIONAL: Weak promo code validation
  const applyPromoCode = () => {
    // INTENTIONAL: Hardcoded promo codes
    const promoCodes = {
      'DISCOUNT10': 10,
      'DISCOUNT50': 50,
      'FREE100': 100, // INTENTIONAL: 100% discount available
      'ADMIN': 100    // INTENTIONAL: Admin override code
    };

    if (promoCodes[promoCode.toUpperCase()]) {
      setDiscount(promoCodes[promoCode.toUpperCase()]);
      console.log('Promo code applied:', promoCode, 'Discount:', promoCodes[promoCode.toUpperCase()]);
    } else {
      setError('Invalid promo code');
    }
  };

  // INTENTIONAL: Calculate total with potential negative values
  const calculateTotal = () => {
    if (!selectedProduct) return 0;
    const subtotal = selectedProduct.price * quantity;
    const discountAmount = (subtotal * discount) / 100;
    // INTENTIONAL: No check for negative total
    return subtotal - discountAmount;
  };

  const handleProductSelect = (product) => {
    setSelectedProduct(product);
    // INTENTIONAL: Logging selection with price
    console.log('Product selected:', product);
  };

  const handleProceedToPayment = () => {
    // INTENTIONAL: Creating order without server validation
    const order = {
      product: selectedProduct,
      quantity,
      subtotal: selectedProduct.price * quantity,
      discount,
      total: calculateTotal(),
      promoCode: promoCode || null,
      createdAt: new Date().toISOString()
    };

    // INTENTIONAL: Logging full order data
    console.log('Order created:', order);
    
    // INTENTIONAL: Storing order in localStorage
    localStorage.setItem('pending_order', JSON.stringify(order));
    
    setOrderData(order);
    setStep('payment');
  };

  const handlePaymentSuccess = (paymentResult) => {
    // INTENTIONAL: Not validating server response
    const completedOrder = {
      ...orderData,
      paymentId: paymentResult.payment_id,
      status: 'completed'
    };

    // INTENTIONAL: Storing completed order in localStorage
    localStorage.setItem('last_order', JSON.stringify(completedOrder));
    
    setStep('complete');
  };

  const handlePaymentError = (err) => {
    setError('Payment failed. Please try again.');
    console.error('Payment error:', err);
  };

  const renderProductSelection = () => (
    <div className="checkout-step">
      <h2>Select a Product</h2>
      <div className="product-grid">
        {SAMPLE_PRODUCTS.map(product => (
          <div 
            key={product.id} 
            className={`product-card ${selectedProduct?.id === product.id ? 'selected' : ''}`}
            onClick={() => handleProductSelect(product)}
          >
            <h3>{product.name}</h3>
            <p className="price">${product.price.toFixed(2)}</p>
            <p className="description">{product.description}</p>
          </div>
        ))}
      </div>
      {selectedProduct && (
        <button className="btn btn-primary" onClick={() => setStep('review')}>
          Continue to Review
        </button>
      )}
    </div>
  );

  const renderOrderReview = () => (
    <div className="checkout-step">
      <h2>Review Your Order</h2>
      
      <div className="order-summary">
        <div className="order-item">
          <span>{selectedProduct.name}</span>
          <span>${selectedProduct.price.toFixed(2)}</span>
        </div>
        
        <div className="quantity-control">
          <label>Quantity:</label>
          <input
            type="number"
            min="1"
            max="100"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
          />
        </div>

        <div className="promo-section">
          <input
            type="text"
            className="input"
            placeholder="Promo code"
            value={promoCode}
            onChange={(e) => setPromoCode(e.target.value)}
          />
          <button className="btn btn-secondary" onClick={applyPromoCode}>
            Apply
          </button>
        </div>

        {discount > 0 && (
          <div className="discount-row">
            <span>Discount ({discount}%)</span>
            <span>-${((selectedProduct.price * quantity * discount) / 100).toFixed(2)}</span>
          </div>
        )}

        <div className="total-row">
          <span>Total</span>
          <span>${calculateTotal().toFixed(2)}</span>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="button-row">
        <button className="btn btn-secondary" onClick={() => setStep('select')}>
          Back
        </button>
        <button className="btn btn-primary" onClick={handleProceedToPayment}>
          Proceed to Payment
        </button>
      </div>
    </div>
  );

  const renderPayment = () => (
    <div className="checkout-step">
      <h2>Payment</h2>
      <PaymentForm 
        amount={calculateTotal()}
        onSuccess={handlePaymentSuccess}
        onError={handlePaymentError}
      />
      <button className="btn btn-secondary back-btn" onClick={() => setStep('review')}>
        Back to Review
      </button>
    </div>
  );

  const renderComplete = () => (
    <div className="checkout-step complete-step">
      <div className="success-icon">✓</div>
      <h2>Order Complete!</h2>
      <p>Thank you for your purchase.</p>
      <p>Order ID: {orderData?.paymentId || 'N/A'}</p>
      <button className="btn btn-primary" onClick={() => window.location.href = '/'}>
        Return to Home
      </button>
    </div>
  );

  return (
    <div className="checkout-container">
      <div className="checkout-progress">
        <span className={step === 'select' ? 'active' : ''}>1. Select</span>
        <span className={step === 'review' ? 'active' : ''}>2. Review</span>
        <span className={step === 'payment' ? 'active' : ''}>3. Payment</span>
        <span className={step === 'complete' ? 'active' : ''}>4. Complete</span>
      </div>

      {step === 'select' && renderProductSelection()}
      {step === 'review' && renderOrderReview()}
      {step === 'payment' && renderPayment()}
      {step === 'complete' && renderComplete()}
    </div>
  );
}

export default CheckoutPage;
