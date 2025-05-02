"use client";

import React from 'react';
import { useWhisky } from "../../../context/WhiskyContext";
import { ArrowLeft, Star, DollarSign, ExternalLink, Clock, Info, ThumbsUp } from "lucide-react";
import { motion } from "framer-motion";
import { Bar } from 'react-chartjs-2';
import { Button } from "../../ui/button";

interface ScanResultsProps {
  onBack: () => void;
}

const ScanResults: React.FC<ScanResultsProps> = ({ onBack }) => {
  const { results, error, file, preview } = useWhisky();

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full bg-card rounded-lg border border-destructive/20 p-6 shadow-sm"
      >
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="p-3 rounded-full bg-destructive/10 text-destructive">
            <Info className="h-8 w-8" />
          </div>
          <h3 className="text-xl font-semibold">Recognition Error</h3>
          <p className="text-muted-foreground">{error}</p>
          <Button 
            onClick={onBack}
            variant="outline"
            className="flex items-center gap-2 mt-4 text-whisky-amber"
          >
            <ArrowLeft className="h-4 w-4" />
            Try Again
          </Button>
        </div>
      </motion.div>
    );
  }

  if (!results) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full flex justify-center p-12"
      >
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 rounded-full border-4 border-whisky-amber border-t-transparent animate-spin"></div>
          <p className="mt-4 text-muted-foreground">Processing your whisky...</p>
        </div>
      </motion.div>
    );
  }

  // Chart data for price comparison
  const chartData = {
    labels: ['Market Price', 'Retail Price'],
    datasets: [
      {
        label: 'Price (USD)',
        data: [
          results.pricing && results.pricing.market_price ? results.pricing.market_price : 0,
          results.pricing && results.pricing.retail_price ? results.pricing.retail_price : 0,
        ],
        backgroundColor: [
          'rgba(245, 158, 11, 0.8)',  // whisky-amber
          'rgba(180, 83, 9, 0.8)',    // whisky-copper
        ],
        borderColor: [
          'rgba(245, 158, 11, 1)',
          'rgba(180, 83, 9, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `$${context.raw.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '$' + value;
          }
        }
      }
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="w-full"
    >
      <div className="flex flex-col space-y-6">
        {/* Back button and title */}
        <div className="flex items-center mb-4">
          <button 
            onClick={onBack}
            className="flex items-center gap-1 p-2 text-whisky-amber hover:bg-whisky-amber/10 rounded-full"
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="sr-only">Back</span>
          </button>
          <h2 className="ml-2 text-xl font-bold whisky-gradient-text">Recognition Results</h2>
        </div>

        {/* Main content */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Whisky image and preview */}
          <div className="md:col-span-1">
            <div className="whisky-card p-4 bg-card">
              <div className="aspect-square w-full flex items-center justify-center overflow-hidden rounded-md bg-whisky-light/30">
                {preview && (
                  <img 
                    src={preview} 
                    alt={results.name || "Detected whisky"} 
                    className="object-contain h-full w-full" 
                  />
                )}
              </div>
              <div className="mt-4 flex justify-between items-center">
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <span>Scanned {new Date().toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-1.5 bg-whisky-amber/10 px-2.5 py-1 rounded-full text-whisky-amber">
                  <ThumbsUp className="h-3.5 w-3.5" />
                  <span className="text-xs font-medium">
                    {((results.confidence || 0.9) * 100).toFixed(0)}% Match
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Whisky details */}
          <div className="md:col-span-1">
            <div className="whisky-card p-4 bg-card h-full flex flex-col">
              <div className="mb-4">
                {/* Display the exact matched BAXUS database name */}
                <h3 className="text-xl font-bold">{results.name || "Unknown Whisky"}</h3>
                {/* If the detected name differs from the matched BAXUS name, show both for transparency */}
                {results.detected_name && results.detected_name !== results.name && (
                  <p className="text-sm text-muted-foreground mt-1">
                    Detected as: {results.detected_name}
                  </p>
                )}
              </div>

              {/* Pricing information from BAXUS database */}
              {results.pricing && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-whisky-amber/5 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <DollarSign className="h-4 w-4 text-whisky-amber" />
                        <span className="text-sm font-medium">Market Price</span>
                      </div>
                      <p className="text-lg font-bold">
                        ${results.pricing.market_price?.toFixed(2) || 'N/A'}
                      </p>
                    </div>
                    <div className="p-3 bg-whisky-copper/5 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Star className="h-4 w-4 text-whisky-copper" />
                        <span className="text-sm font-medium">Retail Price</span>
                      </div>
                      <p className="text-lg font-bold">
                        ${results.pricing.retail_price?.toFixed(2) || 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Price comparison chart */}
                  <div className="mt-6">
                    <h4 className="text-sm font-medium mb-2">Price Comparison</h4>
                    <div className="h-[180px]">
                      <Bar data={chartData} options={chartOptions} />
                    </div>
                  </div>
                </div>
              )}

              {/* Display batch information if available (from your variant detection system) */}
              {results.batch_info && (
                <div className="mt-4 p-3 bg-whisky-light/30 rounded-lg">
                  <h4 className="text-sm font-medium mb-1">Batch Details</h4>
                  <p className="text-sm">{results.batch_info}</p>
                </div>
              )}

              {/* Links and actions */}
              <div className="mt-auto pt-4">
                <div className="border-t border-whisky-amber/10 pt-4">
                  <Button variant="ghost" className="flex items-center gap-2 text-sm text-whisky-amber hover:text-whisky-copper">
                    <ExternalLink className="h-4 w-4" />
                    <span>View Details</span>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ScanResults;
