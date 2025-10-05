"use client"

import { useState, useEffect } from "react"
import { Link, useNavigate, useLocation, useSearchParams } from "react-router-dom"
import { Button } from "@shared/components/ui/button"
import { Input } from "@shared/components/ui/input"
import { Label } from "@shared/components/ui/label"
import { useAuth } from "@client/context/auth-context"
import { useToast } from "@shared/components/ui/use-toast"
import SiteHeader from "@client/components/site-header"
import Footer from "@client/components/footer"

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { login } = useAuth()
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const from = (location.state as any)?.from?.pathname || "/"

  // Show success message if email was just verified
  useEffect(() => {
    if (searchParams.get('verified') === 'true') {
      toast({
        title: "Email Verified!",
        description: "Your email has been successfully verified. You can now log in.",
        variant: "default",
      })
    }
  }, [searchParams, toast])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      await login(formData.username, formData.password)
      navigate(from, { replace: true })
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.")
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
            <h1 className="text-2xl font-bold mb-6 text-center">Welcome Back</h1>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  className="mt-1"
                />
              </div>

              <div className="flex justify-end">
                <Link to="/forgot-password" className="text-sm text-teal-600 hover:text-teal-700">
                  Forgot password?
                </Link>
              </div>

              <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700" disabled={loading}>
                {loading ? "Logging in..." : "Login"}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-gray-600">Don't have an account? </span>
              <Link to="/register" className="text-teal-600 hover:text-teal-700 font-medium">
                Register here
              </Link>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
