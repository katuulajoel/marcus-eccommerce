import { axiosInstance } from "@client/context/auth-context"

export interface CartItem {
  category_id: number
  quantity: number
}

export interface ShippingZone {
  id: number
  zone_code: string
  zone_name: string
  distance_range_min_km: number
  distance_range_max_km: number
  standard_delivery_days: number
  express_delivery_days: number
  is_active: boolean
}

export interface ZoneArea {
  id: number
  area_name: string
  is_landmark: boolean
  keywords: string[]
}

export interface ShippingOption {
  rate_id: number
  delivery_method: string
  delivery_method_display: string
  service_level: string
  service_level_display: string
  base_cost_ugx: number
  helper_fee_ugx: number
  extra_care_fee_ugx: number
  total_cost_ugx: number
  delivery_time: string
  estimated_delivery_date: string
  total_weight_kg: number
  total_volume_m3: number
  requires_helper: boolean
  requires_extra_care: boolean
  reasons: string[]
}

export interface CalculateShippingResponse {
  zone: {
    id: number
    zone_code: string
    zone_name: string
  }
  shipping_options: ShippingOption[]
}

export interface ZoneSuggestion {
  area_name: string
  zone_id: number
  zone_code: string
  zone_name: string
  is_landmark: boolean
}

/**
 * Calculate shipping options for a cart
 */
export async function calculateShipping(
  cartItems: CartItem[],
  zoneId: number
): Promise<CalculateShippingResponse> {
  const response = await axiosInstance.post("/shipping/calculator/calculate/", {
    cart_items: cartItems,
    zone_id: zoneId,
  })
  return response.data
}

/**
 * Get all shipping zones
 */
export async function getShippingZones(): Promise<ShippingZone[]> {
  const response = await axiosInstance.get("/shipping/zones/")
  return response.data
}

/**
 * Get a specific shipping zone with areas
 */
export async function getShippingZone(zoneId: number): Promise<ShippingZone & { areas: ZoneArea[] }> {
  const response = await axiosInstance.get(`/shipping/zones/${zoneId}/`)
  return response.data
}

/**
 * Match an address to a shipping zone
 */
export async function matchAddressToZone(
  address: string,
  city?: string
): Promise<{ matched: boolean; zone?: ShippingZone; message?: string }> {
  const response = await axiosInstance.post("/shipping/zones/match/", {
    address,
    city,
  })
  return response.data
}

/**
 * Get zone area suggestions for autocomplete
 */
export async function getZoneSuggestions(query: string): Promise<{ suggestions: ZoneSuggestion[] }> {
  const response = await axiosInstance.get(`/shipping/zones/suggest/?q=${encodeURIComponent(query)}`)
  return response.data
}
