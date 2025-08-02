import React, { useState } from 'react';
import { X, Mail, CheckCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { authService } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import '../styles/ForgotPasswordModal.css';

const ForgotPasswordModal = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await authService.forgotPassword(email);
      
      if (result.success) {
        setEmailSent(true);
        toast.success('Password reset instructions sent to your email');
      } else {
        setError(result.error || 'Failed to send reset email');
        toast.error(result.error || 'Failed to send reset email');
      }
    } catch (error) {
      console.error('Forgot password error:', error);
      setError('An error occurred. Please try again.');
      toast.error('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setEmailSent(false);
    setError('');
    setLoading(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="forgot-password-overlay">
      <div className="forgot-password-modal">
        <div className="forgot-password-header">
          <h2>Reset Your Password</h2>
          <button 
            className="close-button" 
            onClick={handleClose}
            disabled={loading}
          >
            <X size={20} />
          </button>
        </div>

        <div className="forgot-password-content">
          {!emailSent ? (
            <>
              <div className="forgot-password-description">
                <Mail size={48} className="mail-icon" />
                <p>
                  Enter your email address and we'll send you a link to reset your password.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="forgot-password-form">
                <div className="form-group">
                  <label htmlFor="reset-email">Email Address</label>
                  <input
                    id="reset-email"
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setError('');
                    }}
                    placeholder="Enter your email address"
                    className={error ? 'error' : ''}
                    disabled={loading}
                    autoFocus
                  />
                  {error && <span className="error-message">{error}</span>}
                </div>

                <div className="forgot-password-actions">
                  <button
                    type="button"
                    className="cancel-button"
                    onClick={handleClose}
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="send-button"
                    disabled={loading}
                  >
                    {loading ? <LoadingSpinner size="small" /> : 'Send Reset Link'}
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="email-sent-confirmation">
              <CheckCircle size={48} className="success-icon" />
              <h3>Check Your Email</h3>
              <p>
                We've sent password reset instructions to <strong>{email}</strong>
              </p>
              <p className="secondary-text">
                Didn't receive the email? Check your spam folder or try again.
              </p>
              <div className="confirmation-actions">
                <button
                  type="button"
                  className="try-again-button"
                  onClick={() => {
                    setEmailSent(false);
                    setEmail('');
                  }}
                >
                  Try Different Email
                </button>
                <button
                  type="button"
                  className="done-button"
                  onClick={handleClose}
                >
                  Done
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordModal;
