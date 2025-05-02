// Whisky Recognition Types
export interface WhiskyResultData {
  name: string;
  detected_name: string;
  confidence: number;
  pricing?: {
    market_price: number;
    retail_price: number;
  };
  batch_info?: string;
  variant_details?: string;
  timestamp?: number; // Adding timestamp for recent scans
}

export interface WhiskyContextType {
  file: File | null;
  setFile: (file: File | null) => void;
  preview: string | null;
  setPreview: (preview: string | null) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
  results: WhiskyResultData | null;
  setResults: (results: WhiskyResultData | null) => void;
  error: string | null;
  setError: (error: string | null) => void;
  analyzeImage: (file: File | string) => Promise<void>;
  resetRecognition: () => void;
  recentScans: WhiskyResultData[]; // Added recentScans array
  addToRecentScans: (scan: WhiskyResultData) => void; // Added method to add to recent scans
  clearRecentScans: () => void; // Added method to clear recent scans
}
