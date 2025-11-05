import { useState, useEffect } from "react"
import { fetchIncompatibilityRules, fetchPriceAdjustmentRules } from "@client/services/api"
import { useConvertedPrice } from "@shared/hooks/use-converted-price"

export function useProductRules(configuration: { [key: string]: string }, parts: any[]) {
  // Incompatibility rules
  const [incompatibilityRules, setIncompatibilityRules] = useState<any[]>([])
  const [incompatibilityMessages, setIncompatibilityMessages] = useState<{ [key: string]: string }>({})
  
  // Price adjustment rules
  const [priceAdjustmentRules, setPriceAdjustmentRules] = useState<any[]>([])
  const [adjustedPrices, setAdjustedPrices] = useState<{ [key: number]: number }>({})
  const [totalPrice, setTotalPrice] = useState(0)

  // Fetch compatibility rules
  useEffect(() => {
    const getIncompatibilityRules = async () => {
      try {
        const rulesData = await fetchIncompatibilityRules()
        setIncompatibilityRules(rulesData)
      } catch (err) {
        console.error("Failed to fetch incompatibility rules:", err)
      }
    }

    getIncompatibilityRules()
  }, [])

  // Fetch price adjustment rules
  useEffect(() => {
    const getPriceAdjustmentRules = async () => {
      try {
        const rulesData = await fetchPriceAdjustmentRules()
        setPriceAdjustmentRules(rulesData)
      } catch (err) {
        console.error("Failed to fetch price adjustment rules:", err)
      }
    }

    getPriceAdjustmentRules()
  }, [])

  // Calculate incompatibility messages based on current configuration
  useEffect(() => {
    if (incompatibilityRules.length === 0 || parts.length === 0) return;

    const newIncompatibilityMessages: { [key: string]: string } = {};

    // For each part and its options
    parts.forEach((part) => {
      if (!part.options) return;

      // Check each option against the current configuration
      part.options.forEach((option) => {
        const optionId = option.id.toString();

        // Check this option against all selected options in the configuration
        Object.entries(configuration).forEach(([configPartName, selectedOptionId]) => {
          if (!selectedOptionId) return;
          if (part.name === configPartName && optionId === selectedOptionId) return; // Skip checking against self

          // Find the part for this configuration item
          const configPart = parts.find((p) => p.name === configPartName);
          if (!configPart) return;

          // Find the selected option
          const selectedOption = configPart.options.find(
            (opt) => opt.id.toString() === selectedOptionId,
          );
          if (!selectedOption) return;

          // Check for incompatibilities between these two options
          for (const rule of incompatibilityRules) {
            const isThisOptionInRule =
              rule.part_option === option.id || rule.incompatible_with_option === option.id;
            const isSelectedOptionInRule =
              rule.part_option === selectedOption.id ||
              rule.incompatible_with_option === selectedOption.id;

            if (isThisOptionInRule && isSelectedOptionInRule) {
              newIncompatibilityMessages[`${part.name}-${optionId}`] = rule.message;
            }
          }
        });
      });
    });

    setIncompatibilityMessages(newIncompatibilityMessages);
  }, [configuration, incompatibilityRules, parts]);

  // Calculate price adjustments based on current configuration
  useEffect(() => {
    if (priceAdjustmentRules.length === 0 || parts.length === 0) return
    
    const newAdjustedPrices: { [key: number]: number } = {}
    
    // Convert configuration values to numbers for comparison
    const selectedOptionIds = Object.values(configuration).map(id => parseInt(id, 10))
    
    // Check each rule
    priceAdjustmentRules.forEach(rule => {
      const conditionOptionId = rule.condition_option
      const affectedOptionId = rule.affected_option
      
      // If the condition option is selected
      if (selectedOptionIds.includes(conditionOptionId)) {
        // Find the affected option to get its base price
        let affectedOption = null;
        parts.forEach(part => {
          const foundOption = part.options?.find(opt => opt.id === affectedOptionId);
          if (foundOption) {
            affectedOption = foundOption;
          }
        });
        
        if (affectedOption) {
          // Store the adjusted price value from the rule
          newAdjustedPrices[affectedOptionId] = parseFloat(rule.adjusted_price);
        }
      }
    })
    
    setAdjustedPrices(newAdjustedPrices)
  }, [configuration, priceAdjustmentRules, parts])

  // Calculate total price based on configuration and price adjustments
  useEffect(() => {
    if (Object.keys(configuration).length === 0) return

    let price = 0

    // Add the price of each selected option, considering adjustments
    Object.entries(configuration).forEach(([partName, optionId]) => {
      const part = parts.find((p) => p.name === partName)
      if (!part) return

      const option = part.options.find((opt) => opt.id.toString() === optionId)
      if (option) {
        const optionIdNum = option.id
        const basePrice = parseFloat(option.default_price)
        const adjustment = adjustedPrices[optionIdNum]
        
        // If there's an adjustment, add it to the base price
        if (adjustment !== undefined) {
          price += basePrice + adjustment
        } else {
          price += basePrice
        }
      }
    })

    setTotalPrice(price)
  }, [configuration, parts, adjustedPrices])

  // Check if an option is compatible with current configuration
  const isCompatible = (partName: string, optionId: string): boolean => {
    // If we don't have incompatibility rules yet, consider everything compatible
    if (incompatibilityRules.length === 0) return true;

    // If this option is already in the current configuration, it's compatible
    if (configuration[partName] === optionId) return true;

    // Check if there's an incompatibility message for this option
    return !incompatibilityMessages[`${partName}-${optionId}`];
  }

  // Get option price with adjustments considered
  const getOptionPrice = (option: any) => {
    const optionIdNum = option.id
    const basePrice = parseFloat(option.default_price)
    const adjustment = adjustedPrices[optionIdNum]
    
    if (adjustment !== undefined) {
      return {
        price: basePrice + adjustment,
        hasAdjustment: true,
        isPositiveAdjustment: adjustment > 0,
        isNeutral: adjustment === 0
      }
    }
    return {
      price: basePrice,
      hasAdjustment: false,
      isPositiveAdjustment: false,
      isNeutral: true
    }
  }

  // Get formatted price display for an option with currency conversion
  const getFormattedPriceDisplay = (option: any) => {
    const priceInfo = getOptionPrice(option)
    const basePrice = parseFloat(option.default_price)
    
    if (priceInfo.price <= 0) {
      return { 
        display: "Included", 
        color: "default",
        basePrice: null,
        adjustedPrice: null
      }
    }
    
    // Format both base and adjusted prices
    const { formattedPrice: formattedBasePrice } = useConvertedPrice({ amount: basePrice })
    const { formattedPrice: formattedAdjustedPrice, isConverting } = useConvertedPrice({ amount: priceInfo.price })
    
    if (isConverting) {
      return { 
        display: "Loading...", 
        color: "default",
        basePrice: null,
        adjustedPrice: null
      }
    }
    
    // Determine if we need to show adjustment
    const showAdjustment = priceInfo.hasAdjustment && !priceInfo.isNeutral
    
    return { 
      display: formattedAdjustedPrice,
      displayBasePrice: showAdjustment ? formattedBasePrice : null,
      color: showAdjustment 
        ? priceInfo.isPositiveAdjustment 
          ? 'positive' 
          : 'negative'
        : 'default',
      isPositiveAdjustment: priceInfo.isPositiveAdjustment,
      showAdjustment
    }
  }

  // Get price details for the configuration summary
  const getConfigDetails = () => {
    const details: { [key: string]: { name: string; price: number } } = {}

    Object.entries(configuration).forEach(([partName, optionId]) => {
      const part = parts.find((p) => p.name === partName)
      if (!part) return

      const option = part.options.find((opt) => opt.id.toString() === optionId)
      if (option) {
        const priceInfo = getOptionPrice(option)
        details[partName] = {
          name: option.name,
          price: priceInfo.price,
        }
      }
    })

    return details
  }

  return {
    incompatibilityRules,
    incompatibilityMessages,
    priceAdjustmentRules,
    adjustedPrices,
    totalPrice,
    isCompatible,
    getOptionPrice,
    getFormattedPriceDisplay,
    getConfigDetails,
  }
}
