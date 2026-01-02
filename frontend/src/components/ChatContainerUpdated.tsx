import { useState, useRef, useEffect, useCallback } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";
import { WelcomeMessage } from "./WelcomeMessage";
import { toast } from "@/hooks/use-toast";
import { generateNaturalFollowUps } from "@/lib/aiUtils";

interface Message {
  role: "user" | "assistant";
  content: string;
  structuredData?: {
    ingredients: string[];
    risk: {
      level: "Low" | "Moderate" | "High";
      description: string;
    };
    reasons: string[];
    alternatives?: string[];
    suggested_followup: string[];
  };
}

const CHAT_URL = `${import.meta.env.VITE_API_BASE_URL}/api/chat/stream`;

export const ChatContainer = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFollowUp, setShowFollowUp] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

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
            
            // Handle structured data
            if (parsed.type === "structured") {
              setMessages(prev => {
                const newMessages = [...prev];
                const lastIdx = newMessages.length - 1;
                if (newMessages[lastIdx]?.role === "assistant") {
                  newMessages[lastIdx] = { 
                    ...newMessages[lastIdx], 
                    structuredData: parsed.data 
                  };
                }
                return newMessages;
              });
            }
            // Handle message content
            else {
              const content = parsed.choices?.[0]?.delta?.content as string | undefined;
              if (content) {
                assistantContent += content;
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIdx = newMessages.length - 1;
                  if (newMessages[lastIdx]?.role === "assistant") {
                    newMessages[lastIdx] = { 
                      ...newMessages[lastIdx], 
                      content: assistantContent
                    };
                  }
                  return newMessages;
                });
              }
            }
          } catch {
            textBuffer = line + "\n" + textBuffer;
            break;
          }
        }
      }
     
      setShowFollowUp(true);
    } catch (error) {
      console.error("Chat error:", error);
      setIsLoading(false);
     
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
  }, []);

  const handleSend = useCallback((message: string) => {
    if (message.trim()) {
      setShowFollowUp(false);
      streamChat(message);
    }
  }, [streamChat]);

  const handleFollowUpSelect = useCallback((question: string) => {
    handleSend(question);
  }, [handleSend]);

  return (
    <div className="flex flex-col h-full">
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <WelcomeMessage onSuggestionSelect={handleSend} />
          </div>
        ) : (
          <div className="max-w-3xl mx-auto px-4 py-6">
            <div className="space-y-6">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  role={message.role}
                  content={message.content}
                  structuredData={message.structuredData}
                  onFollowUpClick={handleFollowUpSelect}
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
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-4 py-4">
          {showFollowUp && !isLoading && messages.length > 0 && messages[messages.length - 1]?.role === "assistant" && (
            <div className="mb-4">
              <div className="flex gap-2 flex-wrap">
                {(() => {
                  const lastResponse = messages[messages.length - 1]?.content || "";
                  const questions = generateNaturalFollowUps(lastResponse, messages);
                  return questions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleFollowUpSelect(question)}
                      className="px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded-full transition-colors"
                    >
                      {question}
                    </button>
                  ));
                })()}
              </div>
            </div>
          )}
         
          <ChatInput onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};