/**
 * Preconfigured Product service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface PartOptionDetails {
  id: number;
  name: string;
  part: number;
  part_name?: string;
  default_price: string;
  image_url?: string;
  description?: string;
}

export interface PreconfiguredProductPart {
  id: number;
  preconfigured_product: number;
  part_option: number;
  part_option_details?: PartOptionDetails;
}

export interface CategoryDetails {
  id: number;
  name: string;
  description?: string;
}

export interface PreconfiguredProduct {
  id: number;
  name: string;
  category: number;
  category_details?: CategoryDetails;
  base_price: string;
  image_url?: string;
  description?: string;
  parts?: PreconfiguredProductPart[];
}

export interface PreconfiguredProductCreateInput {
  name: string;
  category: number;
  base_price: number | string;
  image_url?: string;
  description?: string;
  part_options?: number[]; // Array of part option IDs
}

export interface PreconfiguredProductUpdateInput {
  name?: string;
  category?: number;
  base_price?: number | string;
  image_url?: string;
  description?: string;
}

/**
 * Preconfigured Product service for admin operations
 */
export const preconfiguredProductService = {
  /**
   * Get all preconfigured products (optionally filtered by category)
   */
  getAll: async (categoryId?: number): Promise<PreconfiguredProduct[]> => {
    const params = categoryId ? { category_id: categoryId } : {};
    const response = await adminApiClient.get<PreconfiguredProduct[]>('/api/preconfigured-products/products/', { params });
    return response.data;
  },

  /**
   * Get single preconfigured product by ID
   */
  getById: async (id: number): Promise<PreconfiguredProduct> => {
    const response = await adminApiClient.get<PreconfiguredProduct>(`/api/preconfigured-products/products/${id}/`);
    return response.data;
  },

  /**
   * Create new preconfigured product
   */
  create: async (data: PreconfiguredProductCreateInput): Promise<PreconfiguredProduct> => {
    const response = await adminApiClient.post<PreconfiguredProduct>('/api/preconfigured-products/products/', data);
    return response.data;
  },

  /**
   * Create preconfigured product with parts in one transaction
   */
  createWithParts: async (
    name: string,
    category: number,
    basePrice: number,
    partOptionIds: number[],
    imageUrl?: string,
    description?: string
  ): Promise<PreconfiguredProduct> => {
    const productData: PreconfiguredProductCreateInput = {
      name,
      category,
      base_price: basePrice.toFixed(2),
      image_url: imageUrl,
      description,
      part_options: partOptionIds,
    };

    const response = await adminApiClient.post<PreconfiguredProduct>('/api/preconfigured-products/products/', productData);
    return response.data;
  },

  /**
   * Update existing preconfigured product
   */
  update: async (id: number, data: PreconfiguredProductUpdateInput): Promise<PreconfiguredProduct> => {
    const response = await adminApiClient.patch<PreconfiguredProduct>(`/api/preconfigured-products/products/${id}/`, data);
    return response.data;
  },

  /**
   * Delete preconfigured product
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/preconfigured-products/products/${id}/`);
  },

  /**
   * Get parts for a specific preconfigured product
   */
  getParts: async (productId: number): Promise<PreconfiguredProductPart[]> => {
    const response = await adminApiClient.get<PreconfiguredProductPart[]>(`/api/preconfigured-products/products/${productId}/parts/`);
    return response.data;
  },
};
