import React from 'react';
import './styles/globals.css';

// Import main component
import HomePage from './pages/HomePage';

// Import components
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <main className="min-h-screen">
          <HomePage />
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
