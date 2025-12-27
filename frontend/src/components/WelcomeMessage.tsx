import { Bot, Heart, AlertTriangle, Camera } from "lucide-react";
import { SuggestionChips } from "./SuggestionChips";

interface WelcomeMessageProps {
  onSuggestionSelect: (suggestion: string) => void;
}

const SUGGESTIONS = [
  "Tell me about Maggi noodles ingredients",
  "I'm diabetic, is Parle-G safe?",
  "What's maltodextrin and is it bad?",
  "Upload a photo of ingredient label",
];

export const WelcomeMessage = ({ onSuggestionSelect }: WelcomeMessageProps) => {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-8 fade-in">
      {/* Hero Icon */}
      <div className="relative mb-6">
        <div className="w-20 h-20 rounded-3xl bg-primary/10 flex items-center justify-center">
          <Bot className="w-10 h-10 text-primary" />
        </div>
        <div className="pulse-ring bg-primary/20" />
      </div>

      {/* Welcome Text */}
      <h2 className="font-display font-semibold text-2xl text-center text-foreground mb-2">
        Hi! I'm NutriChat
      </h2>
      <p className="text-muted-foreground text-center max-w-md mb-8">
        What food product are you curious about? You can describe it, paste ingredients, upload a photo, or tell me what you're concerned about.
      </p>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-lg mb-8 stagger-children">
        <div className="flex items-center gap-2 p-3 rounded-xl bg-card border border-border">
          <div className="w-8 h-8 rounded-lg bg-safe/10 flex items-center justify-center">
            <Camera className="w-4 h-4 text-safe" />
          </div>
          <span className="text-sm text-foreground">Scan labels</span>
        </div>
        <div className="flex items-center gap-2 p-3 rounded-xl bg-card border border-border">
          <div className="w-8 h-8 rounded-lg bg-chat-user/10 flex items-center justify-center">
            <Heart className="w-4 h-4 text-chat-user" />
          </div>
          <span className="text-sm text-foreground">Health insights</span>
        </div>
        <div className="flex items-center gap-2 p-3 rounded-xl bg-card border border-border">
          <div className="w-8 h-8 rounded-lg bg-caution/10 flex items-center justify-center">
            <AlertTriangle className="w-4 h-4 text-caution" />
          </div>
          <span className="text-sm text-foreground">Safety alerts</span>
        </div>
      </div>

      {/* Suggestions */}
      <div className="w-full max-w-lg">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3 text-center">
          Try asking
        </p>
        <SuggestionChips suggestions={SUGGESTIONS} onSelect={onSuggestionSelect} />
      </div>
    </div>
  );
};
