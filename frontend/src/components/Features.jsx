import React from 'react';
import './Features.css';

const features = [
  {
    title: 'Verified Diagnostic Centres',
    description: 'Access a curated network of top-rated diagnostic centres ensuring accurate and timely reports.',
    icon: '🏥'
  },
  {
    title: 'Seamless Digital Booking',
    description: 'Book your diagnostic tests instantly without the hassle of phone calls or physical visits.',
    icon: '📱'
  },
  {
    title: 'Instant Online Payments',
    description: 'Pay securely using our integrated simulated payment gateway with immediate confirmation.',
    icon: '💳'
  },
  {
    title: 'Digital Health Records',
    description: 'Access all your diagnostic test reports securely from your personalized dashboard anytime.',
    icon: '📊'
  }
];

const Features = () => {
  return (
    <section id="features" className="features section-padding">
      <div className="container">
        <div className="section-header text-center">
          <h2 className="section-title">Why Choose <span className="text-gradient">EVE Healthcare</span></h2>
          <p className="section-subtitle">We bring the best diagnostic centres to your fingertips, making healthcare accessible and stress-free.</p>
        </div>
        
        <div className="features-grid">
          {features.map((feature, index) => (
            <div className="feature-card glass-card" key={index}>
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
