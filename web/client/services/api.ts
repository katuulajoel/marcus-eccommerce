import axios from "axios";
import { API_BASE_URL } from "@shared/utils/env";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Legacy alias for backward compatibility
const apiClient = api;

// Fetch the best-selling product
export const fetchBestSellingProduct = async () => {
  const response = await apiClient.get("/api/preconfigured-products/best-selling/");
  return response.data;
};

// Fetch a few products per category
export const fetchProductsByCategory = async (categoryId: number) => {
  const response = await apiClient.get(`/api/preconfigured-products/products-by-category/${categoryId}/`);
  return response.data;
};

// Fetch all products
export const fetchAllProducts = async () => {
  const response = await apiClient.get("/api/products/");
  return response.data;
};

// Fetch top products
export const fetchTopProducts = async () => {
  const response = await apiClient.get("/api/preconfigured-products/top-products/");
  return response.data;
};

// Fetch all categories
export const fetchCategories = async () => {
  const response = await apiClient.get("/api/categories/");
  return response.data;
};

// Fetch all parts with their options for a category
export const fetchPartsWithOptions = async (categoryId: number) => {
  try {
    // Use the direct endpoint that returns parts with nested options
    const response = await apiClient.get(`/api/categories/${categoryId}/parts/`);
    return response.data;
  } catch (error) {
    console.error("Error fetching parts with options:", error);
    throw error;
  }
};

// Fetch all incompatibility rules
export const fetchIncompatibilityRules = async () => {
  const response = await apiClient.get("/api/configurator/incompatibilities/");
  return response.data;
};

// Fetch all price adjustment rules
export const fetchPriceAdjustmentRules = async () => {
  const response = await apiClient.get("/api/configurator/price-adjustments/");
  return response.data;
};

// Fetch stock information for a specific category
export const fetchCategoryStock = async (categoryId: number) => {
    const response = await apiClient.get(`/api/categories/${categoryId}/stock/`);
    return response.data;
};

// Fetch product details by ID
export const fetchProductById = async (productId: number) => {
    const response = await apiClient.get(`/api/preconfigured-products/products/${productId}/`);
    return response.data;
};

// AI Assistant API endpoints
export const sendAIChatMessage = async (sessionId: string, message: string, context?: any) => {
    // AI chat can take longer due to agent reasoning and tool calls, so use a longer timeout
    const response = await apiClient.post("/api/ai-assistant/chat/", {
        session_id: sessionId,
        message,
        context
    }, {
        timeout: 60000 // 60 seconds timeout for AI chat
    });
    return response.data;
};

export const getAIChatSession = async (sessionId: string) => {
    const response = await apiClient.get(`/api/ai-assistant/session/${sessionId}/`);
    return response.data;
};

export const clearAIChatSession = async (sessionId: string) => {
    const response = await apiClient.delete(`/api/ai-assistant/session/${sessionId}/clear/`);
    return response.data;
};

// ============================================================================
// CART API - Redis-based shopping cart
// ============================================================================

export const addToCart = async (
    sessionId: string,
    productId: number,
    name: string,
    price: number,
    quantity: number = 1,
    configuration?: any,
    imageUrl?: string,
    categoryId?: number,
    configDetails?: any
) => {
    const response = await apiClient.post('/api/ai-assistant/cart/add/', {
        session_id: sessionId,
        product_id: productId,
        name,
        price,
        quantity,
        configuration,
        image_url: imageUrl,
        category_id: categoryId,
        config_details: configDetails
    });
    return response.data;
};

export const getCart = async (sessionId: string) => {
    const response = await apiClient.get(`/api/ai-assistant/cart/${sessionId}/`);
    return response.data;
};

export const removeFromCart = async (sessionId: string, itemId: string) => {
    const response = await apiClient.post('/api/ai-assistant/cart/remove/', {
        session_id: sessionId,
        item_id: itemId
    });
    return response.data;
};

export const updateCartQuantity = async (sessionId: string, itemId: string, quantity: number) => {
    const response = await apiClient.post('/api/ai-assistant/cart/update-quantity/', {
        session_id: sessionId,
        item_id: itemId,
        quantity
    });
    return response.data;
};

export const clearCart = async (sessionId: string) => {
    const response = await apiClient.post('/api/ai-assistant/cart/clear/', {
        session_id: sessionId
    });
    return response.data;
};