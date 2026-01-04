import { Copy, Share2, Edit, Check, Volume2, VolumeX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { useState } from "react";

interface MessageActionsProps {
    content: string;
    structuredData?: any;
    role: "user" | "assistant";
    language?: string;
    messageId: string;
    onEdit?: () => void;
    onSpeak?: (messageId: string) => void;
    isSpeaking?: boolean;
}

export const MessageActions = ({ content, structuredData, role, language, messageId, onEdit, onSpeak, isSpeaking }: MessageActionsProps) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            // Extract clean text from structured data or use content
            let textToCopy = content;

            if (structuredData) {
                // Format structured data as readable text
                textToCopy = `${structuredData.quick_verdict}\n\n`;
                textToCopy += `Why this matters:\n${structuredData.why_this_matters.join('\n• ')}\n\n`;
                textToCopy += `Trade-offs:\n\n`;
                textToCopy += `Positives:\n${structuredData.trade_offs.positives.join('\n• ')}\n\n`;
                textToCopy += `Concerns:\n${structuredData.trade_offs.negatives.join('\n• ')}\n\n`;
                if (structuredData.uncertainty) {
                    textToCopy += `Note: ${structuredData.uncertainty}\n\n`;
                }
                textToCopy += `Advice: ${structuredData.ai_advice}`;
            }

            await navigator.clipboard.writeText(textToCopy);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);

            toast({
                title: "Copied to clipboard",
                duration: 2000,
            });
        } catch (error) {
            toast({
                title: "Failed to copy",
                variant: "destructive",
                duration: 2000,
            });
        }
    };

    const handleShare = async () => {
        try {
            let shareText = content;

            if (structuredData) {
                // Build comprehensive share text
                shareText = `NutriAI Analysis\n\n`;

                // Product title
                if (structuredData.ai_insight_title) {
                    shareText += `📦 ${structuredData.ai_insight_title}\n\n`;
                }

                // Quick verdict
                shareText += `${structuredData.quick_verdict}\n\n`;

                // Why this matters
                if (structuredData.why_this_matters && structuredData.why_this_matters.length > 0) {
                    shareText += ` Why This Matters:\n`;
                    structuredData.why_this_matters.forEach((point: string) => {
                        shareText += `• ${point}\n`;
                    });
                    shareText += `\n`;
                }

                // Trade-offs
                if (structuredData.trade_offs) {
                    // Positives
                    if (structuredData.trade_offs.positives && structuredData.trade_offs.positives.length > 0) {
                        shareText += `✓ Positives:\n`;
                        structuredData.trade_offs.positives.forEach((point: string) => {
                            shareText += `  • ${point}\n`;
                        });
                        shareText += `\n`;
                    }

                    // Concerns
                    if (structuredData.trade_offs.negatives && structuredData.trade_offs.negatives.length > 0) {
                        shareText += `⚠ Concerns:\n`;
                        structuredData.trade_offs.negatives.forEach((point: string) => {
                            shareText += `  • ${point}\n`;
                        });
                        shareText += `\n`;
                    }
                }

                // Advice
                if (structuredData.ai_advice) {
                    shareText += `💡 Advice: ${structuredData.ai_advice}\n`;
                }

                // Footer
                shareText += `\n---\nAnalyzed with NutriAI`;
            }

            if (navigator.share) {
                await navigator.share({
                    title: "NutriAI Analysis",
                    text: shareText,
                });
                toast({
                    title: "Shared successfully",
                    duration: 2000,
                });
            } else {
                // Fallback to copy
                await navigator.clipboard.writeText(shareText);
                toast({
                    title: "Copied for sharing",
                    description: "Share feature not available, text copied instead",
                    duration: 2000,
                });
            }
        } catch (error) {
            // User cancelled or error - silent fail is fine for share
            console.log("Share cancelled or failed");
        }
    };

    return (
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {role === "assistant" && (
                <>
                    {/* Speak Button */}
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-muted-foreground hover:text-foreground"
                        onClick={() => onSpeak?.(messageId)}
                        title={isSpeaking ? "Stop speaking" : "Speak"}
                        aria-label={isSpeaking ? "Stop speaking" : "Speak message"}
                    >
                        {isSpeaking ? <VolumeX className="h-3 w-3" /> : <Volume2 className="h-3 w-3" />}
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-muted-foreground hover:text-foreground"
                        onClick={handleCopy}
                        title="Copy"
                    >
                        {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-muted-foreground hover:text-foreground"
                        onClick={handleShare}
                        title="Share"
                    >
                        <Share2 className="h-3 w-3" />
                    </Button>
                </>
            )}
            {role === "user" && onEdit && (
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-muted-foreground hover:text-foreground"
                    onClick={onEdit}
                    title="Edit"
                >
                    <Edit className="h-3 w-3" />
                </Button>
            )}
        </div>
    );
};
