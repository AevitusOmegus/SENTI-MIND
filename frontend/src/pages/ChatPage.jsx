import { useState, useRef, useEffect } from "react";
import { chatService } from "../services/chatService";
import { listJournalEntries } from "../services/journalService";
import { getMoodTrends } from "../services/moodService";
import { getScreenerHistory } from "../services/screenerService";
import ReactMarkdown from "react-markdown";
import SentiBotAvatar from "../components/SentiBotAvatar";

const QUICK_ACTIONS = [
  { id: "mood", label: "📊 Analyze Mood Trends", action: "mood" },
  { id: "journal", label: "📝 Review Recent Journals", action: "journal" },
  { id: "screener", label: "🩺 Check Screener History", action: "screener" }
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: "model",
      parts: ["Hi there! I'm Senti-Agent. You can ask me for advice, or use the quick buttons below to attach your data to your message so we can review it together."],
    }
  ]);
  const [input, setInput] = useState("");
  const [pendingAttachment, setPendingAttachment] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleQuickAction = (actionType) => {
    // Toggle attachment selection
    if (pendingAttachment === actionType) {
      setPendingAttachment(null);
    } else {
      setPendingAttachment(actionType);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() && !pendingAttachment) return;
    if (isLoading) return;

    let userMessage = input.trim();
    const currentAttachment = pendingAttachment;
    
    setInput("");
    setPendingAttachment(null);
    setIsLoading(true);

    let fetchedDataText = "";
    
    // If the user didn't type anything but has an attachment, use a default prompt
    if (!userMessage) {
      if (currentAttachment === "mood") userMessage = "Please analyze my recent mood trends.";
      else if (currentAttachment === "journal") userMessage = "Please review my recent journal entries.";
      else if (currentAttachment === "screener") userMessage = "Please analyze my recent mental health screener results.";
    }

    // Add user message to UI
    const updatedMessages = [
      ...messages,
      { role: "user", parts: [userMessage] }
    ];
    setMessages(updatedMessages);

    try {
      // Fetch data if attachment exists
      if (currentAttachment === "mood") {
        const data = await getMoodTrends(7);
        fetchedDataText = `Attached Data (Mood Trends): ${JSON.stringify(data)}`;
      } else if (currentAttachment === "journal") {
        const data = await listJournalEntries(5);
        fetchedDataText = `Attached Data (Journal Entries): ${JSON.stringify(data)}`;
      } else if (currentAttachment === "screener") {
        const data = await getScreenerHistory();
        fetchedDataText = `Attached Data (Screener History): ${JSON.stringify(data)}`;
      }

      const hiddenPayload = fetchedDataText ? `${userMessage}\n\n${fetchedDataText}` : userMessage;

      // Pass all messages except the initial system greeting as history.
      // The current user message is sent separately in the `message` field.
      const historyToPass = updatedMessages.slice(1).map(msg => ({
        role: msg.role,
        parts: msg.parts
      }));

      const responseData = await chatService.sendMessage(hiddenPayload, historyToPass);
      
      // Add model response to UI
      setMessages(prev => [
        ...prev,
        { role: "model", parts: [responseData.response] }
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [
        ...prev,
        { role: "model", parts: ["Sorry, I encountered an error fetching data or generating a response. Please try again later."] }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] md:h-[calc(100vh-120px)] bg-white rounded-2xl shadow-sm border border-sage-100 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-sage-100 bg-sage-50/50 flex items-center gap-3">
        <SentiBotAvatar emotion="idle" size="md" animate={true} />
        <div>
          <h2 className="font-semibold text-warm-800">SentiBot</h2>
          <p className="text-xs text-sage-600 font-medium">AI Therapist Companion</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-sage-50/30">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role !== "user" && (
              <div className="flex-shrink-0 mr-2 mt-1">
                <SentiBotAvatar emotion={isLoading && idx === messages.length - 1 ? "loading" : "Normal"} size="sm" animate={true} />
              </div>
            )}
            <div 
              className={`max-w-[80%] md:max-w-[70%] p-3 px-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === "user" 
                  ? "bg-sage-600 text-white rounded-br-sm shadow-md" 
                  : "bg-white text-warm-800 border border-sage-100 shadow-sm rounded-bl-sm"
              }`}
            >
              {msg.role === "user" ? (
                // User messages are simple raw text
                msg.parts[0].split('\n').map((line, i) => (
                  <span key={i}>
                    {line}
                    <br />
                  </span>
                ))
              ) : (
                // Model messages rendered beautifully with Markdown
                <ReactMarkdown
                  components={{
                    strong: ({node, ...props}) => <span className="font-bold text-sage-900" {...props} />,
                    h1: ({node, ...props}) => <h1 className="text-lg font-bold mt-3 mb-1 text-sage-900" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-md font-bold mt-3 mb-1 text-sage-800" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-sm font-bold mt-2 mb-1 text-sage-800" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 my-2 space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal pl-5 my-2 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="pl-1" {...props} />,
                    p: ({node, ...props}) => <p className="mb-3 last:mb-0" {...props} />,
                  }}
                >
                  {msg.parts[0]}
                </ReactMarkdown>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex-shrink-0 mr-2 mt-1">
              <SentiBotAvatar emotion="loading" size="sm" animate={true} />
            </div>
            <div className="bg-white border border-sage-100 shadow-sm rounded-2xl rounded-bl-sm p-4 text-warm-800 text-sm flex gap-1">
              <span className="w-2 h-2 bg-sage-400 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 bg-sage-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions & Input Area */}
      <div className="bg-white border-t border-sage-100">
        {/* Quick Actions Scroller */}
        <div className="flex overflow-x-auto p-3 gap-2 scrollbar-hide border-b border-sage-50/50">
          {QUICK_ACTIONS.map(action => (
            <button
              key={action.id}
              onClick={() => handleQuickAction(action.action)}
              disabled={isLoading}
              className={`flex-shrink-0 px-4 py-1.5 text-xs font-semibold rounded-full border transition-colors disabled:opacity-50 ${
                pendingAttachment === action.action 
                  ? 'bg-sage-600 text-white border-sage-700 shadow-inner' 
                  : 'bg-sage-50 hover:bg-sage-100 text-sage-700 border-sage-200'
              }`}
            >
              {action.label}
            </button>
          ))}
        </div>

        {/* Pending Attachment Indicator */}
        {pendingAttachment && (
          <div className="px-4 pt-3 pb-0 bg-white flex items-center">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-sage-100 text-sage-800 text-xs font-semibold rounded-full border border-sage-200">
              <span className="opacity-70">📎</span>
              {QUICK_ACTIONS.find(a => a.action === pendingAttachment)?.label}
              <button 
                onClick={() => setPendingAttachment(null)}
                className="ml-1 text-sage-500 hover:text-sage-800 focus:outline-none"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Input Form */}
        <div className="p-4 pt-3">
          <form onSubmit={handleSend} className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question or request analysis..."
              className="w-full bg-sage-50/50 border border-sage-200 rounded-full py-3 pl-5 pr-12 text-sm text-warm-800 focus:outline-none focus:border-sage-400 focus:ring-2 focus:ring-sage-100 transition-all placeholder:text-warm-400"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={(!input.trim() && !pendingAttachment) || isLoading}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full bg-sage-600 text-white hover:bg-sage-700 disabled:opacity-50 transition-all"
            >
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                <line x1="22" x2="11" y1="2" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
