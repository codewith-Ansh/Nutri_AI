import { Bot } from "lucide-react";
import { SuggestionChips } from "./SuggestionChips";


interface WelcomeMessageProps {
  onSuggestionSelect: (suggestion: string) => void;
}


// AI-native suggestions - conversational, not technical
const SUGGESTIONS = [
  "Is this snack okay for my kid?",
  "I'm trying to eat healthier - thoughts?",
  "What should I know about this product?",
];


export const WelcomeMessage = ({ onSuggestionSelect }: WelcomeMessageProps) => {
  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-8 animate-fade-in max-w-2xl mx-auto">
      <div className="text-center space-y-4">
        <div className="bg-card p-4 rounded-2xl inline-block ring-1 ring-primary/20 shadow-glow mb-2">
          <img
            src="/assets/nutri-chat-logo.png"
            alt="NutriChat Logo"
            className="w-16 h-16 object-cover"
          />
        </div>
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-glow font-display">
          Welcome to NutriChat
        </h1>
        <p className="text-muted-foreground text-sm max-w-md mx-auto leading-relaxed">
          I'm your AI health co-pilot. Upload a photo of any food label,
          and I'll help you decide if it's right for you.
        </p>
      </div>

      <SuggestionChips suggestions={SUGGESTIONS} onSelect={onSuggestionSelect} />
    </div>
  );
};
