import { useState, useEffect } from "react"
import { Label } from "@shared/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@shared/components/ui/select"
import { Input } from "@shared/components/ui/input"
import { Button } from "@shared/components/ui/button"
import { MapPin, Loader2 } from "lucide-react"
import { getShippingZones, matchAddressToZone, getZoneSuggestions, ShippingZone, ZoneSuggestion } from "@client/services/shipping-api"

interface ZoneSelectorProps {
  selectedZoneId: number | null
  onZoneSelect: (zoneId: number, zone: ShippingZone) => void
  showAddressMatch?: boolean
}

export default function ZoneSelector({ selectedZoneId, onZoneSelect, showAddressMatch = true }: ZoneSelectorProps) {
  const [zones, setZones] = useState<ShippingZone[]>([])
  const [loading, setLoading] = useState(true)
  const [matchingAddress, setMatchingAddress] = useState(false)
  const [addressInput, setAddressInput] = useState("")
  const [suggestions, setSuggestions] = useState<ZoneSuggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  // Load zones on mount
  useEffect(() => {
    loadZones()
  }, [])

  const loadZones = async () => {
    try {
      const zonesData = await getShippingZones()
      setZones(zonesData)
    } catch (error) {
      console.error("Failed to load shipping zones:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddressMatch = async () => {
    if (!addressInput.trim()) return

    setMatchingAddress(true)
    try {
      const result = await matchAddressToZone(addressInput, "Kampala")

      if (result.matched && result.zone) {
        onZoneSelect(result.zone.id, result.zone)
        setAddressInput("")
        setSuggestions([])
      } else {
        // No match found, show message
        alert("Could not automatically detect your zone. Please select manually from the dropdown.")
      }
    } catch (error) {
      console.error("Address matching error:", error)
      alert("Failed to match address. Please select your zone manually.")
    } finally {
      setMatchingAddress(false)
    }
  }

  const handleAddressInputChange = async (value: string) => {
    setAddressInput(value)

    if (value.length >= 2) {
      try {
        const result = await getZoneSuggestions(value)
        setSuggestions(result.suggestions)
        setShowSuggestions(true)
      } catch (error) {
        console.error("Suggestions error:", error)
      }
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }
  }

  const handleSuggestionClick = (suggestion: ZoneSuggestion) => {
    const zone = zones.find((z) => z.id === suggestion.zone_id)
    if (zone) {
      onZoneSelect(zone.id, zone)
    }
    setAddressInput(suggestion.area_name)
    setShowSuggestions(false)
  }

  const selectedZone = zones.find((z) => z.id === selectedZoneId)

  return (
    <div className="space-y-4">
      {showAddressMatch && (
        <div>
          <Label htmlFor="address-match">Find Your Zone (Enter Area/Landmark)</Label>
          <div className="flex gap-2 relative">
            <div className="flex-1 relative">
              <Input
                id="address-match"
                placeholder="e.g., Ntinda, Kololo, Garden City..."
                value={addressInput}
                onChange={(e) => handleAddressInputChange(e.target.value)}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              />

              {/* Suggestions dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      className="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      <MapPin className={`h-4 w-4 ${suggestion.is_landmark ? "text-teal-600" : "text-gray-400"}`} />
                      <div className="flex-1">
                        <div className="font-medium">{suggestion.area_name}</div>
                        <div className="text-xs text-gray-500">
                          {suggestion.zone_name} ({suggestion.zone_code})
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <Button
              type="button"
              onClick={handleAddressMatch}
              disabled={matchingAddress || !addressInput.trim()}
              variant="outline"
            >
              {matchingAddress ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Matching...
                </>
              ) : (
                <>
                  <MapPin className="h-4 w-4 mr-2" />
                  Find Zone
                </>
              )}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Start typing your area name for suggestions, or select manually below
          </p>
        </div>
      )}

      <div>
        <Label htmlFor="zone-select">Delivery Zone *</Label>
        {loading ? (
          <div className="flex items-center justify-center h-10 border rounded-md">
            <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
          </div>
        ) : (
          <Select
            value={selectedZoneId?.toString() || ""}
            onValueChange={(value) => {
              const zone = zones.find((z) => z.id === parseInt(value))
              if (zone) {
                onZoneSelect(zone.id, zone)
              }
            }}
          >
            <SelectTrigger id="zone-select">
              <SelectValue placeholder="Select your delivery zone" />
            </SelectTrigger>
            <SelectContent>
              {zones.map((zone) => (
                <SelectItem key={zone.id} value={zone.id.toString()}>
                  <div className="flex flex-col">
                    <span className="font-medium">{zone.zone_name}</span>
                    <span className="text-xs text-gray-500">
                      {zone.distance_range_min_km}-{zone.distance_range_max_km}km • {zone.standard_delivery_days}{" "}
                      {zone.standard_delivery_days === 1 ? "day" : "days"}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        {selectedZone && (
          <div className="mt-2 p-3 bg-teal-50 border border-teal-200 rounded-md text-sm">
            <div className="flex items-start gap-2">
              <MapPin className="h-4 w-4 text-teal-600 mt-0.5" />
              <div>
                <p className="font-medium text-teal-900">{selectedZone.zone_name}</p>
                <p className="text-teal-700 text-xs">
                  Distance: {selectedZone.distance_range_min_km}-{selectedZone.distance_range_max_km}km •
                  Standard delivery: {selectedZone.standard_delivery_days} {selectedZone.standard_delivery_days === 1 ? "day" : "days"}
                  {selectedZone.express_delivery_days === 0 ? " • Same-day express available" : ""}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
