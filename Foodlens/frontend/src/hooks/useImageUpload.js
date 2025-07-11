/**
 * Custom hook for image upload and OCR processing
 */
<<<<<<< HEAD

import { useState } from 'react';
import { analyzeImage } from '../services/api';

export const useImageUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const uploadImage = async (imageFile, language = 'tr', productName = '', brand = '') => {
    setUploading(true);
    setUploadError(null);

    try {
      const result = await analyzeImage(imageFile, language, productName, brand);
      return result;
    } catch (err) {
      setUploadError(err.message);
      throw err;
    } finally {
      setUploading(false);
    }
  };

  return {
    uploading,
    uploadError,
    uploadImage,
  };
};
=======
>>>>>>> fdd3cedf94404767e3a5728d43eb0c330c6b1ff6
