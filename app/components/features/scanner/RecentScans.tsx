"use client";

import React from 'react';
import { useWhisky } from "../../../context/WhiskyContext";
import { Clock, Trash2 } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "../../ui/button";

interface RecentScansProps {
  onSelectScan: (scanResult: any) => void;
}

const RecentScans: React.FC<RecentScansProps> = ({ onSelectScan }) => {
  const { recentScans, clearRecentScans, setResults } = useWhisky();
  
  // Format date for display
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    }).format(date);
  };
  
  // Format price for display
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };
  
  // Handle scan selection
  const handleSelectScan = (scan: any) => {
    setResults(scan);
    onSelectScan(scan);
  };
  
  if (recentScans.length === 0) {
    return (
      <div className="p-4 text-center text-muted-foreground">
        <Clock className="w-6 h-6 mx-auto mb-2 opacity-40" />
        <p>No recent scans</p>
      </div>
    );
  }
  
  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-medium text-lg flex items-center text-white">
          <Clock className="w-4 h-4 mr-2 text-whisky-amber" />
          Recent Scans
        </h3>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={clearRecentScans}
          className="text-white hover:text-red-400 hover:bg-red-400/10"
        >
          <Trash2 className="w-4 h-4 mr-1" />
          Clear
        </Button>
      </div>
      
      <div className="space-y-3">
        {recentScans.map((scan, index) => (
          <motion.div
            key={`${scan.name}-${scan.timestamp}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="border border-whisky-amber/30 bg-[#262321]/70 rounded-lg p-3 cursor-pointer hover:border-whisky-amber hover:bg-[#28241f] transition-colors shadow-sm"
            onClick={() => handleSelectScan(scan)}
          >
            <div className="flex justify-between">
              <div>
                <h4 className="font-semibold text-white">{scan.name}</h4>
                <p className="text-sm text-whisky-amber/70">
                  {scan.timestamp && formatDate(scan.timestamp)}
                </p>
              </div>
              <div className="text-right">
                {scan.pricing && (
                  <p className="font-bold text-whisky-amber text-lg">
                    {formatPrice(scan.pricing.market_price)}
                  </p>
                )}
                <p className="text-xs text-white/60">Market price</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default RecentScans;
