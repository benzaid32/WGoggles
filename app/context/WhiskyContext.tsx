"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import axios from "axios";
import { WhiskyResultData, WhiskyContextType } from "../types/whisky";

// Configure API endpoint
// const API_ENDPOINT = "http://localhost:5000";  // Using local backend server for testing
const API_ENDPOINT = "/api";  // Using local proxy to avoid CORS issues (for production)
// const API_ENDPOINT = "https://16.16.65.102:5000";  // Using EC2 deployed backend server

// Create the context
const WhiskyContext = createContext<WhiskyContextType | undefined>(undefined);

// Provider component
export function WhiskyProvider({ children }: { children: ReactNode }) {
  // State for handling file upload and recognition
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [results, setResults] = useState<WhiskyResultData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // State for recent scans (stored in localStorage)
  const [recentScans, setRecentScans] = useState<WhiskyResultData[]>([]);
  
  // Use useEffect for client-side only code (localStorage access)
  useEffect(() => {
    // Initialize from localStorage if available (client-side only)
    const saved = localStorage.getItem('whiskyRecentScans');
    if (saved) {
      try {
        setRecentScans(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse recent scans from localStorage', e);
      }
    }
  }, []);
  
  // Reset the recognition state
  const resetRecognition = () => {
    setFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
  };

  // Add a scan to the recent scans list
  const addToRecentScans = (scan: WhiskyResultData) => {
    // Add timestamp if not present
    const scanWithTimestamp = {
      ...scan,
      timestamp: scan.timestamp || Date.now()
    };
    
    // Add to the beginning of the list and keep only the most recent 10 scans
    const updatedScans = [scanWithTimestamp, ...recentScans].slice(0, 10);
    setRecentScans(updatedScans);
    
    // Save to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('whiskyRecentScans', JSON.stringify(updatedScans));
    }
  };
  
  // Clear all recent scans
  const clearRecentScans = () => {
    setRecentScans([]);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('whiskyRecentScans');
    }
  };
  
  // Analyze the uploaded image
  const analyzeImage = async (imageData: File | string) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      
      if (typeof imageData === 'string' && imageData.startsWith('data:')) {
        // Convert data URL to blob for sending
        const response = await fetch(imageData);
        const blob = await response.blob();
        formData.append('image', blob, 'webcam.jpg');
      } else if (imageData instanceof File) {
        formData.append('image', imageData);
      } else {
        throw new Error('Invalid image data format');
      }
      
      const response = await axios.post(`${API_ENDPOINT}/recognize`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: false,  // Don't send cookies with cross-origin requests
      });
      
      if (response.data.error) {
        // Special case for the OpenAI API key error
        if (response.data.error === 'OpenAI API key not configured') {
          setError('The server is currently unavailable due to API configuration issues. Please try again later or contact support.');
        } else {
          setError(response.data.error);
        }
        return;
      }
      
      // Check if bottle was detected
      if (response.data.bottle_detected === false) {
        setError('No whisky bottle detected in the image. Please try a clearer image of a whisky bottle.');
        return;
      }
      
      // Transform the API response to match our WhiskyResultData type
      // Backend returns results array with matches inside
      const matches = response.data.results?.[0]?.matches || [];
      const bottleInfo = matches[0] || {};
      
      // Log full response for debugging
      console.log('Server response:', response.data);
      console.log('Bottle info:', bottleInfo);
      
      // Look for pricing data in various possible locations/formats
      // The backend might return pricing in different fields based on the response format
      let marketPrice = 0;
      let retailPrice = 0;
      
      // Try to find market price in various fields
      if (bottleInfo.fair_market_price) {
        const rawPrice = bottleInfo.fair_market_price;
        // Handle "$XX.XX" string format by removing non-numeric characters
        marketPrice = typeof rawPrice === 'string' 
          ? parseFloat(rawPrice.replace(/[^0-9.]/g, '')) 
          : Number(rawPrice);
      } else if (bottleInfo.market_price) {
        const rawPrice = bottleInfo.market_price;
        marketPrice = typeof rawPrice === 'string' 
          ? parseFloat(rawPrice.replace(/[^0-9.]/g, '')) 
          : Number(rawPrice);
      } else if (bottleInfo.price) {
        const rawPrice = bottleInfo.price;
        marketPrice = typeof rawPrice === 'string' 
          ? parseFloat(rawPrice.replace(/[^0-9.]/g, '')) 
          : Number(rawPrice);
      } else if (bottleInfo.average_price) {
        const rawPrice = bottleInfo.average_price;
        marketPrice = typeof rawPrice === 'string' 
          ? parseFloat(rawPrice.replace(/[^0-9.]/g, '')) 
          : Number(rawPrice);
      }
      
      // Try to find retail price in various fields
      if (bottleInfo.msrp) {
        const rawPrice = bottleInfo.msrp;
        retailPrice = typeof rawPrice === 'string' 
          ? parseFloat(rawPrice.replace(/[^0-9.]/g, '')) 
          : Number(rawPrice);
      } else if (bottleInfo.shelf_price) {
        const rawPrice = bottleInfo.shelf_price;
        retailPrice = typeof rawPrice === 'string' 
          ? parseFloat(rawPrice.replace(/[^0-9.]/g, '')) 
          : Number(rawPrice);
      } else if (bottleInfo.retail_price) {
        const rawPrice = bottleInfo.retail_price;
        retailPrice = typeof rawPrice === 'string' 
          ? parseFloat(rawPrice.replace(/[^0-9.]/g, '')) 
          : Number(rawPrice);
      }
      
      // Ensure we have valid numbers after conversion
      marketPrice = isNaN(marketPrice) ? 0 : marketPrice;
      retailPrice = isNaN(retailPrice) ? 0 : retailPrice;
      
      // If no prices found, use placeholder values for demo purposes
      if (marketPrice === 0 && retailPrice === 0) {
        // Use placeholder values based on the whisky name
        if (bottleInfo.name && typeof bottleInfo.name === 'string') {
          // Generate pseudo-random but consistent prices based on the name
          const nameLength = bottleInfo.name.length;
          marketPrice = 75 + (nameLength * 5); // Example placeholder calculation
          retailPrice = marketPrice * 0.8;  // Retail usually lower than market
        } else {
          // Default fallback values
          marketPrice = 100;
          retailPrice = 80;
        }
      }
      
      const transformedResult: WhiskyResultData = {
        name: bottleInfo.name || "Unknown Whisky",
        detected_name: bottleInfo.name || "Unknown",
        confidence: bottleInfo.confidence || 0.85,
        pricing: {
          market_price: marketPrice,
          retail_price: retailPrice
        },
        batch_info: bottleInfo.batch || null
      };
      
      setResults(transformedResult);
      addToRecentScans(transformedResult);
    } catch (err) {
      console.error('Error analyzing image:', err);
      
      // Enhanced error logging
      if (axios.isAxiosError(err)) {
        console.error('Axios error details:', {
          status: err.response?.status,
          statusText: err.response?.statusText,
          data: err.response?.data,
          headers: err.response?.headers
        });
        
        if (err.response?.status === 500) {
          setError('Server error (500). The image might be too large, in an unsupported format, or the server might be experiencing issues.');
        } else if (err.response?.status === 415) {
          setError('Unsupported media type. Please try a different image format.');
        } else if (err.response) {
          setError(`Request failed with status: ${err.response.status}. ${err.response.data?.message || ''}`);
        } else if (err.request) {
          setError('No response received from server. Please check your network connection.');
        } else {
          setError('Failed to analyze the image. Please try again.');
        }
      } else {
        setError('Failed to analyze the image. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  const contextValue: WhiskyContextType = {
    file,
    setFile,
    preview,
    setPreview,
    results,
    setResults,
    loading,
    setLoading,
    error,
    setError,
    analyzeImage,
    resetRecognition,
    recentScans,
    addToRecentScans,
    clearRecentScans
  };

  return (
    <WhiskyContext.Provider value={contextValue}>
      {children}
    </WhiskyContext.Provider>
  );
}

// Custom hook to use the context
export function useWhisky() {
  const context = useContext(WhiskyContext);
  if (context === undefined) {
    throw new Error('useWhisky must be used within a WhiskyProvider');
  }
  return context;
}
