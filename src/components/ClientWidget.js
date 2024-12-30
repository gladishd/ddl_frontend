import React, { useState, useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function ClientWidget({ title, clientData }) {
  const { name, ip, port, type, link } = clientData;
  const { status, statistics } = link;
  const [ppsHistory, setPpsHistory] = useState([]);
  const lastUpdateTime = useRef(Date.now());
  
  useEffect(() => {
    const currentTime = Date.now();
    const timeDiff = currentTime - lastUpdateTime.current;
    
    // Add new PPS value to history regardless of the value
    setPpsHistory(prev => {
      const newHistory = [...prev];
      
      // If more than 800ms has passed since last update, fill in zeros
      if (timeDiff > 800) {
        const missedUpdates = Math.floor(timeDiff / 1000);
        for (let i = 0; i < missedUpdates && newHistory.length < 30; i++) {
          newHistory.push(0);
        }
      }
      
      // Add the current PPS value
      newHistory.push(statistics.pps);
      return newHistory.slice(-30);
    });
    
    lastUpdateTime.current = currentTime;
  }, [statistics.pps]);

  const chartData = {
    labels: [...Array(ppsHistory.length)].map((_, i) => -ppsHistory.length + i + 1),
    datasets: [
      {
        label: 'PPS',
        data: ppsHistory,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        pointRadius: 0,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Seconds ago'
        },
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    }
  };

  return (
    <div className="client-widget">
      <h3>{title}</h3>
      <div className="widget-content">
        <div className="stat-row">
          <span className="stat-label">Name:</span>
          <span className="stat-value">{name}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Type:</span>
          <span className="stat-value">{type}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Address:</span>
          <span className="stat-value">{`${ip}:${port}`}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Status:</span>
          <span className={`stat-value status-${status}`}>{status}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Events:</span>
          <span className="stat-value">{statistics.events}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Latency:</span>
          <span className="stat-value">
            {(statistics.round_trip_latency * 1000).toFixed(2)} ms
          </span>
        </div>
        <div className="stat-row">
          <span className="stat-label">PPS:</span>
          <span className="stat-value">
            {Math.round(statistics.pps)}
          </span>
        </div>
        <div className="chart-container">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}

export default ClientWidget; 