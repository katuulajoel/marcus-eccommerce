import React from 'react';
import { Routes, Route } from "react-router-dom";
import { Toaster } from "@shared/components/ui/toaster";
import { AIAssistant } from "@client/components/ai-assistant";
import Home from "@client/pages/Home";
import CartPage from "@client/pages/CartPage";
import CustomizePage from "@client/pages/CustomizePage";
import CategoryPage from "@client/pages/CategoryPage";
import LoginPage from "@client/pages/LoginPage";
import RegisterPage from "@client/pages/RegisterPage";
import ForgotPasswordPage from "@client/pages/ForgotPasswordPage";
import ResetPasswordPage from "@client/pages/ResetPasswordPage";
import VerifyEmailPage from "@client/pages/VerifyEmailPage";
import CheckoutPage from "@client/pages/CheckoutPage";
import OrdersPage from "@client/pages/OrdersPage";
import OrderDetailPage from "@client/pages/OrderDetailPage";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/customize" element={<CustomizePage />} />
        <Route path="/category/:category" element={<CategoryPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password/:token" element={<ResetPasswordPage />} />
        <Route path="/verify-email/:token" element={<VerifyEmailPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/orders/:id" element={<OrderDetailPage />} />
      </Routes>
      <Toaster />
      <AIAssistant />
    </>
  );
}

export default App;