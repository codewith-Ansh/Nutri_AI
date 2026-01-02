import { useState, useRef, useEffect } from "react";
import { Send, Camera, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput = ({ onSend, disabled, placeholder = "Message NutriChat..." }: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      try {
        // Actually upload the image to the API
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/analyze/image`, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          throw new Error('Failed to analyze image');
        }
        
        const result = await response.json();
        
        if (result.success && result.analysis) {
          onSend(result.analysis);
        } else {
          onSend("I couldn't analyze this image clearly. Please try taking another photo with better lighting.");
        }
      } catch (error) {
        console.error('Image upload error:', error);
        onSend("I'm having trouble processing the image right now. Please try again.");
      }
    }
    e.target.value = '';
  };

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-2xl shadow-sm focus-within:border-gray-300 transition-all">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={cn(
            "flex-1 resize-none bg-transparent text-gray-900 placeholder:text-gray-500 focus:outline-none text-base leading-6",
            "max-h-[120px] min-h-[20px] py-1",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        />
        
        {/* Image Upload Buttons */}
        <Button
          type="button"
          variant="ghost"
          size="icon"
          disabled={disabled}
          onClick={() => fileInputRef.current?.click()}
          className="h-10 w-10 text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          title="Upload image"
        >
          <Upload className="h-4 w-4" />
        </Button>
        
        <Button
          type="button"
          variant="ghost"
          size="icon"
          disabled={disabled}
          onClick={() => cameraInputRef.current?.click()}
          className="h-10 w-10 text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          title="Take photo"
        >
          <Camera className="h-4 w-4" />
        </Button>
        
        <Button
          type="submit"
          size="icon"
          disabled={disabled || !message.trim()}
          className={cn(
            "h-10 w-10 rounded-xl shrink-0 transition-all",
            message.trim() 
              ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm" 
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
          )}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
      
      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileSelect}
        className="hidden"
      />
    </form>
  );
};
