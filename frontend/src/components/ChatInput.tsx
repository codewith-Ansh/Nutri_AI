import { useState, useRef, useEffect } from "react";
import { Send, Camera, Upload, Scan, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { BarcodeScanner } from "./BarcodeScanner";
import { LiveCameraAnalyzer } from "./LiveCameraAnalyzer";
import { useLanguage } from "@/hooks/useLanguage";

interface ChatInputProps {
  onSend: (message: string) => void;
  onImageSelect?: (file: File) => void;
  onCameraAnalysis?: (analysis: string, capturedImage?: string) => void; // Updated to include captured image
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput = ({ onSend, onImageSelect, onCameraAnalysis, disabled, placeholder = "Message NutriChat..." }: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const [showBarcodeScanner, setShowBarcodeScanner] = useState(false);
  const [showLiveCamera, setShowLiveCamera] = useState(false);
  const [showManualBarcode, setShowManualBarcode] = useState(false);
  const [manualBarcode, setManualBarcode] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const language = useLanguage();

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

  const handleBarcodeDetected = async (barcode: string) => {
    console.log("Barcode detected:", barcode);

    try {
      // Call backend API with barcode
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/product/${barcode}`
      );

      if (!response.ok) {
        throw new Error('Product not found');
      }

      const result = await response.json();

      if (result.found) {
        const message = `Found product: ${result.product_name} by ${result.brands}\n\nAnalyze the ingredients: ${result.ingredients.join(', ')}`;
        onSend(message);
      } else {
        onSend(`Barcode ${barcode} detected but product not found in database. Let me help you analyze this product.`);
      }
    } catch (error) {
      console.error('Barcode lookup error:', error);
      onSend(`Barcode ${barcode} detected. Let me analyze this product...`);
    }
  };

  const handleManualBarcodeSubmit = () => {
    if (manualBarcode.trim() && /^\d{8,13}$/.test(manualBarcode.trim())) {
      handleBarcodeDetected(manualBarcode.trim());
      setManualBarcode("");
      setShowManualBarcode(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/') && onImageSelect) {
      onImageSelect(file);
    }
    e.target.value = '';
  };

  // Try to extract barcode from uploaded image using ZXing
  const tryExtractBarcodeFromImage = async (file: File): Promise<string | null> => {
    try {
      const { BrowserMultiFormatReader } = await import('@zxing/library');
      const reader = new BrowserMultiFormatReader();

      // Create image element
      const imageUrl = URL.createObjectURL(file);
      const image = new Image();

      return new Promise((resolve) => {
        image.onload = async () => {
          try {
            const result = await reader.decodeFromImageElement(image);
            URL.revokeObjectURL(imageUrl);
            resolve(result.getText());
          } catch {
            URL.revokeObjectURL(imageUrl);
            resolve(null);
          }
        };
        image.onerror = () => {
          URL.revokeObjectURL(imageUrl);
          resolve(null);
        };
        image.src = imageUrl;
      });
    } catch (error) {
      console.error('ZXing extraction failed:', error);
      return null;
    }
  };

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  // Listen for edit message event
  useEffect(() => {
    const handleEditMessage = (e: Event) => {
      const customEvent = e as CustomEvent;
      setMessage(customEvent.detail);
      textareaRef.current?.focus();
    };

    window.addEventListener("editMessage", handleEditMessage);
    return () => window.removeEventListener("editMessage", handleEditMessage);
  }, []);

  return (
    <>
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex flex-nowrap items-center gap-1.5 sm:gap-2 md:gap-3 p-2 sm:p-3 bg-card border border-border rounded-2xl shadow-sm focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20 transition-all">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={cn(
              "flex-1 resize-none bg-transparent text-foreground placeholder:text-muted-foreground focus:outline-none text-base leading-6",
              "max-h-[120px] min-h-[20px] py-1",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          />

          {/* Barcode Scanner Button */}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            disabled={disabled}
            onClick={() => setShowBarcodeScanner(true)}
            className="h-9 w-9 sm:h-10 sm:w-10 text-primary hover:text-primary/80 hover:bg-muted shrink-0"
            title="Scan barcode"
          >
            <Scan className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          </Button>

          {/* Image Upload Button */}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            disabled={disabled}
            onClick={() => fileInputRef.current?.click()}
            className="h-9 w-9 sm:h-10 sm:w-10 text-muted-foreground hover:text-foreground hover:bg-muted shrink-0"
            title="Upload image"
          >
            <Upload className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          </Button>

          {/* Live Camera Button */}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            disabled={disabled}
            onClick={() => setShowLiveCamera(true)}
            className="h-9 w-9 sm:h-10 sm:w-10 text-muted-foreground hover:text-foreground hover:bg-muted shrink-0"
            title="Open live camera"
          >
            <Camera className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          </Button>

          {/* Send Button */}
          <Button
            type="submit"
            size="icon"
            disabled={disabled || !message.trim()}
            className={cn(
              "h-9 w-9 sm:h-10 sm:w-10 rounded-xl shrink-0 transition-all",
              message.trim()
                ? "bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm"
                : "bg-muted text-muted-foreground cursor-not-allowed"
            )}
          >
            <Send className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          </Button>
        </div>

        {/* Manual Barcode Input Toggle */}
        <button
          type="button"
          onClick={() => setShowManualBarcode(!showManualBarcode)}
          className="text-xs text-muted-foreground hover:text-primary mt-2 flex items-center gap-1 transition-colors"
        >
          <Scan className="h-3 w-3" />
          {showManualBarcode ? "Hide" : "Enter barcode manually"}
        </button>

        {/* Manual Barcode Input Field */}
        {showManualBarcode && (
          <div className="mt-2 flex gap-2">
            <input
              type="text"
              value={manualBarcode}
              onChange={(e) => setManualBarcode(e.target.value.replace(/\D/g, ''))}
              onKeyDown={(e) => e.key === 'Enter' && handleManualBarcodeSubmit()}
              placeholder="Enter 8-13 digit barcode"
              maxLength={13}
              className="flex-1 px-3 py-2 text-sm border border-border bg-card text-foreground placeholder:text-muted-foreground rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
            <Button
              type="button"
              size="sm"
              onClick={handleManualBarcodeSubmit}
              disabled={!manualBarcode.trim() || !/^\d{8,13}$/.test(manualBarcode)}
              className="bg-primary hover:bg-primary/90"
            >
              Lookup
            </Button>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowManualBarcode(false);
                setManualBarcode("");
              }}
              className="text-muted-foreground hover:text-foreground hover:bg-muted"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
      </form>

      {/* Barcode Scanner Modal */}
      {showBarcodeScanner && (
        <BarcodeScanner
          onBarcodeDetected={handleBarcodeDetected}
          onClose={() => setShowBarcodeScanner(false)}
        />
      )}

      {/* Live Camera Analyzer Modal */}
      {showLiveCamera && (
        <LiveCameraAnalyzer
          onAnalysisComplete={(analysis, capturedImage) => {
            // Use camera-specific handler if available, otherwise fallback to onSend
            if (onCameraAnalysis) {
              onCameraAnalysis(analysis, capturedImage);
            } else {
              onSend(analysis);
            }
            setShowLiveCamera(false);
          }}
          onClose={() => setShowLiveCamera(false)}
          language={language}
        />
      )}
    </>
  );
};
