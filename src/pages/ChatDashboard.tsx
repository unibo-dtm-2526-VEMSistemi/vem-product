import { useState, useRef, useEffect, useCallback } from "react";
import { Send, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ChatSidebar from "@/components/ChatSidebar";
import ChatMessage, { type ChatMsg } from "@/components/ChatMessage";
import LoadingSpinner from "@/components/LoadingSpinner";
import VemLogo from "@/components/VemLogo";
import { findProduct, searchProducts, MOCK_PRODUCTS, type Product } from "@/data/mockProducts";
import { useToast } from "@/hooks/use-toast";

interface ChatSession {
  id: string;
  title: string;
  date: string;
  active?: boolean;
}

const INSTRUCTION_TITLE = "Instruction";
const INSTRUCTION_CONTENT =
  "How to use this assistant:\n\n" +
  "1. Enter a product code or product description in the input field.\n" +
  "2. Review the classification card and accounting rule details.\n" +
  "3. Click 'Consistent with Accounting' to collapse and keep the classification.\n" +
  "4. Click 'Requires Review' if something is wrong, then describe the issue and send it.\n\n" +
  "Examples: VEM-TECH-X, VEM-CYBER-S, VEM-SOFT-M, VEM-CLOUD-01.";

const CHAT_WELCOME_CONTENT =
  "New analysis started. Enter a product code or description to continue.";

const NEW_CHAT_TITLE = "New Analysis";
const INITIAL_SESSIONS: ChatSession[] = [{ id: "1", title: INSTRUCTION_TITLE, date: "Today" }];

const createMessage = (sessionId: string, content: string): ChatMsg => ({
  id: `${sessionId}-welcome`,
  role: "assistant",
  content,
  timestamp: new Date(),
});

const buildInitialMessagesMap = (): Record<string, ChatMsg[]> =>
  Object.fromEntries(
    INITIAL_SESSIONS.map((session) => [
      session.id,
      [createMessage(session.id, session.title === INSTRUCTION_TITLE ? INSTRUCTION_CONTENT : CHAT_WELCOME_CONTENT)],
    ]),
  );

const formatSessionTitle = (query: string): string => {
  const normalized = query.replace(/\s+/g, " ").trim();
  if (!normalized) return NEW_CHAT_TITLE;
  return normalized.length > 32 ? `${normalized.slice(0, 32)}...` : normalized;
};

const ChatDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [sessions, setSessions] = useState<ChatSession[]>(INITIAL_SESSIONS);
  const [currentSessionId, setCurrentSessionId] = useState<string>(INITIAL_SESSIONS[0].id);
  const [messagesBySession, setMessagesBySession] = useState<Record<string, ChatMsg[]>>(buildInitialMessagesMap);
  const [loadingBySession, setLoadingBySession] = useState<Record<string, boolean>>({});
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const currentMessages = messagesBySession[currentSessionId] ?? [];
  const isLoading = Boolean(loadingBySession[currentSessionId]);
  const sidebarSessions = sessions.map((session) => ({ ...session, active: session.id === currentSessionId }));

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [currentMessages, isLoading, currentSessionId]);

  const handleSelectSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId);
    setInput("");
  }, []);

  const handleNewChat = useCallback(() => {
    const newSessionId = `session-${Date.now()}`;
    const newSession: ChatSession = {
      id: newSessionId,
      title: NEW_CHAT_TITLE,
      date: "Today",
    };

    setSessions((prev) => [newSession, ...prev]);
    setMessagesBySession((prev) => ({
      ...prev,
      [newSessionId]: [createMessage(newSessionId, CHAT_WELCOME_CONTENT)],
    }));
    setLoadingBySession((prev) => ({ ...prev, [newSessionId]: false }));
    setCurrentSessionId(newSessionId);
    setInput("");
  }, []);

  const handleSend = useCallback(() => {
    const query = input.trim();
    const sessionId = currentSessionId;

    if (!query || loadingBySession[sessionId]) return;

    const userMsg: ChatMsg = {
      id: `${Date.now()}-user`,
      role: "user",
      content: query,
      timestamp: new Date(),
    };

    setMessagesBySession((prev) => ({
      ...prev,
      [sessionId]: [...(prev[sessionId] ?? []), userMsg],
    }));
    setSessions((prev) =>
      prev.map((session) =>
        session.id === sessionId && session.title === NEW_CHAT_TITLE
          ? { ...session, title: formatSessionTitle(query) }
          : session,
      ),
    );
    setInput("");
    setLoadingBySession((prev) => ({ ...prev, [sessionId]: true }));

    setTimeout(() => {
      const product = findProduct(query) || searchProducts(query)[0];

      const aiMsg: ChatMsg = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        content: product
          ? `I found a match for "${query}". Here's the structured classification based on VEM's 4-pillar strategy:`
          : `No product found for "${query}". Available codes: ${MOCK_PRODUCTS.map((p) => p.code).join(", ")}. Try one of these or search by product name.`,
        product: product || undefined,
        timestamp: new Date(),
      };

      setMessagesBySession((prev) => ({
        ...prev,
        [sessionId]: [...(prev[sessionId] ?? []), aiMsg],
      }));
      setLoadingBySession((prev) => ({ ...prev, [sessionId]: false }));
    }, 1500);
  }, [currentSessionId, input, loadingBySession]);

  const handleReviewSubmit = useCallback(
    (product: Product, problem: string) => {
      const sessionId = currentSessionId;
      const now = Date.now();
      const reviewRequestMsg: ChatMsg = {
        id: `${now}-review-user`,
        role: "user",
        content: `Review request for ${product.code}: ${problem}`,
        timestamp: new Date(),
      };

      const ackMsg: ChatMsg = {
        id: `${now}-review-assistant`,
        role: "assistant",
        content:
          `Request sent. The accounting team will review ${product.code}. ` +
          "You can continue with another product or add more context.",
        timestamp: new Date(),
      };

      setMessagesBySession((prev) => ({
        ...prev,
        [sessionId]: [...(prev[sessionId] ?? []), reviewRequestMsg, ackMsg],
      }));
      toast({
        title: "Review request sent",
        description: `${product.code} has been flagged for manual review.`,
      });
    },
    [currentSessionId, toast],
  );

  const handleConsistentSubmit = useCallback(
    (product: Product) => {
      const sessionId = currentSessionId;
      const now = Date.now();
      const ackMsg: ChatMsg = {
        id: `${now}-consistent-assistant`,
        role: "assistant",
        content: `Thank you, code ${product.code} has been marked as correctly classified.`,
        timestamp: new Date(),
      };

      setMessagesBySession((prev) => ({
        ...prev,
        [sessionId]: [...(prev[sessionId] ?? []), ackMsg],
      }));
    },
    [currentSessionId],
  );

  return (
    <div className="h-screen flex overflow-hidden">
      <ChatSidebar sessions={sidebarSessions} onNewChat={handleNewChat} onSelectSession={handleSelectSession} />

      <div className="flex-1 flex flex-col bg-background">
        <header className="h-16 border-b flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate("/")} className="text-muted-foreground hover:text-foreground transition-colors">
              <ArrowLeft className="h-5 w-5" />
            </button>
            <VemLogo />
          </div>
          <span className="text-xs text-muted-foreground font-medium">Smart Inventory Assistant</span>
        </header>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {currentMessages.map((msg) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              onReviewSubmit={handleReviewSubmit}
              onConsistentSubmit={handleConsistentSubmit}
            />
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="pl-11">
              <LoadingSpinner />
            </motion.div>
          )}
        </div>

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
