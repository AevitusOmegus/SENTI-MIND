import axios from "axios";
import { supabase } from "../lib/supabaseClient";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT from active Supabase session if available
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers["Authorization"] = `Bearer ${session.access_token}`;
  }
  return config;
});

export async function analyzeText(text) {
  const { data } = await api.post("/analysis/", { text });
  return data;
}

export default api;
