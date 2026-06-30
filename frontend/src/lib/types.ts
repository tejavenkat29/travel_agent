// Mirrors the backend `FinalResponse` / `TravelSummary` schemas (the parts the
// UI consumes). Kept loose where the backend allows nulls.

export interface FareClass {
  name: string;
  price_per_person: number;
}

export interface TransportOption {
  mode: "flight" | "train" | "bus";
  available: boolean;
  provider?: string | null;
  price_per_person?: number | null;
  total_price?: number | null;
  currency: string;
  duration_hours?: number | null;
  fare_classes: FareClass[];
  booking_apps: string[];
  note?: string | null;
}

export interface TransportComparison {
  origin: string;
  destination: string;
  travelers: number;
  currency: string;
  options: TransportOption[];
  recommended?: TransportOption | null;
  advisory: string;
  disclaimer: string;
}

export interface HotelInfo {
  name: string;
  area?: string | null;
  rating?: number | null;
  nightly_rate: number;
  nights: number;
  total_price: number;
  currency: string;
}

export interface WeatherAdvisory {
  forecast: {
    condition: string;
    temp_high_c: number;
    temp_low_c: number;
  };
  clothing_suggestions: string[];
  best_seasons: string[];
  best_time_to_visit: string;
}

export interface CostLineItem {
  category: string;
  amount: number;
  detail: string;
  estimated: boolean;
}

export interface BudgetEstimate {
  currency: string;
  total_cost: number;
  user_budget?: number | null;
  within_budget?: boolean | null;
  difference?: number | null;
  summary: string;
  breakdown: { line_items: CostLineItem[] };
}

export interface DayPlan {
  day: number;
  title: string;
  activities: string[];
}

export interface TravelSummary {
  destination?: string | null;
  source?: string | null;
  travelers: number;
  num_days: number;
  currency: string;
  transport?: TransportComparison | null;
  hotel?: HotelInfo | null;
  hotel_options: HotelInfo[];
  weather?: WeatherAdvisory | null;
  budget?: BudgetEstimate | null;
  recommendations: string[];
  daily_itinerary: DayPlan[];
}

export interface FinalResponse {
  summary: TravelSummary;
  natural_language: string;
}

export interface ApiError {
  error: string;
  message: string;
  request_id?: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string; // markdown for assistant, plain for user
  error?: boolean;
  summary?: TravelSummary; // structured plan → rendered as rich cards
}

/** A user-created folder ("Trip") that groups conversations. */
export interface Folder {
  id: string;
  name: string;
}

/** A saved conversation (chat thread), optionally filed under a folder. */
export interface Conversation {
  id: string;
  title: string;
  folderId: string | null;
  createdAt: number;
  updatedAt: number;
  messages: ChatMessage[];
}
