"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, X, Image as ImageIcon, RefreshCw } from "lucide-react";
import { useWhisky } from "../../../context/WhiskyContext";
import { motion } from "framer-motion";
import { Button } from "../../ui/button";

const ScanCamera: React.FC<{ onScanComplete: () => void }> = ({ onScanComplete }) => {
  const { file, setFile, preview, setPreview, loading, analyzeImage, resetRecognition } = useWhisky();
  const [captureMode, setCaptureMode] = useState<'camera' | 'upload'>('upload');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [cameraReady, setCameraReady] = useState(false);

  // Handle file upload
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    handleSelectedFile(selectedFile);
  };

  const handleSelectedFile = (selectedFile?: File) => {
    if (selectedFile) {
      setFile(selectedFile);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          setPreview(e.target.result as string);
        }
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  // Handle drag events
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  };

  // Reset the file input
  const handleReset = () => {
    resetRecognition();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle analyze button click
  const handleAnalyze = async () => {
    if (file) {
      await analyzeImage(file);
      onScanComplete();
    } else if (preview) {
      // Handle case where we have preview from webcam
      await analyzeImage(preview);
      onScanComplete();
    }
  };

  // Initialize camera when in camera mode
  useEffect(() => {
    if (captureMode === 'camera') {
      startCamera();
    } else {
      stopCamera();
    }

    // Cleanup function to stop camera when component unmounts
    return () => {
      stopCamera();
    };
  }, [captureMode]);

  // Event handler for when video is ready
  const handleVideoPlay = () => {
    setCameraReady(true);
  };

  // Start the camera
  const startCamera = async () => {
    try {
      setCameraError(null);

      // Reset any previous preview
      setPreview(null);

      // Request camera access with specific constraints for mobile compatibility
      const constraints = {
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };

      // Try to get user media with better error handling
      try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        setCameraStream(stream);

        // Connect stream to video element
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err: any) {
        console.error('Initial camera error:', err);

        // If environment camera fails, try without facingMode constraint
        if (err.name === 'OverconstrainedError' || err.name === 'ConstraintNotSatisfiedError') {
          const fallbackStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
          });
          
          setCameraStream(fallbackStream);
          
          if (videoRef.current) {
            videoRef.current.srcObject = fallbackStream;
          }
        } else {
          throw err; // Re-throw for the outer catch block
        }
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setCameraError('Unable to access camera. Please ensure camera permissions are granted and you are using a secure connection (HTTPS).');
    }
  };

  // Stop the camera
  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  // Take a photo from the camera
  const capturePhoto = () => {
    if (!videoRef.current) return;
    
    try {
      // Ensure video is ready
      if (videoRef.current.readyState !== 4) {
        setCameraError('Camera not ready. Please wait a moment and try again.');
        return;
      }

      // Create a canvas element to capture the frame
      const canvas = document.createElement('canvas');
      const videoWidth = videoRef.current.videoWidth;
      const videoHeight = videoRef.current.videoHeight;
      
      // Handle case where dimensions are not available yet
      if (!videoWidth || !videoHeight) {
        setCameraError('Unable to capture image. Please try again.');
        return;
      }
      
      canvas.width = videoWidth;
      canvas.height = videoHeight;
      
      // Draw the video frame to the canvas
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        // Convert to data URL with lower quality for better performance
        const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
        setPreview(dataUrl);
        stopCamera(); // Stop camera after taking photo
      }
    } catch (err) {
      console.error('Error capturing photo:', err);
      setCameraError('Failed to capture photo. Please try again.');
    }
  };

  return (
    <motion.div
      className="w-full"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="p-4 bg-card rounded-lg border border-[#FFD700]/20 shadow-sm">
        <div className="flex justify-center mb-6">
          <div className="flex rounded-lg border border-[#FFD700]/20 overflow-hidden">
            <button
              onClick={() => setCaptureMode('upload')}
              className={`px-4 py-2 flex items-center gap-2 ${
                captureMode === 'upload'
                  ? 'bg-[#FFD700] text-[#1b1a1a]'
                  : 'hover:bg-[#FFD700]/10 text-white'
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </button>
            <button
              onClick={() => setCaptureMode('camera')}
              className={`px-4 py-2 flex items-center gap-2 ${
                captureMode === 'camera'
                  ? 'bg-[#B45309] text-white font-bold'
                  : 'bg-[#B45309]/80 text-white'
              }`}
            >
              <Camera className="h-4 w-4" />
              <span>Camera</span>
            </button>
          </div>
        </div>

        {captureMode === 'upload' ? (
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors overflow-hidden
              ${dragActive ? 'border-[#FFD700] bg-[#FFD700]/5' : 'border-[#FFD700]/30'}
              ${!dragActive && 'hover:border-[#FFD700]/60 hover:bg-[#FFD700]/5'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              background: !preview ? 'radial-gradient(circle at top right, rgba(255, 215, 0, 0.08) 0%, rgba(25, 24, 23, 0) 60%), radial-gradient(circle at bottom left, rgba(255, 215, 0, 0.05) 0%, rgba(25, 24, 23, 0) 60%)' : 'none',
              boxShadow: 'inset 0 0 30px rgba(0, 0, 0, 0.2)'
            }}
          >
            {/* Decorative whisky glass SVG */}
            {!preview && (
              <div className="absolute opacity-5 right-4 bottom-4 w-32 h-32">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 2H16M9 22H15M12 2V22M17 2L16 8C16 10 17 11 17 11C17 11 17.5 12 18 14C18.5 16 18 22 18 22M7 2L8 8C8 10 7 11 7 11C7 11 6.5 12 6 14C5.5 16 6 22 6 22" 
                    stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-[#FFD700]"/>
                </svg>
              </div>
            )}
            
            {/* Decorative barrels pattern */}
            {!preview && (
              <div className="absolute opacity-[0.03] left-0 top-0 w-full h-full pointer-events-none">
                <div className="absolute left-4 top-10 w-20 h-20">
                  <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M30 20H70M30 50H70M30 80H70M20 30V70M50 30V70M80 30V70M20 20C20 15 25 10 30 10H70C75 10 80 15 80 20M20 80C20 85 25 90 30 90H70C75 90 80 85 80 80" 
                      stroke="currentColor" strokeWidth="4" strokeLinecap="round" className="text-[#FFD700]"/>
                  </svg>
                </div>
              </div>
            )}
            
            <input
              ref={fileInputRef}
              type="file"
              id="fileInput"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            
            {!preview ? (
              <div className="space-y-4 relative z-10">
                <div className="flex justify-center">
                  <div className="bg-[#2A2725] p-5 rounded-full border border-[#FFD700]/20 shadow-inner">
                    <ImageIcon className="h-10 w-10 text-[#FFD700]" />
                  </div>
                </div>
                <div>
                  <p className="text-lg font-medium text-white">Drag and drop your image here</p>
                  <p className="text-sm text-[#a19789]">or</p>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="mt-2 px-6 py-2.5 bg-white text-[#1b1a1a] rounded-md hover:bg-white/90 transition-all shadow-md border border-[#FFD700]/30"
                  >
                    Choose file
                  </button>
                  <p className="mt-2 text-xs text-[#a19789]">Supports JPG, PNG and GIF up to 5MB</p>
                </div>
              </div>
            ) : (
              <div className="relative">
                <img
                  src={preview}
                  alt="Preview"
                  className="max-h-64 mx-auto rounded-md shadow-sm"
                />
                <button
                  onClick={handleReset}
                  className="absolute top-2 right-2 p-1.5 bg-black/50 text-white rounded-full hover:bg-black/70 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center border-2 border-dashed border-[#FFD700]/30 rounded-lg overflow-hidden">
            {cameraError ? (
              <div className="p-6">
                <p className="text-destructive font-medium mb-2">{cameraError}</p>
                <button
                  onClick={startCamera}
                  className="mt-2 px-4 py-2 bg-[#FFD700] text-[#1b1a1a] rounded-md hover:bg-[#FFD700]/90 transition-colors flex items-center justify-center gap-2 mx-auto"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </button>
              </div>
            ) : (
              <>
                {!preview ? (
                  <div className="relative">
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full max-h-64 mx-auto bg-black"
                      onPlay={handleVideoPlay}
                      onCanPlay={() => setCameraReady(true)}
                    />
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      <div className="w-48 h-48 border-2 border-[#FFD700] rounded-lg opacity-50"></div>
                    </div>
                    <button 
                      onClick={capturePhoto}
                      className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-8 py-4 bg-white text-[#1b1a1a] rounded-full hover:bg-white/90 transition-colors shadow-2xl border-2 border-[#FFD700]/30 font-medium text-base"
                      disabled={!cameraReady}
                    >
                      <Camera className="inline-block mr-2 h-5 w-5 text-[#1b1a1a]" />
                      {cameraReady ? 'Take Photo' : 'Camera Loading...'}
                    </button>
                  </div>
                ) : (
                  <div className="relative">
                    <img
                      src={preview}
                      alt="Preview"
                      className="max-h-64 mx-auto"
                    />
                    <button
                      onClick={() => {
                        setPreview(null);
                        startCamera();
                      }}
                      className="absolute top-2 right-2 p-1.5 bg-black/50 text-white rounded-full hover:bg-black/70 transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {preview && (
          <div className="mt-6 flex justify-center">
            <Button
              onClick={handleAnalyze}
              disabled={loading}
              variant="whisky"
              className="px-6 py-3 bg-[#FFD700] text-[#1b1a1a]"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-[#1b1a1a]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                <>
                  Recognize Whisky
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ScanCamera;
