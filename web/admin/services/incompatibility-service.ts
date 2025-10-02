/**
 * Incompatibility Rule service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface IncompatibilityRule {
  id: number;
  part_option: number;
  option_a_name?: string;
  incompatible_with_option: number;
  option_b_name?: string;
  message: string;
}

export interface IncompatibilityRuleCreateInput {
  part_option: number;
  incompatible_with_option: number;
  message: string;
}

export interface IncompatibilityRuleUpdateInput {
  part_option?: number;
  incompatible_with_option?: number;
  message?: string;
}

/**
 * Incompatibility Rule service for admin operations
 */
export const incompatibilityService = {
  /**
   * Get all incompatibility rules
   */
  getAll: async (): Promise<IncompatibilityRule[]> => {
    const response = await adminApiClient.get<IncompatibilityRule[]>('/api/configurator/incompatibilities/');
    return response.data;
  },

  /**
   * Get single incompatibility rule by ID
   */
  getById: async (id: number): Promise<IncompatibilityRule> => {
    const response = await adminApiClient.get<IncompatibilityRule>(`/api/configurator/incompatibilities/${id}/`);
    return response.data;
  },

  /**
   * Create new incompatibility rule
   */
  create: async (data: IncompatibilityRuleCreateInput): Promise<IncompatibilityRule> => {
    const response = await adminApiClient.post<IncompatibilityRule>('/api/configurator/incompatibilities/', data);
    return response.data;
  },

  /**
   * Update existing incompatibility rule
   */
  update: async (id: number, data: IncompatibilityRuleUpdateInput): Promise<IncompatibilityRule> => {
    const response = await adminApiClient.patch<IncompatibilityRule>(`/api/configurator/incompatibilities/${id}/`, data);
    return response.data;
  },

  /**
   * Delete incompatibility rule
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/configurator/incompatibilities/${id}/`);
  },
};
