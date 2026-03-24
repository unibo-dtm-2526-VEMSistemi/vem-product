import { useState, useRef, useEffect, useCallback } from "react";
import { Send, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage, { type ChatMsg } from "@/components/ChatMessage";
import LoadingSpinner from "@/components/LoadingSpinner";
import VemLogo from "@/components/VemLogo";
import { findProduct, searchProducts, MOCK_PRODUCTS } from "@/data/mockProducts";

const WELCOME_MSG: ChatMsg = {
  id: "welcome",
  role: "assistant",
  content:
    "Welcome to the VEM Intelligent Assistant. I can help you with product classification and accounting rules based on our Code of Ethics and 4-pillar strategy.\n\nTry entering a product code like VEM-TECH-X, VEM-CYBER-S, VEM-SOFT-M, or VEM-CLOUD-01.",
  timestamp: new Date(),
};

const SESSIONS = [
  { id: "1", title: "Cisco Nexus Analysis", date: "Today", active: true },
  { id: "2", title: "Certego Sentinel Review", date: "Yesterday" },
  { id: "3", title: "Cloud Migration Codes", date: "Mar 20" },
];

const ChatDashboard = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMsg[]>([WELCOME_MSG]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = useCallback(() => {
    const query = input.trim();
    if (!query || isLoading) return;

    const userMsg: ChatMsg = {
      id: Date.now().toString(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    // Simulate RAG processing
    setTimeout(() => {
      const product = findProduct(query) || searchProducts(query)[0];

      const aiMsg: ChatMsg = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: product
          ? `I found a match for "${query}". Here's the structured classification based on VEM's 4-pillar strategy:`
          : `No product found for "${query}". Available codes: ${MOCK_PRODUCTS.map((p) => p.code).join(", ")}. Try one of these or search by product name.`,
        product: product || undefined,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsLoading(false);
    }, 1500);
  }, [input, isLoading]);

  return (
    <div className="h-screen flex overflow-hidden">
      <ChatSidebar
        sessions={SESSIONS}
        onNewChat={() => setMessages([WELCOME_MSG])}
        onSelectSession={() => {}}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-background">
        {/* Header */}
        <header className="h-16 border-b flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate("/")} className="text-muted-foreground hover:text-foreground transition-colors">
              <ArrowLeft className="h-5 w-5" />
            </button>
            <VemLogo />
          </div>
          <span className="text-xs text-muted-foreground font-medium">Smart Inventory Assistant</span>
        </header>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="pl-11">
              <LoadingSpinner />
            </motion.div>
          )}
        </div>

        {/* Input */}
        <div className="border-t p-4 shrink-0">
          <div className="max-w-3xl mx-auto flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Enter a product code (e.g. VEM-TECH-X)..."
              className="flex-1 bg-muted rounded-lg px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="bg-accent text-accent-foreground rounded-lg px-5 py-3 font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatDashboard;
