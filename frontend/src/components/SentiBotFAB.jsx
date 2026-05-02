import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import SentiBotAvatar from "./SentiBotAvatar";

const AMBIENT_DIALOGUES = [
  "I'm here if you need to talk.",
  "How are you feeling today?",
  "Remember to take a deep breath.",
  "You're doing great.",
  "Want to reflect on your day?",
];

const ROUTE_DIALOGUES = {
  "/dashboard": "Welcome to your Journal. This is a safe space to write down your thoughts. I'll analyze your entries to help you understand your emotional state.",
  "/dashboard/": "Welcome to your Journal. This is a safe space to write down your thoughts. I'll analyze your entries to help you understand your emotional state.",
  "/dashboard/heatmap": "This is the Mood Heatmap. Here we can visualize your emotional journey over time through color patterns.",
  "/dashboard/history": "This is your History. You can review all your past entries and clinical analyses here.",
  "/dashboard/gratitude": "Welcome to the Gratitude Jar! Taking a moment to appreciate the little things does wonders for mental health.",
  "/dashboard/screener": "Here is the Clinical Screener. You can take standardized mental health assessments to keep track of your clinical symptoms.",
  "/dashboard/wellness": "These are your Wellness Tools. Explore breathing exercises and grounding techniques to center yourself.",
};

export default function SentiBotFAB({ emotion = null }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [showDialogue, setShowDialogue] = useState(false);
  const [dialogueText, setDialogueText] = useState(AMBIENT_DIALOGUES[0]);

  // Handle route change dialogues
  useEffect(() => {
    // Only show if not on chat
    if (location.pathname.includes("/chat")) return;

    // Remove trailing slash for consistent matching
    const normalizedPath = location.pathname.endsWith("/") && location.pathname !== "/"
      ? location.pathname.slice(0, -1)
      : location.pathname;

    const matchedText = ROUTE_DIALOGUES[normalizedPath];

    if (matchedText) {
      setDialogueText(matchedText);
      setShowDialogue(true);
      const timer = setTimeout(() => setShowDialogue(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [location.pathname]);

  // Ambient dialogue popups
  useEffect(() => {
    const interval = setInterval(() => {
      // 30% chance to show a bubble every 20 seconds if not already showing
      if (Math.random() > 0.7 && !showDialogue) {
        setDialogueText(AMBIENT_DIALOGUES[Math.floor(Math.random() * AMBIENT_DIALOGUES.length)]);
        setShowDialogue(true);
        setTimeout(() => setShowDialogue(false), 5000);
      }
    }, 20000);
    return () => clearInterval(interval);
  }, [showDialogue]);

  // Hide on the chat page itself
  if (location.pathname.includes("/chat")) return null;

  return (
    <div className="sentibot-fab animate-medical-fade-in" style={{ zIndex: 9999 }}>
      {showDialogue && (
        <div 
          className="sentibot-speech-bubble"
          onClick={() => navigate("/dashboard/chat")}
        >
          {dialogueText}
        </div>
      )}
      
      <div className="sentibot-fab-pulse" />
      
      <div 
        className="sentibot-fab-inner" 
        onClick={() => navigate("/dashboard/chat")}
        onMouseEnter={() => {
          setDialogueText("Chat with me!");
          setShowDialogue(true);
        }}
        onMouseLeave={() => setShowDialogue(false)}
        title="Chat with SentiBot"
      >
        <SentiBotAvatar 
          emotion={showDialogue ? "Normal" : (emotion || "idle")} 
          size="md" 
          animate={true} 
        />
      </div>
    </div>
  );
}
