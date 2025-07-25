/**
 * Custom hook for API data fetching with loading and error states
 */
<<<<<<< HEAD

import { useState } from 'react';
import { apiRequest } from '../services/api';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callApi = async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiRequest(endpoint, options);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    callApi,
  };
};
=======
>>>>>>> fdd3cedf94404767e3a5728d43eb0c330c6b1ff6
