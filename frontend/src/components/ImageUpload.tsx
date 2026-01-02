import { useState, useRef } from "react";
import { Camera, Upload, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";


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
     // AI-native approach: Send image directly for visual context inference
     // No OCR extraction shown to user - AI infers context from visual cues
    
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
    
     // Let the AI provide context-aware response based on visual inference
     if (result.success && result.analysis) {
       onTextExtracted(result.analysis);
     } else {
       // Natural language fallback - no technical error messages
       onTextExtracted("I'm having trouble making out the details in this image. Could you try taking another photo with better lighting?");
     }
    
   } catch (error) {
     console.error('Image processing error:', error);
     // Natural, non-technical error message
     onTextExtracted("I couldn't analyze this image right now. Mind trying again?");
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
       className="h-10 w-10 rounded-xl"
       title="Upload photo"
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
       className="h-10 w-10 rounded-xl"
       title="Take photo"
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
       <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
         <div className="bg-white rounded-lg max-w-md w-full mx-4">
           <div className="flex justify-between items-center p-4 border-b">
             <h3 className="font-medium">Let me take a look...</h3>
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
               alt="Food product"
               className="w-full h-auto rounded-lg mb-4 max-h-[60vh] object-contain"
             />
             {isProcessing && (
               <div className="flex items-center justify-center gap-2 text-sm text-gray-600 py-2">
                 <Loader2 className="h-4 w-4 animate-spin" />
                 Analyzing...
               </div>
             )}
           </div>
         </div>
       </div>
     )}
   </div>
 );
};
