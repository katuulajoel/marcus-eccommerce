import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Button from '@shared/components/Button';

function Home() {
  return (
    <div>
      <h1>Marcus eCommerce Store</h1>
      <p>Welcome to our online store!</p>
      <Button>Shop Now</Button>
    </div>
  );
}

function NotFound() {
  return <h1>404 - Page Not Found</h1>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
