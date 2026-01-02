import { Bot } from "lucide-react";
import { SuggestionChips } from "./SuggestionChips";


interface WelcomeMessageProps {
 onSuggestionSelect: (suggestion: string) => void;
}


// AI-native suggestions - conversational, not technical
const SUGGESTIONS = [
 "Is this snack okay for my kid?",
 "I'm trying to eat healthier - thoughts on this?",
 "What should I know about this product?",
 "Help me understand these ingredients",
];


export const WelcomeMessage = ({ onSuggestionSelect }: WelcomeMessageProps) => {
 return (
   <div className="flex flex-col items-center justify-center h-full px-8">
     <div className="text-center mb-12">
       <div className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mx-auto mb-8 shadow-lg">
         <Bot className="w-8 h-8 text-white" />
       </div>
       <h1 className="text-4xl font-semibold text-gray-900 mb-4 tracking-tight">
         What are you deciding about?
       </h1>
       <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
         I'm here to help you think through food choices - just share what you're looking at or wondering about
       </p>
     </div>


     <div className="w-full max-w-4xl">
       <SuggestionChips suggestions={SUGGESTIONS} onSelect={onSuggestionSelect} />
     </div>
   </div>
 );
};
