import { MousePointerClick, Palette, Gift } from "lucide-react"
import type { CustomizationStep } from "@client/services/mock-data"

interface HowItWorksProps {
  steps: CustomizationStep[]
}

export default function HowItWorks({ steps }: HowItWorksProps) {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case "MousePointerClick":
        return <MousePointerClick className="h-10 w-10 text-purple-600" />
      case "Palette":
        return <Palette className="h-10 w-10 text-pink-600" />
      case "Gift":
        return <Gift className="h-10 w-10 text-yellow-600" />
      default:
        return <Gift className="h-10 w-10 text-pink-600" />
    }
  }

  return (
    <div className="grid md:grid-cols-3 gap-8">
      {steps.map((step, index) => (
        <div key={step.id} className="bg-white rounded-2xl shadow-lg p-8 text-center relative">
          <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 bg-white rounded-full p-4 shadow-md">
            {getIcon(step.icon)}
          </div>
          <div className="mt-8">
            <span className="inline-block bg-pink-100 text-pink-800 text-xs font-medium px-2.5 py-0.5 rounded-full mb-4">
              Step {index + 1}
            </span>
            <h3 className="text-xl font-bold mb-3">{step.title}</h3>
            <p className="text-gray-600">{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
