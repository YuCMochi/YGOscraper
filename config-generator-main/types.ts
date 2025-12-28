export interface GlobalSettings {
  default_shipping_cost: number;
  global_exclude_keywords: string[];
  global_exclude_seller: string[];
}

export interface CartItemData {
  card_name_zh: string;
  required_amount: number;
  target_ids: string[];
}

// Internal interface extending CartItemData with a unique ID for React rendering
export interface CartItemInternal extends CartItemData {
  id: string;
}

export interface OutputJson {
  global_settings: GlobalSettings;
  shopping_cart: CartItemData[];
}