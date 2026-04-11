import api from "./analysisService";

export const saveJournalEntry = (data) => api.post("/journal/", data).then(r => r.data);
export const listJournalEntries = (limit = 20, offset = 0) =>
  api.get(`/journal/?limit=${limit}&offset=${offset}`).then(r => r.data);
export const getJournalEntry = (id) => api.get(`/journal/${id}`).then(r => r.data);
export const deleteJournalEntry = (id) => api.delete(`/journal/${id}`);

export const saveGratitude = (text, source_entry_id = null) =>
  api.post("/journal/gratitude/", { text, source_entry_id }).then(r => r.data);
export const listGratitude = () => api.get("/journal/gratitude/").then(r => r.data);
export const deleteGratitude = (id) => api.delete(`/journal/gratitude/${id}`);
