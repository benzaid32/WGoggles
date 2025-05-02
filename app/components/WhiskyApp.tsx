"use client";

import React, { useState, useEffect } from 'react';
import { useWhisky } from "../context/WhiskyContext";
import { motion, AnimatePresence } from "framer-motion";
import ScanCamera from './features/scanner/ScanCamera';
import ScanResults from './features/scanner/ScanResults';
import RecentScans from './features/scanner/RecentScans';
import Image from 'next/image';
import { Clock, ArrowLeft, Camera, Search } from 'lucide-react';

const WhiskyApp: React.FC = () => {
  const [showResults, setShowResults] = useState(false);
  const [showRecents, setShowRecents] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { resetRecognition, recentScans } = useWhisky();
  
  // Track scroll for header effect
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  const handleScanComplete = () => {
    setShowResults(true);
    setShowRecents(false);
  };
  
  const handleBack = () => {
    setShowResults(false);
    resetRecognition();
  };
  
  // Handle selecting a recent scan
  const handleSelectRecentScan = () => {
    setShowResults(true);
    setShowRecents(false);
  };
  
  const toggleRecents = () => {
    setShowRecents(!showRecents);
    if (showResults) {
      setShowResults(false);
      resetRecognition();
    }
  };
  
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-[#1b1a1a] via-[#222120] to-[#262523]">
      <AnimatePresence mode="wait">
        {/* Main content area with animation between states */}
        <div className="flex-1 h-full relative">
          {showResults ? (
            <motion.div
              key="results"
              initial={{ opacity: 0, x: '100%' }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="h-full pt-6 pb-20 px-4"
            >
              <ScanResults onBack={handleBack} />
            </motion.div>
          ) : showRecents ? (
            <motion.div
              key="recents"
              initial={{ opacity: 0, x: '100%' }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="h-full pt-6 pb-20 px-4"
            >
              <div className="flex items-center mb-6">
                <button 
                  onClick={toggleRecents}
                  className="flex items-center gap-2 text-[#FFD700]"
                >
                  <ArrowLeft className="h-5 w-5" />
                  <span className="font-medium">Back to Scanner</span>
                </button>
              </div>
              <RecentScans onSelectScan={handleSelectRecentScan} />
            </motion.div>
          ) : (
            <motion.div
              key="scanner"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
              className="h-full"
            >
              {/* Logo area with subtle parallax effect */}
              <motion.div 
                className="text-center pt-14 pb-6 px-4"
                style={{ 
                  opacity: scrolled ? 0.6 : 1,
                  scale: scrolled ? 0.95 : 1,
                }}
                transition={{ duration: 0.3 }}
              >
                <motion.div 
                  className="flex justify-center mb-5"
                  animate={{ y: scrolled ? -10 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Image 
                    src="/logo.png" 
                    alt="Whisky Goggles" 
                    width={160} 
                    height={160}
                    className="rounded-lg drop-shadow-xl"
                    priority
                  />
                </motion.div>
                <motion.p 
                  className="text-lg font-medium mt-2 mb-4 text-white max-w-md mx-auto"
                  animate={{ y: scrolled ? -5 : 0, opacity: scrolled ? 0.8 : 1 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                >
                  <span className="text-[#FFD700]">Instantly identify</span> and track whisky bottle prices
                </motion.p>
              </motion.div>
              
              {/* Scanner component */}
              <div className="px-4 pb-24">
                <ScanCamera onScanComplete={handleScanComplete} />
              </div>
            </motion.div>
          )}
        </div>
      </AnimatePresence>
      
      {/* App navigation bar - fixed at bottom of viewport */}
      <div className="fixed bottom-0 left-0 right-0 flex justify-center pb-4 z-50">
        <motion.div 
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5, type: 'spring' }}
          className="px-5 py-3 bg-[#1d1c1b]/90 backdrop-blur-xl border border-[#FFD700]/20 rounded-full shadow-xl"
        >
          <div className="flex gap-10">
            <button 
              onClick={() => {
                setShowResults(false);
                setShowRecents(false);
                resetRecognition();
              }}
              className={`flex items-center gap-2 rounded-full px-3 py-1.5 ${!showResults && !showRecents 
                ? 'text-white bg-[#FFD700]/20' 
                : 'text-[#a19789] hover:text-white transition-colors'}`}
              aria-label="Scanner"
            >
              <Camera className="h-5 w-5" />
              <span className="text-sm font-medium">Scanner</span>
            </button>
            
            <button 
              onClick={toggleRecents}
              className={`flex items-center gap-2 rounded-full px-3 py-1.5 relative ${showRecents 
                ? 'text-white bg-[#FFD700]/20' 
                : 'text-[#a19789] hover:text-white transition-colors'}`}
              disabled={recentScans.length === 0}
              aria-label="History"
            >
              <Clock className="h-5 w-5" />
              <span className="text-sm font-medium">History</span>
              <span className={`absolute -top-1 -right-1 bg-[#FFD700] text-[#1b1a1a] text-[10px] w-4 h-4 flex items-center justify-center rounded-full font-bold ${recentScans.length > 0 ? 'opacity-100' : 'opacity-0'}`}>
                {recentScans.length || 0}
              </span>
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default WhiskyApp;
