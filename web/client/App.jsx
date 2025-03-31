import React from 'react';
import { Routes, Route } from "react-router-dom";
import { Toaster } from "@client/components/ui/toaster";
import Home from "@client/pages/Home";
import CartPage from "@client/pages/CartPage";
import CustomizePage from "@client/pages/CustomizePage";
import CategoryPage from "@client/pages/CategoryPage";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/customize" element={<CustomizePage />} />
        <Route path="/category/:category" element={<CategoryPage />} />
      </Routes>
      <Toaster />
    </>
  );
}

export default App;