import React, { useState, useEffect } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import GoogleIcon from '../components/GoogleIcon';
import ForgotPasswordModal from '../components/ForgotPasswordModal';
import { toast } from 'react-hot-toast';
import '../styles/AuthenticationPage.css';
import foodlensLogo from '../assets/images/foodlens.png';

const AuthenticationPage = ({ onSuccess }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  
  const { login, register, googleLogin } = useAuth();

  const [signInForm, setSignInForm] = useState({
    email_or_username: '',
    password: ''
  });

  const [signUpForm, setSignUpForm] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: ''
  });

  const [errors, setErrors] = useState({});

  // Google OAuth setup
  useEffect(() => {
    // Only load Google OAuth if we have proper client ID configured
    const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
    
    if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') {
      console.log('Google OAuth not configured - using demo mode');
      return;
    }

    // Load Google OAuth script
    const loadGoogleScript = () => {
      if (window.google) {
        initializeGoogleAuth();
        return;
      }
      
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initializeGoogleAuth;
      script.onerror = () => {
        console.error('Failed to load Google OAuth script');
      };
      document.head.appendChild(script);
    };

    const initializeGoogleAuth = () => {
      if (window.google && window.google.accounts) {
        try {
          // Initialize for both ID token and access token flows
          window.google.accounts.id.initialize({
            client_id: clientId,
            callback: handleGoogleCredentialResponse,
            auto_select: false,
            cancel_on_tap_outside: true
          });
          console.log('Google OAuth initialized successfully');
        } catch (error) {
          console.error('Google OAuth initialization error:', error);
        }
      }
    };

    loadGoogleScript();
  }, []);

  const handleGoogleCredentialResponse = async (response) => {
    try {
      await handleGoogleAuth(response.credential);
    } catch (error) {
      console.error('Google credential response error:', error);
      toast.error('Google authentication failed');
    }
  };

  const handleGoogleSignIn = () => {
    if (window.google && window.google.accounts && process.env.REACT_APP_GOOGLE_CLIENT_ID !== 'your-google-client-id.apps.googleusercontent.com') {
      // Use Google OAuth popup for sign in
      window.google.accounts.oauth2.initTokenClient({
        client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
        scope: 'email profile',
        callback: (response) => {
          if (response.access_token) {
            handleGoogleAuth(response.access_token);
          }
        }
      }).requestAccessToken();
    } else {
      // For development/testing when Google credentials are not configured
      console.log('Google OAuth not configured, using demo token for testing');
      toast.info('Demo Google Sign In - Using test authentication');
      handleGoogleAuth('demo-google-token-signin');
    }
  };

  const handleGoogleSignUp = () => {
    if (window.google && window.google.accounts && process.env.REACT_APP_GOOGLE_CLIENT_ID !== 'your-google-client-id.apps.googleusercontent.com') {
      // Use Google OAuth popup for sign up
      window.google.accounts.oauth2.initTokenClient({
        client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
        scope: 'email profile',
        callback: (response) => {
          if (response.access_token) {
            handleGoogleAuth(response.access_token);
          }
        }
      }).requestAccessToken();
    } else {
      // For development/testing when Google credentials are not configured
      console.log('Google OAuth not configured, using demo token for testing');
      toast.info('Demo Google Sign Up - Using test authentication');
      handleGoogleAuth('demo-google-token-signup');
    }
  };

  const handleSignInChange = (e) => {
    const { name, value } = e.target;
    setSignInForm(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSignUpChange = (e) => {
    const { name, value } = e.target;
    setSignUpForm(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateSignInForm = () => {
    const newErrors = {};
    
    if (!signInForm.email_or_username.trim()) {
      newErrors.email_or_username = 'Email or username is required';
    }
    
    if (!signInForm.password) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateSignUpForm = () => {
    const newErrors = {};
    
    if (!signUpForm.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(signUpForm.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!signUpForm.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (signUpForm.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }
    
    if (!signUpForm.password) {
      newErrors.password = 'Password is required';
    } else if (signUpForm.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSignIn = async (e) => {
    e.preventDefault();
    
    if (!validateSignInForm()) return;
    
    setLoading(true);
    
    try {
      const result = await login(signInForm);
      
      if (result.success) {
        toast.success('Signed in successfully!');
        onSuccess && onSuccess(result.user, result.isNewUser);
      } else {
        toast.error(result.error || 'Sign in failed');
      }
    } catch (error) {
      console.error('Sign in error:', error);
      toast.error('An error occurred during sign in');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    
    console.log('Sign up form data:', signUpForm);
    
    if (!validateSignUpForm()) {
      console.log('Form validation failed');
      return;
    }
    
    setLoading(true);
    
    try {
      console.log('Calling register function...');
      const result = await register(signUpForm);
      console.log('Register result:', result);
      
      if (result.success) {
        toast.success('Account created successfully!');
        onSuccess && onSuccess(result.user, true);
      } else {
        console.log('Registration failed:', result);
        if (result.details && Array.isArray(result.details)) {
          result.details.forEach(error => toast.error(error));
        } else {
          toast.error(result.error || 'Registration failed');
        }
      }
    } catch (error) {
      console.error('Sign up error:', error);
      toast.error('An error occurred during registration');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async (googleToken) => {
    setLoading(true);
    
    try {
      const result = await googleLogin(googleToken);
      
      if (result.success) {
        toast.success('Signed in with Google successfully!');
        onSuccess && onSuccess(result.user, result.isNewUser);
      } else {
        toast.error(result.error || 'Google sign in failed');
      }
    } catch (error) {
      console.error('Google auth error:', error);
      toast.error('An error occurred during Google sign in');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    setShowForgotPassword(true);
  };

  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setErrors({});
    setSignInForm({ email_or_username: '', password: '' });
    setSignUpForm({ email: '', username: '', password: '', first_name: '', last_name: '' });
  };

  if (loading) {
    return (
      <div className="auth-loading">
        <LoadingSpinner />
        <p>Please wait...</p>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <img src={foodlensLogo} alt="FoodLens" className="auth-logo" />
        </div>

        <h2 className="auth-title">
          {isSignUp ? 'Sign Up' : 'Sign In'}
        </h2>

        {!isSignUp ? (
          // Sign In Form
          <form onSubmit={handleSignIn} className="auth-form">
            <div className="form-group">
              <label>Email or Username</label>
              <input
                type="text"
                name="email_or_username"
                value={signInForm.email_or_username}
                onChange={handleSignInChange}
                className={errors.email_or_username ? 'error' : ''}
                placeholder="Enter your email or username"
              />
              {errors.email_or_username && (
                <span className="error-message">{errors.email_or_username}</span>
              )}
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="password-field">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={signInForm.password}
                  onChange={handleSignInChange}
                  className={errors.password ? 'error' : ''}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <span className="error-message">{errors.password}</span>
              )}
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                Remember Me
              </label>
              <button 
                type="button" 
                className="forgot-password-button"
                onClick={handleForgotPassword}
              >
                Forgot Password?
              </button>
            </div>

            <button type="submit" className="auth-button primary">
              Sign In
            </button>

            <div className="auth-divider">
              <span>or</span>
            </div>

            <button
              type="button"
              id="google-signin-button"
              className="auth-button google"
              onClick={handleGoogleSignIn}
            >
              <GoogleIcon size={20} />
              Sign In with Google
            </button>

            <p className="auth-switch">
              Not registered yet?{' '}
              <button type="button" onClick={toggleMode} className="link-button">
                Create an account
              </button>
            </p>
          </form>
        ) : (
          // Sign Up Form
          <form onSubmit={handleSignUp} className="auth-form">
            <button
              type="button"
              id="google-signup-button"
              className="auth-button google"
              onClick={handleGoogleSignUp}
            >
              <GoogleIcon size={20} />
              Sign Up with Google
            </button>

            <div className="auth-divider">
              <span>or</span>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input
                  type="text"
                  name="first_name"
                  value={signUpForm.first_name}
                  onChange={handleSignUpChange}
                  placeholder="First name"
                />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  value={signUpForm.last_name}
                  onChange={handleSignUpChange}
                  placeholder="Last name"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={signUpForm.email}
                onChange={handleSignUpChange}
                className={errors.email ? 'error' : ''}
                placeholder="Enter your email"
              />
              {errors.email && (
                <span className="error-message">{errors.email}</span>
              )}
            </div>

            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                name="username"
                value={signUpForm.username}
                onChange={handleSignUpChange}
                className={errors.username ? 'error' : ''}
                placeholder="Choose a username"
              />
              {errors.username && (
                <span className="error-message">{errors.username}</span>
              )}
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="password-field">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={signUpForm.password}
                  onChange={handleSignUpChange}
                  className={errors.password ? 'error' : ''}
                  placeholder="Create a password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <span className="error-message">{errors.password}</span>
              )}
            </div>

            <button type="submit" className="auth-button primary">
              Sign Up
            </button>

            <p className="auth-switch">
              Already have an account?{' '}
              <button type="button" onClick={toggleMode} className="link-button">
                Sign in
              </button>
            </p>
          </form>
        )}
      </div>

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        isOpen={showForgotPassword}
        onClose={() => setShowForgotPassword(false)}
      />
    </div>
  );
};

export default AuthenticationPage;
