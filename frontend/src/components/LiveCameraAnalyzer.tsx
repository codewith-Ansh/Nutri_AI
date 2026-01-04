import { useState, useRef, useEffect } from "react";
import { Camera, X, Loader2, Scan, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LiveCameraAnalyzerProps {
    onAnalysisComplete: (analysis: string) => void;
    onClose: () => void;
}

export const LiveCameraAnalyzer = ({ onAnalysisComplete, onClose }: LiveCameraAnalyzerProps) => {
    const [isStreaming, setIsStreaming] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [mode, setMode] = useState<'barcode' | 'product'>('product');
    const [error, setError] = useState<string | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        startCamera();
        return () => {
            stopCamera();
        };
    }, []);

    const startCamera = async () => {
        try {
            setError(null);

            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment', // Use back camera on mobile
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                }
            });

            streamRef.current = stream;

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.onloadedmetadata = () => {
                    videoRef.current?.play();
                    setIsStreaming(true);
                };
            }
        } catch (err) {
            console.error('Failed to start camera:', err);
            setError("Failed to access camera. Please check permissions.");
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setIsStreaming(false);
    };

    const captureAndAnalyze = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        setIsAnalyzing(true);

        try {
            // Capture current frame
            const canvas = canvasRef.current;
            const video = videoRef.current;

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext('2d');
            if (!ctx) return;

            ctx.drawImage(video, 0, 0);

            // Convert to blob
            const blob = await new Promise<Blob | null>((resolve) => {
                canvas.toBlob(resolve, 'image/jpeg', 0.95);
            });

            if (!blob) {
                throw new Error('Failed to capture image');
            }

            if (mode === 'barcode') {
                // Try to extract barcode first
                await analyzeBarcodeMode(blob);
            } else {
                // Analyze product directly
                await analyzeProductMode(blob);
            }

        } catch (err) {
            console.error('Analysis error:', err);
            onAnalysisComplete("I couldn't analyze the image. Please try again with better lighting.");
            stopCamera();
            onClose();
        } finally {
            setIsAnalyzing(false);
        }
    };

    const analyzeBarcodeMode = async (imageBlob: Blob) => {
        try {
            // First try ZXing barcode detection
            const { BrowserMultiFormatReader } = await import('@zxing/library');
            const reader = new BrowserMultiFormatReader();

            const imageUrl = URL.createObjectURL(imageBlob);
            const image = new Image();

            const barcodeDetected = await new Promise<string | null>((resolve) => {
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

            if (barcodeDetected) {
                // Fetch product from API
                const response = await fetch(
                    `${import.meta.env.VITE_API_BASE_URL}/api/product/${barcodeDetected}`
                );

                if (response.ok) {
                    const result = await response.json();
                    if (result.found) {
                        onAnalysisComplete(
                            `Found product: ${result.product_name} by ${result.brands}\n\nAnalyze the ingredients: ${result.ingredients.join(', ')}`
                        );
                    } else {
                        // No product in database, send to AI
                        await analyzeProductMode(imageBlob);
                    }
                } else {
                    await analyzeProductMode(imageBlob);
                }
            } else {
                // No barcode found, analyze as product
                await analyzeProductMode(imageBlob);
            }
        } catch (error) {
            console.error('Barcode mode error:', error);
            await analyzeProductMode(imageBlob);
        }

        stopCamera();
        onClose();
    };

    const analyzeProductMode = async (imageBlob: Blob) => {
        try {
            // Send to backend AI for analysis
            const formData = new FormData();
            formData.append('file', imageBlob, 'camera-capture.jpg');

            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL}/api/analyze/image`,
                {
                    method: 'POST',
                    body: formData
                }
            );

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const result = await response.json();

            if (result.success && result.analysis) {
                onAnalysisComplete(result.analysis);
            } else {
                onAnalysisComplete("I couldn't analyze this clearly. Please try taking another photo with better lighting.");
            }
        } catch (error) {
            console.error('Product analysis error:', error);
            onAnalysisComplete("I'm having trouble analyzing this. Please try again.");
        }

        stopCamera();
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full mx-4 overflow-hidden">
                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b bg-gradient-to-r from-emerald-50 to-blue-50">
                    <div className="flex items-center gap-2">
                        <Camera className="h-5 w-5 text-emerald-600" />
                        <h3 className="font-semibold text-gray-900">Live Camera Analysis</h3>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                            stopCamera();
                            onClose();
                        }}
                        className="h-8 w-8"
                    >
                        <X className="h-4 w-4" />
                    </Button>
                </div>

                {/* Mode Selector */}
                <div className="flex gap-2 p-3 bg-gray-50 border-b">
                    <Button
                        size="sm"
                        variant={mode === 'product' ? 'default' : 'outline'}
                        onClick={() => setMode('product')}
                        className={mode === 'product' ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
                    >
                        <Eye className="h-4 w-4 mr-2" />
                        Analyze Product
                    </Button>
                    <Button
                        size="sm"
                        variant={mode === 'barcode' ? 'default' : 'outline'}
                        onClick={() => setMode('barcode')}
                        className={mode === 'barcode' ? 'bg-purple-600 hover:bg-purple-700' : ''}
                    >
                        <Scan className="h-4 w-4 mr-2" />
                        Scan Barcode
                    </Button>
                </div>

                {/* Video Preview */}
                <div className="relative bg-gray-900">
                    <video
                        ref={videoRef}
                        className="w-full h-96 object-cover"
                        autoPlay
                        playsInline
                        muted
                    />

                    <canvas ref={canvasRef} className="hidden" />

                    {/* Overlay Guide */}
                    {isStreaming && !isAnalyzing && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div className="w-4/5 h-64 border-2 border-emerald-400 rounded-lg relative">
                                <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-60 text-white px-3 py-1 rounded-full text-sm">
                                    {mode === 'barcode' ? 'Position barcode in frame' : 'Show product label'}
                                </div>
                                <div className="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2 border-emerald-400" />
                                <div className="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2 border-emerald-400" />
                                <div className="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2 border-emerald-400" />
                                <div className="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2 border-emerald-400" />
                            </div>
                        </div>
                    )}

                    {/* Analyzing State */}
                    {isAnalyzing && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                            <div className="text-center text-white">
                                <Loader2 className="h-12 w-12 mx-auto mb-3 animate-spin text-emerald-400" />
                                <p className="font-semibold">Analyzing...</p>
                                <p className="text-sm text-gray-300 mt-1">
                                    {mode === 'barcode' ? 'Looking for barcode' : 'Reading ingredients'}
                                </p>
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

                {/* Controls */}
                <div className="p-4 bg-gray-50 space-y-3">
                    {/* Capture Button */}
                    <Button
                        onClick={captureAndAnalyze}
                        disabled={!isStreaming || isAnalyzing}
                        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white h-12 text-base font-medium"
                    >
                        {isAnalyzing ? (
                            <>
                                <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Camera className="h-5 w-5 mr-2" />
                                {mode === 'barcode' ? 'Scan Barcode' : 'Analyze Product'}
                            </>
                        )}
                    </Button>

                    {/* Instructions */}
                    <div className="text-xs text-gray-600 space-y-1">
                        <p className="flex items-start gap-2">
                            <span className="text-emerald-600">•</span>
                            <span>Point camera at the product label or barcode</span>
                        </p>
                        <p className="flex items-start gap-2">
                            <span className="text-emerald-600">•</span>
                            <span>Make sure the text is clear and well-lit</span>
                        </p>
                        <p className="flex items-start gap-2">
                            <span className="text-emerald-600">•</span>
                            <span>Click the button when ready to analyze</span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
