import React from 'react';
import './GetStarted.css';

const GetStarted = () => {
  return (
    <section id="get-started" className="get-started section-padding">
      <div className="container">
        <div className="cta-box glass-card">
          <div className="cta-content">
            <h2>Ready to Take Control of Your Health?</h2>
            <p>Join thousands of users who have streamlined their diagnostic experience. Sign up today and get 20% off your first test booking.</p>
            <div className="cta-buttons">
              <a href="/register" className="btn btn-primary pulse-btn">Create an Account</a>
              <a href="#features" className="btn btn-secondary">Learn More</a>
            </div>
          </div>
          <div className="cta-visual">
            <div className="circle-bg"></div>
            <img src="https://ui-avatars.com/api/?name=EVE+Health&background=00d8ff&color=fff&size=200&rounded=true" alt="EVE Healthcare" className="cta-image float-anim" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default GetStarted;
