import api from "./analysisService";

export const chatService = {
  async sendMessage(message, history = []) {
    const { data } = await api.post("/chat/", { message, history });
    return data;
  }
};
