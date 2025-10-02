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
  image?: File;
  description?: string;
}

export interface PartOptionUpdateInput {
  name?: string;
  part?: number;
  default_price?: number;
  minimum_payment_percentage?: number;
  image?: File | null;
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
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('part', String(data.part));
    formData.append('default_price', String(data.default_price));
    if (data.minimum_payment_percentage !== undefined) {
      formData.append('minimum_payment_percentage', String(data.minimum_payment_percentage));
    }
    if (data.image) {
      formData.append('image', data.image);
    }
    if (data.description) {
      formData.append('description', data.description);
    }

    const response = await adminApiClient.post<PartOption>('/api/part-options/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Update existing part option
   */
  update: async (id: number, data: PartOptionUpdateInput): Promise<PartOption> => {
    const formData = new FormData();
    if (data.name !== undefined) {
      formData.append('name', data.name);
    }
    if (data.part !== undefined) {
      formData.append('part', String(data.part));
    }
    if (data.default_price !== undefined) {
      formData.append('default_price', String(data.default_price));
    }
    if (data.minimum_payment_percentage !== undefined) {
      formData.append('minimum_payment_percentage', String(data.minimum_payment_percentage));
    }
    if (data.image !== undefined) {
      if (data.image === null) {
        formData.append('image', '');
      } else {
        formData.append('image', data.image);
      }
    }
    if (data.description !== undefined) {
      formData.append('description', data.description);
    }

    const response = await adminApiClient.patch<PartOption>(`/api/part-options/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Delete part option
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/part-options/${id}/`);
  },
};
