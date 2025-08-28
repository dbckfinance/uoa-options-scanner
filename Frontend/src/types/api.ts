// API Types - matching backend Pydantic models

export interface OptionContract {
  contractSymbol: string;
  strike: number;
  type: 'call' | 'put';
  expirationDate: string;
  lastPrice: number;
  volume: number;
  openInterest: number;
  volumeToOiRatio: number;
  premiumSpent: number;
  underlyingPrice: number;
  // Simplified fields for now (backend sends fixed values)
  moneyness?: string;
  distanceFromStrike?: number;
  unusualityLevel?: string;
  daysToExpiration?: number;
  timeDecayRisk?: string;
  strategicSignal?: string;
}

export interface MarketSentiment {
  totalCallVolume: number;
  totalPutVolume: number;
  callPutRatio: number;
  bullishSignals: number;
  bearishSignals: number;
  netSentiment: string;
}

export interface UOAResponse {
  ticker: string;
  analysisDate: string;
  underlyingPrice: number;
  totalContracts: number;
  unusualContracts: OptionContract[];
  // Simplified fields (backend sends basic values for now)
  marketSentiment?: MarketSentiment;
  topSignals?: string[];
  riskWarnings?: string[];
}

export interface ErrorResponse {
  detail: string;
  ticker?: string;
}

