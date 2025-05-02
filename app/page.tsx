"use client";

import React from 'react';
import WhiskyApp from './components/WhiskyApp';
import { WhiskyProvider } from "./context/WhiskyContext";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function Home() {
  return (
    <WhiskyProvider>
      <WhiskyApp />
    </WhiskyProvider>
  );
}
