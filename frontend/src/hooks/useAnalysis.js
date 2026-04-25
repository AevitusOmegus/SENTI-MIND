import { useState, useCallback } from "react";
import { analyzeText } from "../services/analysisService";

export function useAnalysis() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (text) => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeText(text);
      setResult(data);
      return data;
    } catch (err) {
      // err.response exists for HTTP errors (4xx/5xx from server)
      // err.response is undefined for network failures (timeout, ECONNREFUSED)
      const detail =
        err?.response?.data?.detail ??
        (err?.code === "ECONNABORTED" ? "Request timed out. Please try again." :
        err?.message?.includes("Network Error") ? "Cannot reach server. Check your connection." :
        "An unexpected error occurred.");
      setError(detail);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, analyze, reset };
}
