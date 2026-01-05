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
  onEdit
}: ChatMessageProps) => {
  const isUser = role === "user";

  // Try to parse structured response from AI
  const parsedStructuredData = !isUser ? tryParseStructuredResponse(content) : null;

  // If we have structured data, don't show the raw content
  const shouldShowRawContent = !parsedStructuredData;

  // AI-native formatting - no scores, no technical indicators
  const formattedContent = !isUser && shouldShowRawContent ? formatAIResponse(content) : content;

  // Final structured data to use (prefer prop, then parsed)
  const finalStructuredData = structuredData || parsedStructuredData;

  return (
    <div className={cn(
      "group flex gap-3 px-3 sm:px-4 py-4 transition-colors",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      {/* Avatar */}
      {isUser ? (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-primary flex items-center justify-center">
          <User className="w-4 h-4 text-primary-foreground" />
        </div>
      ) : (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-card border border-primary/30 flex items-center justify-center">
          <Bot className="w-3.5 h-3.5 text-primary" />
        </div>
      )}

      <div className={cn(
        "max-w-[95%] sm:max-w-[85%] md:max-w-[75%] relative",
        isUser ? "order-first" : ""
      )}>
        {/* Message Bubble */}
        <div className={cn(
          "relative px-3 py-3 sm:px-4 sm:py-3 rounded-xl sm:rounded-2xl shadow-sm text-sm border transition-all duration-200 break-words overflow-hidden",
          isUser
            ? "bg-primary text-primary-foreground border-primary"
            : "bg-card text-foreground border-border"
        )}>
          {/* User image */}
          {isUser && image && (
            <div className="mb-2">
              <img
                src={image}
                alt="Uploaded"
                className="max-w-full h-auto rounded-lg border border-border/50"
              />
            </div>
          )}

          {/* Content */}
          {finalStructuredData ? (
            <StructuredResponse
              data={finalStructuredData}
            />
          ) : (
            <div className="whitespace-pre-wrap">
              {formattedContent}
              {isStreaming && (
                <span className="inline-block w-1 h-4 ml-1 bg-current animate-pulse" />
              )}
            </div>
          )}
        </div>

        {/* Message Actions - Only for assistant messages */}
        {!isUser && !isStreaming && (
          <div className="mt-2 flex justify-end">
            <MessageActions
              content={content}
              structuredData={finalStructuredData}
              role={role}
              language={language}
              messageId={messageId}
              onEdit={onEdit}
            />
          </div>
        )}
      </div>
    </div>
  );
};