/**
 * Price Adjustment Rule service for admin CRUD operations
 */

import { adminApiClient } from './api-client';

export interface PriceAdjustmentRule {
  id: number;
  condition_option: number;
  condition_option_name?: string;
  affected_option: number;
  affected_option_name?: string;
  adjusted_price: number;
}

export interface PriceAdjustmentRuleCreateInput {
  condition_option: number;
  affected_option: number;
  adjusted_price: number;
}

export interface PriceAdjustmentRuleUpdateInput {
  condition_option?: number;
  affected_option?: number;
  adjusted_price?: number;
}

/**
 * Price Adjustment Rule service for admin operations
 */
export const priceRuleService = {
  /**
   * Get all price adjustment rules
   */
  getAll: async (): Promise<PriceAdjustmentRule[]> => {
    const response = await adminApiClient.get<PriceAdjustmentRule[]>('/api/configurator/price-adjustments/');
    return response.data;
  },

  /**
   * Get single price adjustment rule by ID
   */
  getById: async (id: number): Promise<PriceAdjustmentRule> => {
    const response = await adminApiClient.get<PriceAdjustmentRule>(`/api/configurator/price-adjustments/${id}/`);
    return response.data;
  },

  /**
   * Create new price adjustment rule
   */
  create: async (data: PriceAdjustmentRuleCreateInput): Promise<PriceAdjustmentRule> => {
    const response = await adminApiClient.post<PriceAdjustmentRule>('/api/configurator/price-adjustments/', data);
    return response.data;
  },

  /**
   * Update existing price adjustment rule
   */
  update: async (id: number, data: PriceAdjustmentRuleUpdateInput): Promise<PriceAdjustmentRule> => {
    const response = await adminApiClient.patch<PriceAdjustmentRule>(`/api/configurator/price-adjustments/${id}/`, data);
    return response.data;
  },

  /**
   * Delete price adjustment rule
   */
  delete: async (id: number): Promise<void> => {
    await adminApiClient.delete(`/api/configurator/price-adjustments/${id}/`);
  },
};
