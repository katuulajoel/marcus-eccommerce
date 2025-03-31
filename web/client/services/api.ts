import axios from "axios";
import { API_BASE_URL } from "@shared/utils/env";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Fetch the best-selling product
export const fetchBestSellingProduct = async () => {
  const response = await apiClient.get("/api/products/best-selling");
  return response.data;
};

// Fetch a few products per category
export const fetchProductsByCategory = async (category: string, limit: number = 3) => {
  const response = await apiClient.get(`/api/categories/${category}/products`, {
    params: { limit },
  });
  return response.data;
};

// Fetch all products
export const fetchAllProducts = async () => {
    const response = await apiClient.get("/api/products/");
      return response.data;
};
