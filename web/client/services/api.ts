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
