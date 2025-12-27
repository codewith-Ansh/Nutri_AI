import { useState, useRef } from "react";
import { Camera, Upload, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import Tesseract from "tesseract.js";
import { BrowserMultiFormatReader } from '@zxing/library';
import { indianProducts } from '@/data/indianProducts';

interface ImageUploadProps {
  onTextExtracted: (text: string) => void;
  disabled?: boolean;
}

export const ImageUpload = ({ onTextExtracted, disabled }: ImageUploadProps) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const processImage = async (file: File) => {
    setIsProcessing(true);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewImage(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    try {
      // First try barcode scanning with ZXing
      const codeReader = new BrowserMultiFormatReader();
      
      try {
        const imageUrl = URL.createObjectURL(file);
        const result = await codeReader.decodeFromImageUrl(imageUrl);
        const barcode = result.getText();
        console.log('ZXing found barcode:', barcode);
        
        // Lookup product using OpenFoodFacts API
        const response = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
        const data = await response.json();
        
        if (data.status === 1 && data.product) {
          const product = data.product;
          const productName = product.product_name || 'Unknown Product';
          const ingredients = product.ingredients_text || 'Ingredients not available';
          
          onTextExtracted(`Found product: **${productName}**\n\nIngredients: ${ingredients}`);
          return;
        } else {
          // Check fallback Indian products database
          const fallbackProduct = indianProducts[barcode];
          if (fallbackProduct) {
            onTextExtracted(`Found product: **${fallbackProduct.name}**\n\nIngredients: ${fallbackProduct.ingredients}`);
            return;
          }
          
          // If not in fallback either, use generic analysis
          const genericProduct = indianProducts['unknown'];
          onTextExtracted(`Found product: **${genericProduct.name}**\n\nThis appears to be a local Indian product. Based on common Indian packaged foods, here's a typical analysis:\n\nIngredients: Refined wheat flour, vegetable oil, salt, sugar, preservatives, artificial flavors, colors. Most packaged Indian snacks contain high sodium, refined flour, and palm oil.`);
          return;
        }
      } catch (barcodeError) {
        console.log('ZXing failed, trying OCR fallback...');
      }
      
      // Fallback: Try OCR and check if it's a barcode number
      const { data: { text } } = await Tesseract.recognize(file, 'eng');
      console.log('OCR detected text:', text);
      
      // Check if OCR found a barcode (8-14 digits)
      const barcodeMatch = text.match(/\b\d{8,14}\b/);
      
      if (barcodeMatch) {
        const barcode = barcodeMatch[0];
        console.log('OCR found barcode:', barcode);
        
        try {
          // Try to lookup the barcode
          const response = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
          const data = await response.json();
          
          if (data.status === 1 && data.product) {
            const product = data.product;
            const productName = product.product_name || 'Unknown Product';
            const ingredients = product.ingredients_text || 'Ingredients not available';
            
            onTextExtracted(`Found product: **${productName}**\n\nIngredients: ${ingredients}`);
            return;
          } else {
            // Check fallback database
            const fallbackProduct = indianProducts[barcode];
            if (fallbackProduct) {
              onTextExtracted(`Found product: **${fallbackProduct.name}**\n\nIngredients: ${fallbackProduct.ingredients}`);
              return;
            }
            
            // Generic analysis for unknown products
            onTextExtracted(`Found product: **Unknown Indian Packaged Food**\n\nIngredients: Based on typical Indian packaged foods - Refined wheat flour, vegetable oil (palm oil), salt, sugar, preservatives (sodium benzoate), artificial flavors, colors. Most contain high sodium and refined ingredients.`);
            return;
          }
        } catch (error) {
          onTextExtracted(`I found barcode ${barcode} but couldn't look it up. Please try photographing the ingredient list on the package instead.`);
          return;
        }
      }
      
      // If not a barcode, treat as regular ingredient text
      const cleanedText = text
        .replace(/[^a-zA-Z0-9\s.,()%-]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
      
      if (cleanedText && cleanedText.length > 5) {
        onTextExtracted(`Analyze these ingredients: "${cleanedText}"`);
      } else {
        onTextExtracted("I couldn't read clear text from this image. Please try photographing the ingredient list with better lighting and focus.");
      }
    } catch (error) {
      console.error('Processing error:', error);
      onTextExtracted("Sorry, couldn't process the image. Please try again with a clearer photo.");
    } finally {
      setIsProcessing(false);
      setPreviewImage(null);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      processImage(file);
    }
    // Reset input
    e.target.value = '';
  };

  const clearPreview = () => {
    setPreviewImage(null);
    setIsProcessing(false);
  };

  return (
    <div className="flex gap-2">
      {/* Upload from Gallery */}
      <Button
        type="button"
        variant="outline"
        size="icon"
        disabled={disabled || isProcessing}
        onClick={() => fileInputRef.current?.click()}
        className="h-10 w-10 rounded-xl image-upload-button"
        title="Upload ingredient label photo"
      >
        {isProcessing ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Upload className="h-4 w-4" />
        )}
      </Button>

      {/* Take Photo */}
      <Button
        type="button"
        variant="outline"
        size="icon"
        disabled={disabled || isProcessing}
        onClick={() => cameraInputRef.current?.click()}
        className="h-10 w-10 rounded-xl image-upload-button"
        title="Take photo of ingredient label"
      >
        <Camera className="h-4 w-4" />
      </Button>

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

      {/* Preview Modal */}
      {previewImage && (
        <div className="image-preview-modal">
          <div className="image-preview-content">
            <div className="flex justify-between items-center p-4 border-b border-border">
              <h3 className="font-semibold text-foreground">Processing Image...</h3>
              <Button
                variant="ghost"
                size="icon"
                onClick={clearPreview}
                disabled={isProcessing}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4">
              <img
                src={previewImage}
                alt="Ingredient label"
                className="w-full h-auto rounded-lg mb-4 max-h-[60vh] object-contain"
              />
              {isProcessing && (
                <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground py-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Extracting text from image...
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};