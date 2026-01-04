import { useState, useRef, useEffect } from "react";
import { BrowserMultiFormatReader } from "@zxing/library";
import { Camera, X, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface BarcodeScannerProps {
  onBarcodeDetected: (barcode: string) => void;
  onClose: () => void;
}

export const BarcodeScanner = ({ onBarcodeDetected, onClose }: BarcodeScannerProps) => {
  const [isScanning, setIsScanning] = useState(false);
  const [detectedBarcode, setDetectedBarcode] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const readerRef = useRef<BrowserMultiFormatReader | null>(null);

  useEffect(() => {
    startScanning();
    return () => {
      stopScanning();
    };
  }, []);

  const startScanning = async () => {
    try {
      setIsScanning(true);
      setError(null);

      // Initialize ZXing reader
      const reader = new BrowserMultiFormatReader();
      readerRef.current = reader;

      // Get available video devices
      const videoDevices = await reader.listVideoInputDevices();
      
      if (videoDevices.length === 0) {
        setError("No camera found on this device");
        setIsScanning(false);
        return;
      }

      // Use back camera if available (for mobile)
      const backCamera = videoDevices.find(device => 
        device.label.toLowerCase().includes('back')
      ) || videoDevices[0];

      // Start decoding from video device
      if (videoRef.current) {
        reader.decodeFromVideoDevice(
          backCamera.deviceId,
          videoRef.current,
          (result, error) => {
            if (result) {
              const barcode = result.getText();
              setDetectedBarcode(barcode);
              setIsScanning(false);
              
              // Notify parent and close after short delay
              setTimeout(() => {
                onBarcodeDetected(barcode);
                stopScanning();
                onClose();
              }, 1000);
            }
            
            if (error && !(error.name === 'NotFoundException')) {
              console.error('Barcode scan error:', error);
            }
          }
        );
      }
    } catch (err) {
      console.error('Failed to start camera:', err);
      setError("Failed to access camera. Please check permissions.");
      setIsScanning(false);
    }
  };

  const stopScanning = () => {
    if (readerRef.current) {
      readerRef.current.reset();
      readerRef.current = null;
    }
    setIsScanning(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b bg-gradient-to-r from-emerald-50 to-blue-50">
          <div className="flex items-center gap-2">
            <Camera className="h-5 w-5 text-emerald-600" />
            <h3 className="font-semibold text-gray-900">Scan Barcode</h3>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              stopScanning();
              onClose();
            }}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Video Preview */}
        <div className="relative bg-gray-900">
          <video
            ref={videoRef}
            className="w-full h-64 object-cover"
            autoPlay
            playsInline
          />
          
          {/* Scanning Overlay */}
          {isScanning && !detectedBarcode && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-4/5 h-32 border-2 border-emerald-500 rounded-lg relative">
                <div className="absolute inset-x-0 top-1/2 h-0.5 bg-emerald-500 animate-pulse" />
                <p className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-white text-sm">
                  Position barcode within frame
                </p>
              </div>
            </div>
          )}

          {/* Success State */}
          {detectedBarcode && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <div className="text-center text-white">
                <CheckCircle className="h-16 w-16 mx-auto mb-2 text-emerald-400" />
                <p className="font-semibold">Barcode Detected!</p>
                <p className="text-sm text-gray-300 mt-1">{detectedBarcode}</p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-75">
              <div className="text-center text-white px-4">
                <p className="font-semibold mb-2">Camera Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="p-4 bg-gray-50">
          <div className="flex items-start gap-2 text-sm text-gray-600">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5" />
            <p>Hold your camera steady over the barcode until it's detected automatically</p>
          </div>
        </div>
      </div>
    </div>
  );
};
