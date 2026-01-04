import { useState, useRef, useEffect, useCallback } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";
import { WelcomeMessage } from "./WelcomeMessage";
import { toast } from "@/hooks/use-toast";
import { generateNaturalFollowUps } from "@/lib/aiUtils";
import { useLanguage } from "@/hooks/useLanguage";

interface Message {
  role: "user" | "assistant";
  content: string;
  image?: string;
  structuredData?: {
    ai_insight_title: string;
    quick_verdict: string;
    why_this_matters: string[];
    trade_offs: {
      positives: string[];
      negatives: string[];
    };
    uncertainty?: string;
    ai_advice: string;
  };
}

const CHAT_URL = `${import.meta.env.VITE_API_BASE_URL}/api/chat/stream`;

export const ChatContainer = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFollowUp, setShowFollowUp] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const language = useLanguage();

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
          session_id: sessionId,
          language: language
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
  }, [language]);

  const handleImageSelect = useCallback(async (file: File) => {
    // 1. Create optimistic message with image
    const imageUrl = URL.createObjectURL(file);
    const userMsg: Message = {
      role: "user",
      content: "Analyzing this product...",
      image: imageUrl
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // 2. Upload to backend
      const formData = new FormData();
      formData.append('file', file);
      formData.append('language', language);

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/analyze/image`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();

      // 3. Process result
      if (result.success && result.analysis) {
        // Try parsing JSON if it's a string, or use as is
        let structuredData;
        try {
          structuredData = typeof result.analysis === 'string'
            ? JSON.parse(result.analysis)
            : result.analysis;
        } catch (e) {
          console.error("Failed to parse analysis JSON", e);
        }

        const assistantMsg: Message = {
          role: "assistant",
          content: "",
          structuredData: structuredData || undefined
        };

        // If parsing failed, fallback to text content if it's not JSON
        if (!structuredData) {
          assistantMsg.content = result.analysis;
        }

        setMessages(prev => [...prev, assistantMsg]);
      } else {
        throw new Error("Invalid response");
      }
    } catch (error) {
      console.error('Image upload error:', error);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "I had trouble reading this image. You can try another photo or ask a question."
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [language]);

  const handleCameraAnalysis = useCallback(async (analysis: string) => {
    //Live camera returns JSON string from backend, parse it like image upload
    setIsLoading(true);

    try {
      // Try parsing JSON if it's a string
      let structuredData;
      try {
        structuredData = typeof analysis === 'string'
          ? JSON.parse(analysis)
          : analysis;
      } catch (e) {
        console.error("Failed to parse camera analysis JSON", e);
      }

      const assistantMsg: Message = {
        role: "assistant",
        content: "",
        structuredData: structuredData || undefined
      };

      // If parsing failed, fallback to text content
      if (!structuredData) {
        assistantMsg.content = analysis;
      }

      setMessages(prev => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Camera analysis error:', error);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "I had trouble processing the analysis. You can try again or ask a question."
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [language]);

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
          <div className="max-w-3xl mx-auto px-4 py-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div key={index}>
                  <ChatMessage
                    role={message.role}
                    content={message.content}
                    image={message.image}
                    structuredData={message.structuredData}
                    onFollowUpClick={handleFollowUpSelect}
                    isStreaming={
                      isLoading &&
                      index === messages.length - 1 &&
                      message.role === "assistant"
                    }
                  />
                </div>
              ))}
              {isLoading && messages[messages.length - 1]?.role === "user" && (
                <TypingIndicator />
              )}
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-border bg-background/95">
        <div className="max-w-3xl mx-auto px-4 py-3">
          {showFollowUp && !isLoading && messages.length > 0 && messages[messages.length - 1]?.role === "assistant" && (
            <div className="mb-3">
              <div className="flex gap-2 flex-wrap">
                {(() => {
                  const lastResponse = messages[messages.length - 1]?.content || "";
                  const questions = generateNaturalFollowUps(lastResponse, messages);
                  return questions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleFollowUpSelect(question)}
                      className="px-3 py-1.5 text-xs bg-card hover:bg-muted text-muted-foreground border border-border hover:border-primary/50 rounded-full transition-colors"
                    >
                      {question}
                    </button>
                  ));
                })()}
              </div>
            </div>
          )}

          <ChatInput
            onSend={handleSend}
            onImageSelect={handleImageSelect}
            onCameraAnalysis={handleCameraAnalysis}
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
};