// Mirrors the backend `FinalResponse` / `TravelSummary` schemas (the parts the
// UI consumes). Kept loose where the backend allows nulls.

export interface FlightOffer {
  airline: string;
  flight_number: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  stops: number;
  total_price: number;
  currency: string;
  within_budget?: boolean | null;
}

export interface BudgetEstimate {
  currency: string;
  total_cost: number;
  user_budget?: number | null;
  within_budget?: boolean | null;
  summary: string;
}

export interface TravelSummary {
  destination?: string | null;
  source?: string | null;
  travelers: number;
  num_days: number;
  currency: string;
  flight?: FlightOffer | null;
  hotel?: { name: string; total_price: number; currency: string } | null;
  budget?: BudgetEstimate | null;
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
