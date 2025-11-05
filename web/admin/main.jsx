import React from "react"
import ReactDOM from "react-dom/client"
import { BrowserRouter } from "react-router-dom"
import App from "./App"
import "./index.css"
import { ThemeProvider } from "@admin/context/theme-provider"
import { AuthProvider } from "@admin/context/auth-context"
import { CurrencyProvider } from "@shared/contexts/currency-context"

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <CurrencyProvider>
        <ThemeProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </ThemeProvider>
      </CurrencyProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
