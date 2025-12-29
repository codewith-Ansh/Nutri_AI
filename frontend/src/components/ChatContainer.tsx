import { useState, useRef, useEffect, useCallback } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";
import { WelcomeMessage } from "./WelcomeMessage";
import { FollowUpQuestions } from "./FollowUpQuestions";
import { toast } from "@/hooks/use-toast";
import { detectPatterns } from "@/lib/aiUtils";

interface Message {
  role: "user" | "assistant";
  content: string;
  pattern?: any;
}

const CHAT_URL = `${import.meta.env.VITE_API_BASE_URL}/chat/stream`;

export const ChatContainer = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFollowUp, setShowFollowUp] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const streamChat = useCallback(async (userMessage: string) => {
    const userMsg: Message = { role: "user", content: userMessage };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Create session ID if we don't have one
      const sessionId = "session_" + Date.now();
      
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: sessionId
        }),
      });

      if (!resp.ok) {
        const errorData = await resp.json().catch(() => ({}));
        throw new Error(errorData.error || `Request failed with status ${resp.status}`);
      }

      if (!resp.body) {
        throw new Error("No response body");
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let textBuffer = "";
      let assistantContent = "";
      let streamDone = false;

      // Add empty assistant message
      setMessages(prev => [...prev, { role: "assistant", content: "" }]);
      setIsLoading(false);

      while (!streamDone) {
        const { done, value } = await reader.read();
        if (done) break;
        textBuffer += decoder.decode(value, { stream: true });

        let newlineIndex: number;
        while ((newlineIndex = textBuffer.indexOf("\n")) !== -1) {
          let line = textBuffer.slice(0, newlineIndex);
          textBuffer = textBuffer.slice(newlineIndex + 1);

          if (line.endsWith("\r")) line = line.slice(0, -1);
          if (line.startsWith(":") || line.trim() === "") continue;
          if (!line.startsWith("data: ")) continue;

          const jsonStr = line.slice(6).trim();
          if (jsonStr === "[DONE]") {
            streamDone = true;
            break;
          }

          try {
            const parsed = JSON.parse(jsonStr);
            const content = parsed.choices?.[0]?.delta?.content as string | undefined;
            if (content) {
              assistantContent += content;
              setMessages(prev => {
                const newMessages = [...prev];
                const lastIdx = newMessages.length - 1;
                if (newMessages[lastIdx]?.role === "assistant") {
                  newMessages[lastIdx] = { ...newMessages[lastIdx], content: assistantContent };
                }
                return newMessages;
              });
            }
          } catch {
            // Incomplete JSON, put it back
            textBuffer = line + "\n" + textBuffer;
            break;
          }
        }
      }

      // Final flush
      if (textBuffer.trim()) {
        for (let raw of textBuffer.split("\n")) {
          if (!raw) continue;
          if (raw.endsWith("\r")) raw = raw.slice(0, -1);
          if (raw.startsWith(":") || raw.trim() === "") continue;
          if (!raw.startsWith("data: ")) continue;
          const jsonStr = raw.slice(6).trim();
          if (jsonStr === "[DONE]") continue;
          try {
            const parsed = JSON.parse(jsonStr);
            const content = parsed.choices?.[0]?.delta?.content as string | undefined;
            if (content) {
              assistantContent += content;
              setMessages(prev => {
                const newMessages = [...prev];
                const lastIdx = newMessages.length - 1;
                if (newMessages[lastIdx]?.role === "assistant") {
                  newMessages[lastIdx] = { ...newMessages[lastIdx], content: assistantContent };
                }
                return newMessages;
              });
            }
          } catch { /* ignore */ }
        }
      }
      
      // Detect patterns after response is complete
      const allMessagesWithNew = [...messages, userMsg, { role: "assistant", content: assistantContent }];
      const detectedPattern = detectPatterns(allMessagesWithNew);
      
      if (detectedPattern) {
        // Add pattern to the last assistant message
        setMessages(prev => {
          const newMessages = [...prev];
          const lastIdx = newMessages.length - 1;
          if (newMessages[lastIdx]?.role === "assistant") {
            newMessages[lastIdx] = { ...newMessages[lastIdx], pattern: detectedPattern };
          }
          return newMessages;
        });
      }
      
      // Show follow-up questions after AI response
      setShowFollowUp(true);
    } catch (error) {
      console.error("Chat error:", error);
      setIsLoading(false);
      
      // Remove failed assistant message if it was empty
      setMessages(prev => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg?.role === "assistant" && !lastMsg.content) {
          return prev.slice(0, -1);
        }
        return prev;
      });

      toast({
        title: "Unable to get response",
        description: error instanceof Error ? error.message : "Please try again in a moment.",
        variant: "destructive",
      });
    }
  }, [messages]);

  const handleSend = useCallback((message: string) => {
    if (message.trim()) {
      setShowFollowUp(false); // Hide follow-up when new message sent
      streamChat(message);
    }
  }, [streamChat]);

  const handleSuggestionSelect = useCallback((suggestion: string) => {
    handleSend(suggestion);
  }, [handleSend]);

  const handleFollowUpSelect = useCallback((question: string) => {
    handleSend(question);
  }, [handleSend]);

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto chat-scroll px-4 py-6"
      >
        <div className="container max-w-3xl mx-auto">
          {messages.length === 0 ? (
            <WelcomeMessage onSuggestionSelect={handleSuggestionSelect} />
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  role={message.role}
                  content={message.content}
                  pattern={message.pattern}
                  conversationHistory={messages}
                  onFollowUpSelect={handleFollowUpSelect}
                  isStreaming={
                    isLoading &&
                    index === messages.length - 1 &&
                    message.role === "assistant"
                  }
                />
              ))}
              {isLoading && messages[messages.length - 1]?.role === "user" && (
                <TypingIndicator />
              )}
              
              {/* Follow-up Questions - Separate Section */}
              {showFollowUp && !isLoading && messages.length > 0 && messages[messages.length - 1]?.role === "assistant" && (
                <div className="mt-6">
                  <FollowUpQuestions 
                    aiResponse={messages[messages.length - 1]?.content || ""}
                    conversationHistory={messages}
                    onQuestionSelect={handleFollowUpSelect}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-card/50 backdrop-blur-lg">
        <div className="container max-w-3xl mx-auto px-4 py-4">
          <ChatInput onSend={handleSend} disabled={isLoading} />
          <p className="text-xs text-muted-foreground text-center mt-2">
            NutriChat provides educational information only. Always consult a healthcare professional for medical advice.
          </p>
        </div>
      </div>
    </div>
  );
};
