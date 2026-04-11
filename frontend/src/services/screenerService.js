import api from "./analysisService";

export const submitScreener = (gad2_answers, phq2_answers) =>
  api.post("/screener/", { gad2_answers, phq2_answers }).then(r => r.data);
export const getScreenerHistory = () => api.get("/screener/history").then(r => r.data);
