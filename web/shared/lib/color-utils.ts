type ColorClasses = {
  base: string
  hover: string
  text: string
}

export function getColorClasses(colorScheme: string): ColorClasses {
  // Default to purple if the color scheme is not found
  const defaultColors: ColorClasses = {
    base: "bg-purple-100",
    hover: "hover:bg-purple-200",
    text: "text-purple-800",
  }

  const colorMap: Record<string, ColorClasses> = {
    purple: {
      base: "bg-purple-100",
      hover: "hover:bg-purple-200",
      text: "text-purple-800",
    },
    green: {
      base: "bg-green-100",
      hover: "hover:bg-green-200",
      text: "text-green-800",
    },
    pink: {
      base: "bg-pink-100",
      hover: "hover:bg-pink-200",
      text: "text-pink-800",
    },
    yellow: {
      base: "bg-yellow-100",
      hover: "hover:bg-yellow-200",
      text: "text-yellow-800",
    },
    blue: {
      base: "bg-blue-100",
      hover: "hover:bg-blue-200",
      text: "text-blue-800",
    },
    orange: {
      base: "bg-orange-100",
      hover: "hover:bg-orange-200",
      text: "text-orange-800",
    },
    teal: {
      base: "bg-teal-100",
      hover: "hover:bg-teal-200",
      text: "text-teal-800",
    },
  }

  return colorMap[colorScheme] || defaultColors
}
