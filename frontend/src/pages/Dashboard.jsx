import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '';

function Dashboard() {
  const [stats, setStats] = useState({
    total_products: 0,
    total_customers: 0,
    total_orders: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div>
      <h2>Dashboard</h2>
      <div className="dashboard-cards">
        <div className="card">
          <h3>Total Products</h3>
          <div className="number">{stats.total_products}</div>
        </div>
        <div className="card">
          <h3>Total Customers</h3>
          <div className="number">{stats.total_customers}</div>
        </div>
        <div className="card">
          <h3>Total Orders</h3>
          <div className="number">{stats.total_orders}</div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;