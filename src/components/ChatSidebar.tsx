import { MessageSquare, Plus, Clock } from "lucide-react";

interface ChatSession {
  id: string;
  title: string;
  date: string;
  active?: boolean;
}

interface ChatSidebarProps {
  sessions: ChatSession[];
  onNewChat: () => void;
  onSelectSession: (id: string) => void;
}

const ChatSidebar = ({ sessions, onNewChat, onSelectSession }: ChatSidebarProps) => {
  return (
    <aside className="w-72 bg-primary flex flex-col h-full">
      {/* New Chat */}
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 py-2.5 px-4 rounded-lg border border-primary-foreground/20 text-primary-foreground text-sm font-medium hover:bg-primary-foreground/10 transition-colors"
        >
          <Plus className="h-4 w-4" />
          New Analysis
        </button>
      </div>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
        <p className="px-3 py-2 text-[10px] font-semibold text-primary-foreground/40 uppercase tracking-wider">
          Recent
        </p>
        {sessions.map((session) => (
          <button
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`w-full text-left flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              session.active
                ? "bg-primary-foreground/15 text-primary-foreground"
                : "text-primary-foreground/60 hover:bg-primary-foreground/5 hover:text-primary-foreground/80"
            }`}
          >
            <MessageSquare className="h-4 w-4 shrink-0" />
            <span className="truncate">{session.title}</span>
          </button>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-primary-foreground/10">
        <div className="flex items-center gap-2 text-primary-foreground/40 text-xs">
          <Clock className="h-3.5 w-3.5" />
          <span>VEM Smart Inventory v1.0</span>
        </div>
      </div>
    </aside>
  );
};

export default ChatSidebar;
