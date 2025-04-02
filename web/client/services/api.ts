import axios from "axios";
import { API_BASE_URL } from "@shared/utils/env";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

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
