import React from 'react';
import './HowItWorks.css';

const steps = [
  {
    number: '01',
    title: 'Find a Test',
    description: 'Search for the required diagnostic test and choose a centre near you from our verified network.'
  },
  {
    number: '02',
    title: 'Book & Pay',
    description: 'Select your preferred time slot and securely complete the payment via our simulated gateway.'
  },
  {
    number: '03',
    title: 'Visit Centre',
    description: 'Visit the diagnostic centre at the scheduled time. No waiting lines, just quick and smooth service.'
  },
  {
    number: '04',
    title: 'Get Reports',
    description: 'Access your detailed digital reports directly on your EVE Healthcare dashboard.'
  }
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="how-it-works section-padding">
      <div className="container">
        <div className="section-header text-center">
          <h2 className="section-title">How It <span className="text-gradient">Works</span></h2>
          <p className="section-subtitle">Four simple steps to a healthier you.</p>
        </div>
        
        <div className="steps-container">
          <div className="steps-line"></div>
          {steps.map((step, index) => (
            <div className="step-card glass-card" key={index}>
              <div className="step-number">{step.number}</div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
