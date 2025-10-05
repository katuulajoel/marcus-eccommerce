"use client"

import { useState, FormEvent } from "react"
import {
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js"
import { Button } from "@shared/components/ui/button"

interface StripePaymentFormProps {
  onSuccess: (paymentIntentId: string) => void
  onError: (error: string) => void
  totalAmount: number
}

export default function StripePaymentForm({
  onSuccess,
  onError,
  totalAmount,
}: StripePaymentFormProps) {
  const stripe = useStripe()
  const elements = useElements()
  const [isProcessing, setIsProcessing] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setIsProcessing(true)

    try {
      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/orders`,
        },
        redirect: "if_required",
      })

      if (error) {
        onError(error.message || "Payment failed")
      } else if (paymentIntent && paymentIntent.status === "succeeded") {
        onSuccess(paymentIntent.id)
      } else {
        onError("Payment was not successful")
      }
    } catch (err: any) {
      onError(err.message || "An unexpected error occurred")
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <PaymentElement />

      <div className="pt-4">
        <Button
          type="submit"
          disabled={!stripe || isProcessing}
          className="w-full bg-teal-600 hover:bg-teal-700"
        >
          {isProcessing ? "Processing..." : `Pay $${totalAmount.toLocaleString()}`}
        </Button>
      </div>
    </form>
  )
}
