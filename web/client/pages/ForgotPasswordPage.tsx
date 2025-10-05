"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { Button } from "@shared/components/ui/button"
import { Input } from "@shared/components/ui/input"
import { Label } from "@shared/components/ui/label"
import axios from "axios"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("")
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      await axios.post(`${API_BASE_URL}/api/auth/forgot-password/`, { email })
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.error || "Failed to send reset email. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <SiteHeader />

      <main className="flex-1 container mx-auto px-4 py-8 flex items-center justify-center">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-lg border shadow-sm p-8">
            <h1 className="text-2xl font-bold mb-6 text-center">Reset Password</h1>

            {success ? (
              <div className="text-center">
                <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-md">
                  <p className="font-medium">Check your email!</p>
                  <p className="text-sm mt-2">
                    We've sent you a password reset link. Please check your inbox and follow the instructions.
                  </p>
                </div>
                <Link to="/login">
                  <Button className="bg-teal-600 hover:bg-teal-700">Back to Login</Button>
                </Link>
              </div>
            ) : (
              <>
                <p className="text-gray-600 mb-6 text-center text-sm">
                  Enter your email address and we'll send you a link to reset your password.
                </p>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="mt-1"
                    />
                  </div>

                  <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700" disabled={loading}>
                    {loading ? "Sending..." : "Send Reset Link"}
                  </Button>
                </form>

                <div className="mt-6 text-center text-sm">
                  <Link to="/login" className="text-teal-600 hover:text-teal-700">
                    Back to Login
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
