import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Button from '@shared/components/Button';

function Dashboard() {
  return (
    <div>
      <h1>Admin Dashboard</h1>
      <p>Welcome to the admin panel!</p>
      <Button>View Products</Button>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
    </Routes>
  );
}
