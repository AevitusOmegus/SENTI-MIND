import api from "./analysisService";

export const logMood = (data) => api.post("/mood/", data).then(r => r.data);
export const getMoodHeatmap = () => api.get("/mood/heatmap").then(r => r.data);
export const getMoodTrends = (days = 30) => api.get(`/mood/trends?days=${days}`).then(r => r.data);
