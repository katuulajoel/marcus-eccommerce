import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { CartProvider } from '@client/context/cart-context';
import { AuthProvider } from '@client/context/auth-context';
import { CurrencyProvider } from '@shared/contexts/currency-context';
import { AIAssistantProvider } from '@client/context/ai-assistant-context';
import App from './App';
import './index.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <CurrencyProvider>
          <AuthProvider>
            <AIAssistantProvider>
              <CartProvider>
                <App />
              </CartProvider>
            </AIAssistantProvider>
          </AuthProvider>
        </CurrencyProvider>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
);