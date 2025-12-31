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
            textBuffer = line + "\n" + textBuffer;
            break;
          }
        }
      }

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
      
      const allMessagesWithNew = [...messages, userMsg, { role: "assistant", content: assistantContent }];
      const detectedPattern = detectPatterns(allMessagesWithNew);
      
      if (detectedPattern) {
        setMessages(prev => {
          const newMessages = [...prev];
          const lastIdx = newMessages.length - 1;
          if (newMessages[lastIdx]?.role === "assistant") {
            newMessages[lastIdx] = { ...newMessages[lastIdx], pattern: detectedPattern };
          }
          return newMessages;
        });
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
  }, [messages]);

  const handleSend = useCallback((message: string) => {
    if (message.trim()) {
      setShowFollowUp(false);
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
    
    if (response.includes('sodium')) questions.push('How much sodium is safe daily?');
    if (response.includes('sugar')) questions.push('What are sugar-free alternatives?');
    if (response.includes('trans fat')) questions.push('Why are trans fats harmful?');
    if (response.includes('maggi')) questions.push('Is Top Ramen healthier than Maggi?');
    if (response.includes('parle')) questions.push('Which biscuits are healthiest?');
    if (response.includes('preservative')) questions.push('Are preservatives dangerous?');
    if (response.includes('palm oil')) questions.push('Why avoid palm oil?');
    
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
    
    if (questions.length < 3) {
      questions.push('What nutrients does this provide?');
      questions.push('How does this affect my health?');
    }
    
    return [...new Set(questions)].slice(0, 4);
  };

  return (
    <div className="flex flex-col h-full">
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <WelcomeMessage onSuggestionSelect={handleSuggestionSelect} />
          </div>
        ) : (
          <div className="flex">
            {/* Left Sidebar - AI Confidence */}
            <div className="w-64 flex-shrink-0 p-4">
              {(() => {
                const lastMessage = messages[messages.length - 1];
                const detectedPattern = lastMessage?.role === "assistant" && !isLoading ? 
                  lastMessage.pattern || detectPatterns(messages) : null;
                
                if (!detectedPattern) return null;
                
                return (
                  <div className="sticky top-4">
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                      <div className="flex items-center gap-2 mb-3">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                          detectedPattern.confidence >= 80 ? 'bg-emerald-500' :
                          detectedPattern.confidence >= 60 ? 'bg-blue-500' : 'bg-amber-500'
                        }`}>
                          <span className="text-white font-bold text-xs">AI</span>
                        </div>
                        <span className="text-sm font-medium text-gray-900">Confidence</span>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900 mb-2">{detectedPattern.confidence}%</div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-500 ${
                              detectedPattern.confidence >= 80 ? 'bg-emerald-500' :
                              detectedPattern.confidence >= 60 ? 'bg-blue-500' : 'bg-amber-500'
                            }`} 
                            style={{width: `${detectedPattern.confidence}%`}}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-600">{detectedPattern.description}</p>
                      </div>
                    </div>
                  </div>
                );
              })()
              }
            </div>
            
            {/* Main Chat Area */}
            <div className="flex-1 max-w-3xl mx-auto px-4 py-6">
              <div className="space-y-6">
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
              </div>
            </div>
            
            {/* Right Sidebar - AI Pattern */}
            <div className="w-64 flex-shrink-0 p-4">
              {(() => {
                const lastMessage = messages[messages.length - 1];
                const detectedPattern = lastMessage?.role === "assistant" && !isLoading ? 
                  lastMessage.pattern || detectPatterns(messages) : null;
                
                if (!detectedPattern) return null;
                
                return (
                  <div className="sticky top-4">
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
                      <h3 className="text-sm font-medium text-blue-900 mb-2">Pattern Analysis</h3>
                      <div className="text-xs text-blue-700 space-y-1">
                        <div>Type: {detectedPattern.title}</div>
                        <div>Insights: {detectedPattern.insights || 'Processing...'}</div>
                      </div>
                    </div>
                  </div>
                );
              })()
              }
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-4 py-4">
          {showFollowUp && !isLoading && messages.length > 0 && messages[messages.length - 1]?.role === "assistant" && (
            <div className="mb-4">
              <div className="flex flex-wrap gap-2">
                {(() => {
                  const lastResponse = messages[messages.length - 1]?.content || "";
                  const questions = generateQuickQuestions(lastResponse, messages);
                  return questions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleFollowUpSelect(question)}
                      className="px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded-lg transition-colors"
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
