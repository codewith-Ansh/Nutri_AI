import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { HealthRiskScore } from "./HealthRiskScore";
import { PatternInsight } from "./PatternInsight";
import { FollowUpQuestions } from "./FollowUpQuestions";
import { extractHealthScore, formatAIResponse } from "@/lib/aiUtils";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  pattern?: any;
  conversationHistory?: Array<{role: string, content: string}>;
  onFollowUpSelect?: (question: string) => void;
}

export const ChatMessage = ({ role, content, isStreaming, pattern, conversationHistory = [], onFollowUpSelect }: ChatMessageProps) => {
  const isUser = role === "user";
  
  // Extract health score if it's an AI response
  const healthScore = !isUser ? extractHealthScore(content) : null;
  
  // Debug logging
  if (!isUser && !isStreaming) {
    console.log('AI Response:', content);
    console.log('Health Score Extracted:', healthScore);
  }
  
  // Format the content (remove asterisks, format properly)
  const formattedContent = !isUser ? formatAIResponse(content) : content;

  // Parse markdown-style formatting for display
  const formatContent = (text: string) => {
    // Split by double newlines for paragraphs
    const paragraphs = text.split(/\n\n+/);
    
    return paragraphs.map((paragraph, i) => {
      // Handle bullet points
      if (paragraph.trim().startsWith('-') || paragraph.trim().startsWith('•')) {
        const items = paragraph.split('\n').filter(line => line.trim());
        return (
          <ul key={i} className="list-disc list-inside space-y-1 my-2">
            {items.map((item, j) => (
              <li key={j} className="text-sm leading-relaxed">
                {formatInlineText(item.replace(/^[-•]\s*/, ''))}
              </li>
            ))}
          </ul>
        );
      }
      
      // Handle numbered lists
      if (/^\d+\./.test(paragraph.trim())) {
        const items = paragraph.split('\n').filter(line => line.trim());
        return (
          <ol key={i} className="list-decimal list-inside space-y-1 my-2">
            {items.map((item, j) => (
              <li key={j} className="text-sm leading-relaxed">
                {formatInlineText(item.replace(/^\d+\.\s*/, ''))}
              </li>
            ))}
          </ol>
        );
      }
      
      return (
        <p key={i} className="text-sm leading-relaxed mb-2 last:mb-0">
          {formatInlineText(paragraph)}
        </p>
      );
    });
  };

  const formatInlineText = (text: string) => {
    // Handle bold text with **
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-foreground">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  return (
    <div
      className={cn(
        "flex gap-3 chat-bubble-enter",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser
            ? "bg-chat-user text-chat-user-foreground"
            : "bg-primary text-primary-foreground"
        )}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Message Bubble */}
      <div className="flex-1 max-w-[85%]">
        <div
          className={cn(
            "rounded-2xl px-4 py-3",
            isUser
              ? "bg-chat-user text-chat-user-foreground rounded-tr-sm ml-auto"
              : "bg-card border border-border shadow-sm rounded-tl-sm"
          )}
        >
          <div className={cn(isUser ? "text-chat-user-foreground" : "text-card-foreground")}>
            {isUser ? (
              <p className="text-sm leading-relaxed">{content}</p>
            ) : (
              <div className="text-sm leading-relaxed space-y-2">
                <div dangerouslySetInnerHTML={{ __html: formattedContent }} />
              </div>
            )}
          </div>
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
          )}
        </div>
        
        {/* Health Risk Score Component */}
        {healthScore && !isStreaming && (
          <HealthRiskScore
            score={healthScore.score}
            risks={healthScore.risks}
            positives={healthScore.positives}
            alternative={healthScore.alternative}
          />
        )}
        
        {/* Pattern Insight Component */}
        {pattern && !isStreaming && (
          <PatternInsight pattern={pattern} />
        )}
      </div>
    </div>
  );
};
