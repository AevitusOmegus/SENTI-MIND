import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
});

export async function analyzeText(text) {
  const { data } = await api.post("/analysis/", { text });
  return data;
}

export default api;
