"use client";

import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';

const Header: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <header className="whisky-header bg-background/80 backdrop-blur-sm border-b border-[#FFD700]/10">
      <div className="container flex h-20 items-center justify-between px-4">
        <div className="flex items-center">
          <Image 
            src="/logo.png" 
            alt="Whisky Goggles Logo" 
            width={80} 
            height={80}
            className="rounded-sm drop-shadow-lg"
            priority
          />
        </div>

        {/* Navigation for larger screens */}
        <nav className="hidden md:flex gap-6">
          <a href="#" className="text-sm font-medium text-white hover:text-[#FFD700] transition-colors">Scanner</a>
          <a href="#" className="text-sm font-medium text-white hover:text-[#FFD700] transition-colors">Collection</a>
          <a href="#" className="text-sm font-medium text-white hover:text-[#FFD700] transition-colors">Database</a>
          <a href="#" className="text-sm font-medium text-white hover:text-[#FFD700] transition-colors">About</a>
        </nav>

        {/* Mobile menu button */}
        <button 
          onClick={toggleMenu}
          className="flex items-center justify-center p-2 md:hidden"
          aria-label="Toggle menu"
        >
          {isOpen ? (
            <X className="h-6 w-6 text-[#FFD700]" />
          ) : (
            <Menu className="h-6 w-6 text-[#FFD700]" />
          )}
        </button>
      </div>

      {/* Mobile navigation menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden overflow-hidden bg-card shadow-md"
          >
            <nav className="flex flex-col p-4 gap-3">
              <a 
                href="#" 
                className="flex py-2 text-sm font-medium text-white hover:text-[#FFD700] transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Scanner
              </a>
              <a 
                href="#" 
                className="flex py-2 text-sm font-medium text-white hover:text-[#FFD700] transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Collection
              </a>
              <a 
                href="#" 
                className="flex py-2 text-sm font-medium text-white hover:text-[#FFD700] transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Database
              </a>
              <a 
                href="#" 
                className="flex py-2 text-sm font-medium text-white hover:text-[#FFD700] transition-colors"
                onClick={() => setIsOpen(false)}
              >
                About
              </a>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Header;
