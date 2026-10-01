import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-brand">
            <h3><span className="text-gradient">EVE</span> Healthcare</h3>
            <p>Redefining diagnostic experiences with cutting-edge technology and seamless integrations.</p>
          </div>
          
          <div className="footer-links">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="#features">Features</a></li>
              <li><a href="#how-it-works">How It Works</a></li>
              <li><a href="/login">Login</a></li>
              <li><a href="/register">Register</a></li>
            </ul>
          </div>
          
          <div className="footer-links">
            <h4>Legal</h4>
            <ul>
              <li><a href="/privacy">Privacy Policy</a></li>
              <li><a href="/terms">Terms of Service</a></li>
              <li><a href="/refunds">Refund Policy</a></li>
            </ul>
          </div>
          
          <div className="footer-contact">
            <h4>Contact Us</h4>
            <p>support@evehealthcare.com</p>
            <p>+1 (800) 123-4567</p>
            <div className="social-links">
              <a href="#" className="social-icon">In</a>
              <a href="#" className="social-icon">Tw</a>
              <a href="#" className="social-icon">Fb</a>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} EVE Healthcare. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
