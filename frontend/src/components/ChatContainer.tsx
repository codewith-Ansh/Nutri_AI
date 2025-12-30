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

const CHAT_URL = `${import.meta.env.VITE_API_BASE_URL}/api/chat/stream`;

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

  const generateQuickQuestions = (aiResponse: string, conversationHistory: Array<{role: string, content: string}>): string[] => {
    const questions: string[] = [];
    const response = aiResponse.toLowerCase();
    
    // Generate questions based on response content
    if (response.includes('sodium')) questions.push('How much sodium is safe daily?');
    if (response.includes('sugar')) questions.push('What are sugar-free alternatives?');
    if (response.includes('trans fat')) questions.push('Why are trans fats harmful?');
    if (response.includes('maggi')) questions.push('Is Top Ramen healthier than Maggi?');
    if (response.includes('parle')) questions.push('Which biscuits are healthiest?');
    if (response.includes('preservative')) questions.push('Are preservatives dangerous?');
    if (response.includes('palm oil')) questions.push('Why avoid palm oil?');
    
    // Get health score from response
    const scoreMatch = response.match(/(\d+)\/100/);
    const score = scoreMatch ? parseInt(scoreMatch[1]) : 50;
    
    if (score < 30) {
      questions.push('What are healthier alternatives?');
      questions.push('Should I avoid this completely?');
    } else if (score > 70) {
      questions.push('Can I eat this daily?');
      questions.push('What makes this healthy?');
    } else {
      questions.push('How can I make this healthier?');
    }
    
    // Add generic nutritional questions if not enough specific ones
    if (questions.length < 3) {
      questions.push('What nutrients does this provide?');
      questions.push('How does this affect my health?');
    }
    
    return [...new Set(questions)].slice(0, 4);
  };

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
              
              {/* AI Confidence Score - Only show when patterns detected */}
              {(() => {
                const detectedPattern = detectPatterns(messages);
                if (!detectedPattern || isLoading || messages.length === 0 || messages[messages.length - 1]?.role !== "assistant") return null;
                
                const confidence = detectedPattern.confidence;
                const getConfidenceColor = (conf: number) => {
                  if (conf >= 80) return 'from-green-500 to-emerald-500';
                  if (conf >= 60) return 'from-blue-500 to-indigo-500';
                  return 'from-yellow-500 to-orange-500';
                };
                
                return (
                  <div className="mt-6 max-w-md mx-auto">
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`w-8 h-8 rounded-full bg-gradient-to-r ${getConfidenceColor(confidence)} flex items-center justify-center shadow-sm`}>
                          <span className="text-white font-bold text-xs">AI</span>
                        </div>
                        <div>
                          <span className="text-sm font-bold text-blue-600">🎯 AI Confidence</span>
                          <p className="text-xs text-gray-600">{detectedPattern.title}</p>
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-xl font-bold text-blue-600 mb-2">{confidence}%</div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mb-2">
                          <div className={`bg-gradient-to-r ${getConfidenceColor(confidence)} h-1.5 rounded-full`} style={{width: `${confidence}%`}}></div>
                        </div>
                        <p className="text-xs text-gray-600">{detectedPattern.description}</p>
                      </div>
                    </div>
                  </div>
                );
              })()
              }
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-card/50 backdrop-blur-lg">
        <div className="container max-w-3xl mx-auto px-4 py-4">
          {/* Quick Questions - Horizontal Scroll */}
          {showFollowUp && !isLoading && messages.length > 0 && messages[messages.length - 1]?.role === "assistant" && (
            <div className="mb-3">
              <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
                {(() => {
                  const lastResponse = messages[messages.length - 1]?.content || "";
                  const questions = generateQuickQuestions(lastResponse, messages);
                  return questions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleFollowUpSelect(question)}
                      className="flex-shrink-0 px-3 py-1.5 text-xs font-medium bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 rounded-full transition-colors whitespace-nowrap"
                    >
                      {question}
                    </button>
                  ));
                })()}
              </div>
            </div>
          )}
          
          <ChatInput onSend={handleSend} disabled={isLoading} />
          <p className="text-xs text-muted-foreground text-center mt-2">
            NutriChat provides educational information only. Always consult a healthcare professional for medical advice.
          </p>
        </div>
      </div>
    </div>
  );
};
