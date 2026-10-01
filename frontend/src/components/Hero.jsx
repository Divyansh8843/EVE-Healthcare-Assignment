import React from 'react';
import './Hero.css';

const Hero = () => {
  return (
    <section className="hero">
      <div className="hero-background">
        <div className="glow glow-1"></div>
        <div className="glow glow-2"></div>
      </div>
      <div className="container hero-container">
        <div className="hero-content animate-fade-in">
          <div className="badge">Next-Gen Diagnostics</div>
          <h1 className="hero-title">
            Your Health, <br/>
            <span className="text-gradient">Precision Delivered.</span>
          </h1>
          <p className="hero-subtitle">
            Book diagnostic tests instantly at verified centres. Receive digital reports, seamless payments, and an unmatched healthcare experience.
          </p>
          <div className="hero-cta">
            <a href="#get-started" className="btn btn-primary pulse-btn">Book a Test Now</a>
            <a href="#how-it-works" className="btn btn-secondary">Explore Features</a>
          </div>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">50+</span>
              <span className="stat-label">Diagnostic Centres</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">10k+</span>
              <span className="stat-label">Happy Patients</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">24/7</span>
              <span className="stat-label">Customer Support</span>
            </div>
          </div>
        </div>
        <div className="hero-visual animate-fade-in delay-200">
          <div className="glass-card main-card float-anim">
            <div className="card-header">
              <div className="dot"></div>
              <span>Recent Booking</span>
            </div>
            <div className="card-body">
              <div className="booking-info">
                <h4>Comprehensive Blood Panel</h4>
                <p>City Center Diagnostics</p>
              </div>
              <div className="status confirmed">Confirmed</div>
            </div>
          </div>
          <div className="glass-card sub-card float-anim delay-200">
            <div className="card-header">
              <div className="dot green"></div>
              <span>Payment</span>
            </div>
            <div className="card-body">
              <div className="payment-amount">$120.00</div>
              <div className="status success">Success</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
