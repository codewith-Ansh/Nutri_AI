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
  language?: string;
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
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = localStorage.getItem('nutri_chat_messages');
    return saved ? JSON.parse(saved) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showFollowUp, setShowFollowUp] = useState(false);
  const [sessionId] = useState(() => {
    let id = localStorage.getItem('nutri_session_id');
    if (!id) {
      id = `session_${Date.now()}`;
      localStorage.setItem('nutri_session_id', id);
    }
    return id;
  });
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const language = useLanguage();
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    localStorage.setItem('nutri_chat_messages', JSON.stringify(messages));
  }, [messages]);



  const streamChat = useCallback(async (userMessage: string) => {
    const userMsg: Message = { role: "user", content: userMessage };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
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
      content: "",  // Empty content, let the image speak for itself
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

  const handleCameraAnalysis = useCallback(async (analysis: string, capturedImage?: string) => {
    // 1. FIRST: Show the captured image as a user message (if we have it)
    if (capturedImage) {
      const userMsg: Message = {
        role: "user",
        content: "",  // Empty content, let the image speak for itself
        image: capturedImage
      };
      setMessages(prev => [...prev, userMsg]);
    }

    // 2. THEN: Show loading
    setIsLoading(true);

    try {
      // 3. Parse the analysis
      let structuredData;
      try {
        structuredData = typeof analysis === 'string'
          ? JSON.parse(analysis)
          : analysis;
      } catch (e) {
        console.error("Failed to parse camera analysis JSON", e);
      }

      // 4. FINALLY: Show AI response as assistant message
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

  // Speech helper functions
  const getVoiceForLanguage = useCallback((lang: string): string => {
    const voiceMap: Record<string, string> = {
      'en': 'en-US',
      'hi': 'hi-IN',
      'hinglish': 'en-IN',
      'gu': 'gu-IN'
    };
    return voiceMap[lang] || 'en-US';
  }, []);

  const cleanTextForSpeech = useCallback((text: string, structuredData?: any): string => {
    if (structuredData) {
      let cleanText = `${structuredData.quick_verdict}. `;
      if (Array.isArray(structuredData.why_this_matters)) {
        cleanText += `${structuredData.why_this_matters.join('. ')}. `;
      }
      if (structuredData.ai_advice) {
        cleanText += `${structuredData.ai_advice}.`;
      }
      return cleanText;
    }

    return text
      .replace(/[#*_`]/g, '')
      .replace(/[\u{1F600}-\u{1F64F}]/gu, '')
      .replace(/[\u{1F300}-\u{1F5FF}]/gu, '')
      .replace(/[\u{1F680}-\u{1F6FF}]/gu, '')
      .replace(/[\u{2600}-\u{26FF}]/gu, '')
      .replace(/[\u{2700}-\u{27BF}]/gu, '')
      .replace(/✓|✗|•/g, '')
      .trim();
  }, []);

  const handleSpeak = useCallback(async (messageId: string) => {
    const index = parseInt(messageId.replace('msg-', ''));
    const message = messages[index];

    if (!message || message.role !== "assistant") return;

    const messageLang = message.language || language;

    // GUJARATI SAFETY GUARD: Gujarati not supported in browser-only mode
    if (messageLang === 'gu') {
      toast({
        title: "Speech not supported",
        description: "Gujarati speech is not supported on this device",
        variant: "destructive",
        duration: 3000,
      });
      return;
    }

    // Check browser support
    if (!('speechSynthesis' in window)) {
      toast({
        title: "Speech not supported",
        description: "Your browser doesn't support text-to-speech",
        variant: "destructive",
        duration: 3000,
      });
      return;
    }

    // Stop currently playing speech
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      if (speakingMessageId === messageId) {
        setIsSpeaking(false);
        setSpeakingMessageId(null);
        return;
      }
    }

    try {
      const cleanText = cleanTextForSpeech(message.content, message.structuredData);

      if (!cleanText) {
        toast({
          title: "No text to speak",
          variant: "destructive",
          duration: 2000,
        });
        return;
      }

      const voiceLang = getVoiceForLanguage(messageLang);
      const utterance = new SpeechSynthesisUtterance(cleanText);

      utterance.lang = voiceLang;
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      // Wait for voices to load
      let voices = window.speechSynthesis.getVoices();
      if (voices.length === 0) {
        await new Promise<void>((resolve) => {
          window.speechSynthesis.onvoiceschanged = () => {
            voices = window.speechSynthesis.getVoices();
            resolve();
          };
          setTimeout(() => resolve(), 100);
        });
      }

      // Explicitly select best matching voice
      const availableVoices = window.speechSynthesis.getVoices();

      // Try exact match first
      let matchingVoice = availableVoices.find(voice => voice.lang === voiceLang);

      // If no exact match, try language prefix (e.g., "hi" in "hi-IN")
      if (!matchingVoice) {
        const langPrefix = voiceLang.split('-')[0];
        matchingVoice = availableVoices.find(voice =>
          voice.lang.startsWith(langPrefix)
        );
      }

      if (matchingVoice) {
        utterance.voice = matchingVoice;
      } else {
        // No matching voice found
        toast({
          title: "Voice not available",
          description: `${messageLang} voice not found on your device`,
          variant: "destructive",
          duration: 3000,
        });
        return;
      }

      utterance.onend = () => {
        setIsSpeaking(false);
        setSpeakingMessageId(null);
      };

      utterance.onerror = (event) => {
        console.error('Speech error:', event);
        setIsSpeaking(false);
        setSpeakingMessageId(null);
      };

      setIsSpeaking(true);
      setSpeakingMessageId(messageId);
      window.speechSynthesis.speak(utterance);

    } catch (error) {
      console.error('Speech synthesis error:', error);
      setIsSpeaking(false);
      setSpeakingMessageId(null);
      toast({
        title: "Speech failed",
        description: "Failed to start speech synthesis",
        variant: "destructive",
        duration: 3000,
      });
    }
  }, [messages, language, isSpeaking, speakingMessageId, getVoiceForLanguage, cleanTextForSpeech, toast]);

  const handleEditMessage = useCallback((index: number) => {
    const messageToEdit = messages[index];
    if (messageToEdit.role === "user") {
      // Remove all messages after this one (including AI responses)
      setMessages(prev => prev.slice(0, index));

      // Trigger a custom event to populate the input
      window.dispatchEvent(new CustomEvent("editMessage", {
        detail: messageToEdit.content
      }));
    }
  }, [messages]);

  // Cleanup: Stop speech on unmount
  useEffect(() => {
    return () => {
      if (isSpeaking && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [isSpeaking]);

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
                    key={index}
                    messageId={`msg-${index}`}
                    role={message.role}
                    content={message.content}
                    image={message.image}
                    language={message.language}
                    structuredData={message.structuredData}
                    onFollowUpClick={handleFollowUpSelect}
                    onEdit={message.role === "user" ? () => handleEditMessage(index) : undefined}
                    onSpeak={message.role === "assistant" ? handleSpeak : undefined}
                    isSpeaking={speakingMessageId === `msg-${index}`}
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