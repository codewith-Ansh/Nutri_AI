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
  
  const healthScore = !isUser ? extractHealthScore(content) : null;
  
  if (!isUser && !isStreaming) {
    console.log('AI Response:', content);
    console.log('Health Score Extracted:', healthScore);
  }
  
  const formattedContent = !isUser ? formatAIResponse(content) : content;

  const formatContent = (text: string) => {
    const paragraphs = text.split(/\n\n+/);
    
    return paragraphs.map((paragraph, i) => {
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
    <div className={cn(
      "flex gap-4 py-6",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={cn(
        "max-w-[75%]",
        isUser ? "order-first" : ""
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3",
          isUser
            ? "bg-emerald-600 text-white ml-auto"
            : "bg-gray-50 text-gray-900 border border-gray-100"
        )}>
          <div>
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
        
        {healthScore && !isStreaming && (
          <div className="mt-4">
            <HealthRiskScore
              score={healthScore.score}
              risks={healthScore.risks}
              positives={healthScore.positives}
              alternative={healthScore.alternative}
            />
          </div>
        )}
        
        {pattern && !isStreaming && (
          <div className="mt-4">
            <PatternInsight pattern={pattern} />
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
};import { Bot, User } from "lucide-react";
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
  
  const healthScore = !isUser ? extractHealthScore(content) : null;
  
  if (!isUser && !isStreaming) {
    console.log('AI Response:', content);
    console.log('Health Score Extracted:', healthScore);
  }
  
  const formattedContent = !isUser ? formatAIResponse(content) : content;

  const formatContent = (text: string) => {
    const paragraphs = text.split(/\n\n+/);
    
    return paragraphs.map((paragraph, i) => {
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
    <div className={cn(
      "flex gap-4 py-6",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={cn(
        "max-w-[75%]",
        isUser ? "order-first" : ""
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3",
          isUser
            ? "bg-emerald-600 text-white ml-auto"
            : "bg-gray-50 text-gray-900 border border-gray-100"
        )}>
          <div>
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
        
        {healthScore && !isStreaming && (
          <div className="mt-4">
            <HealthRiskScore
              score={healthScore.score}
              risks={healthScore.risks}
              positives={healthScore.positives}
              alternative={healthScore.alternative}
            />
          </div>
        )}
        
        {pattern && !isStreaming && (
          <div className="mt-4">
            <PatternInsight pattern={pattern} />
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
};import { Bot, User } from "lucide-react";
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
  
  const healthScore = !isUser ? extractHealthScore(content) : null;
  
  if (!isUser && !isStreaming) {
    console.log('AI Response:', content);
    console.log('Health Score Extracted:', healthScore);
  }
  
  const formattedContent = !isUser ? formatAIResponse(content) : content;

  const formatContent = (text: string) => {
    const paragraphs = text.split(/\n\n+/);
    
    return paragraphs.map((paragraph, i) => {
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
    <div className={cn(
      "flex gap-4 py-6",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={cn(
        "max-w-[75%]",
        isUser ? "order-first" : ""
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3",
          isUser
            ? "bg-emerald-600 text-white ml-auto"
            : "bg-gray-50 text-gray-900 border border-gray-100"
        )}>
          <div>
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
        
        {healthScore && !isStreaming && (
          <div className="mt-4">
            <HealthRiskScore
              score={healthScore.score}
              risks={healthScore.risks}
              positives={healthScore.positives}
              alternative={healthScore.alternative}
            />
          </div>
        )}
        
        {pattern && !isStreaming && (
          <div className="mt-4">
            <PatternInsight pattern={pattern} />
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
};
