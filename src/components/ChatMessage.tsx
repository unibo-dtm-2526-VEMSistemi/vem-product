import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";
import ProductCard from "./ProductCard";
import { type Product } from "@/data/mockProducts";

export interface ChatMsg {
  id: string;
  role: "user" | "assistant";
  content: string;
  product?: Product;
  timestamp: Date;
}

interface ChatMessageProps {
  message: ChatMsg;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? "bg-muted" : "bg-primary"
      }`}>
        {isUser ? (
          <User className="h-4 w-4 text-muted-foreground" />
        ) : (
          <Bot className="h-4 w-4 text-primary-foreground" />
        )}
      </div>

      <div className={`max-w-[75%] space-y-3 ${isUser ? "text-right" : ""}`}>
        <div className={`inline-block rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-muted text-foreground rounded-bl-sm"
        }`}>
          {message.content}
        </div>

        {message.product && (
          <ProductCard product={message.product} />
        )}

        <p className="text-[10px] text-muted-foreground">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </p>
      </div>
    </motion.div>
  );
};

export default ChatMessage;
