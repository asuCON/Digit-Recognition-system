/**
 * API client for MNIST Digit Recognition backend (PHP + mysqli)
 */
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export interface PredictResponse {
  digit: number;
  confidence: number;
  probabilities: number[];
  label: string;
  id?: number;
}

export interface EvaluateResponse {
  accuracy: number;
  confusion_matrix: number[][];
  classification_report: Record<string, unknown>;
  precision?: string;
  recall?: string;
  f1_score?: string;
}

export interface Sample {
  image_base64: string;
  label: number;
}

export interface TrainResponse {
  message: string;
  test_accuracy: number;
  test_loss: number;
}

export const predictFromBase64 = async (imageBase64: string): Promise<PredictResponse> => {
  const { data } = await api.post<PredictResponse>("/predict/base64", { image: imageBase64 });
  return data;
};

export const getSamples = async (count = 12, digit?: number): Promise<{ samples: Sample[] }> => {
  const params = new URLSearchParams({ count: String(count) });
  if (digit != null) params.set("digit", String(digit));
  const { data } = await api.get<{ samples: Sample[] }>(`/samples?${params}`);
  return data;
};

export const getEvaluate = async (): Promise<EvaluateResponse> => {
  const { data } = await api.get<EvaluateResponse>("/evaluate");
  return data;
};

export const getTrainProgress = async (): Promise<{
  status: string;
  message?: string;
  current_epoch?: number;
  total_epochs?: number;
  loss?: number;
  acc?: number;
  val_loss?: number;
  val_acc?: number;
  test_accuracy?: number;
  test_loss?: number;
  error?: string;
}> => {
  const { data } = await api.get("/train/progress");
  return data;
};

export const trainModel = async (params: {
  model_type?: string;
  epochs?: number;
  batch_size?: number;
}): Promise<TrainResponse> => {
  const { data } = await api.post<TrainResponse>("/train", {
    model_type: params.model_type ?? "advanced",
    epochs: params.epochs ?? 15,
    batch_size: params.batch_size ?? 128,
  });
  return data;
};

export const getHealth = async (): Promise<{ status: string; model_loaded: boolean }> => {
  const { data } = await api.get("/health");
  return data;
};

export const getModelStatus = async (): Promise<{ loaded: boolean; path: string }> => {
  const { data } = await api.get("/model/status");
  return data;
};

export const getPredictions = async (): Promise<{
  count: number;
  results: Array<{ id: number; digit: number; confidence: number; source: string; created_at: string }>;
}> => {
  const { data } = await api.get("/predictions");
  return data;
};

export const getTrainingRuns = async (): Promise<{
  results: Array<{
    id: number;
    model_type: string;
    epochs: number;
    batch_size: number;
    test_accuracy: number;
    test_loss: number;
    created_at: string;
  }>;
}> => {
  const { data } = await api.get("/training-runs");
  return data;
};

export default api;
