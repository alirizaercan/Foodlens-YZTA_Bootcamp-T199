/**
 * Loading spinner component for async operations
 */
<<<<<<< HEAD
import React from 'react';

const LoadingSpinner = ({ message = 'Loading...', size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`animate-spin rounded-full border-4 border-gray-300 border-t-blue-500 ${sizeClasses[size]}`}></div>
      {message && (
        <p className="mt-4 text-gray-600 text-center">{message}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
=======
>>>>>>> fdd3cedf94404767e3a5728d43eb0c330c6b1ff6
