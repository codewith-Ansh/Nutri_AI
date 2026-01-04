import React from "react";
import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatAIResponse } from "@/lib/aiUtils";
import { StructuredResponse } from "./StructuredResponse";
import { MessageActions } from "./MessageActions";

interface ChatMessageProps {
  messageId: string;
  role: "user" | "assistant";
  content: string;
  image?: string;
  language?: string;
  isStreaming?: boolean;
  structuredData?: any;
  onFollowUpClick?: (question: string) => void;
  onEdit?: () => void;
  onSpeak?: (messageId: string) => void;
  isSpeaking?: boolean;
}

// Helper to parse JSON from AI response
const tryParseStructuredResponse = (content: string) => {
  try {
    // Look for JSON in the response
    const jsonMatch = content.match(/\{[\s\S]*"ai_insight_title"[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      // Validate required fields
      if (parsed.ai_insight_title && parsed.quick_verdict && parsed.why_this_matters) {
        return parsed;
      }
    }
  } catch (e) {
    // Not valid JSON or not structured format
    return null;
  }
  return null;
};

export const ChatMessage = ({
  messageId,
  role,
  content,
  image,
  language,
  structuredData,
  onFollowUpClick,
  isStreaming,
  onEdit,
  onSpeak,
  isSpeaking
}: ChatMessageProps) => {
  const isUser = role === "user";

  // Try to parse structured response from AI
  const parsedStructuredData = !isUser ? tryParseStructuredResponse(content) : null;

  // If we have structured data, don't show the raw content
  const shouldShowRawContent = !parsedStructuredData;

  // AI-native formatting - no scores, no technical indicators
  const formattedContent = !isUser && shouldShowRawContent ? formatAIResponse(content) : content;

  const formatContent = (text: string) => {
    const paragraphs = text.split(/\n\n+/);

    return paragraphs.map((paragraph, i) => {
      // Simple paragraph formatting - no complex structures
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
          <strong key={i} className="font-medium text-gray-900">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  return (
    <div className={cn(
      "flex gap-3 py-3 group",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-card border border-primary/30 flex items-center justify-center">
          <Bot className="w-3.5 h-3.5 text-primary" />
        </div>
      )}

      <div className={cn(
        "max-w-[90%] sm:max-w-[85%] lg:max-w-[75%]",
        isUser ? "order-first" : ""
      )}>
        {/* Message Bubble */}
        <div className={cn(
          "relative px-3 py-2 sm:px-4 sm:py-2.5 rounded-2xl shadow-sm text-sm border transition-all duration-200",
          isUser
            ? "bg-primary text-primary-foreground border-primary"
            : isSpeaking
              ? "bg-primary/10 border-primary ring-2 ring-primary/30"
              : "bg-card text-foreground border-border"
        )}>
          {/* Image Attachment */}
          {image && (
            <div className="mb-2 rounded-lg overflow-hidden border border-border/50">
              <img
                src={image}
                alt="Uploaded food label"
                className="w-full max-w-[200px] sm:max-w-[250px] lg:max-w-[280px] h-auto object-cover block"
              />
            </div>
          )}
          {isUser ? (
            <p className="text-sm leading-relaxed">{content}</p>
          ) : (
            <div>
              {/* Show parsed structured response if available */}
              {parsedStructuredData && (
                <StructuredResponse data={parsedStructuredData} />
              )}

              {/* Show original structured data if provided (legacy) */}
              {!parsedStructuredData && structuredData && (
                <StructuredResponse data={structuredData as any} />
              )}

              {/* Show narrative content if no structured data */}
              {shouldShowRawContent && !structuredData && (
                <div className="bg-muted/50 text-foreground border border-border rounded-xl px-3 py-2">
                  <div className="text-sm leading-relaxed space-y-1">
                    <div dangerouslySetInnerHTML={{ __html: formattedContent }} />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        {isStreaming && (
          <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1 text-primary" />
        )}

        {/* Message Actions */}
        {!isStreaming && (
          <div className="flex justify-end mt-1">
            <MessageActions
              content={content}
              structuredData={structuredData}
              role={role}
              language={language}
              messageId={messageId}
              onEdit={role === "user" ? onEdit : undefined}
              onSpeak={role === "assistant" ? onSpeak : undefined}
              isSpeaking={isSpeaking}
            />
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-card border border-border flex items-center justify-center">
          <User className="w-3.5 h-3.5 text-muted-foreground" />
        </div>
      )}
    </div>
  );
};
