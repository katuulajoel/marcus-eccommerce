/**
 * Part Option service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface PartOption {
  id: number;
  name: string;
  part: number;
  part_name?: string;
  default_price: number;
  minimum_payment_percentage?: number;
  image_url?: string;
  description?: string;
}

export interface PartOptionCreateInput {
  name: string;
  part: number;
  default_price: number;
  minimum_payment_percentage?: number;
  image_url?: string;
  description?: string;
}

export interface PartOptionUpdateInput {
  name?: string;
  part?: number;
  default_price?: number;
  minimum_payment_percentage?: number;
  image_url?: string;
  description?: string;
}

/**
 * Part Option service for admin operations
 */
export const partOptionService = {
  /**
   * Get all part options (optionally filtered by part)
   */
  getAll: async (partId?: number): Promise<PartOption[]> => {
    const params = partId ? { part_id: partId } : {};
    const response = await adminApiClient.get<PartOption[]>('/api/part-options/', { params });
    return response.data;
  },

  /**
   * Get single part option by ID
   */
  getById: async (id: number): Promise<PartOption> => {
    const response = await adminApiClient.get<PartOption>(`/api/part-options/${id}/`);
    return response.data;
  },

  /**
   * Create new part option
   */
  create: async (data: PartOptionCreateInput): Promise<PartOption> => {
    const response = await adminApiClient.post<PartOption>('/api/part-options/', data);
    return response.data;
  },

  /**
   * Update existing part option
   */
  update: async (id: number, data: PartOptionUpdateInput): Promise<PartOption> => {
    const response = await adminApiClient.patch<PartOption>(`/api/part-options/${id}/`, data);
    return response.data;
  },

  /**
   * Delete part option
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/part-options/${id}/`);
  },
};
