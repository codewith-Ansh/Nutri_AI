import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatAIResponse } from "@/lib/aiUtils";
import { StructuredResponse } from "./StructuredResponse";

interface ChatMessageProps {
 role: "user" | "assistant";
 content: string;
 isStreaming?: boolean;
 structuredData?: {
   ingredients: string[];
   risk: {
     level: "Low" | "Moderate" | "High";
     description: string;
   };
   reasons: string[];
   alternatives?: string[];
   suggested_followup: string[];
 };
 onFollowUpClick?: (question: string) => void;
}


export const ChatMessage = ({ role, content, isStreaming, structuredData, onFollowUpClick }: ChatMessageProps) => {
 const isUser = role === "user";
  // AI-native formatting - no scores, no technical indicators
 const formattedContent = !isUser ? formatAIResponse(content) : content;


 const formatContent = (text: string) => {
   const paragraphs = text.split(/\n\n+/);
  
   return paragraphs.map((paragraph, i) => {
     // Simple paragraph formatting - no complex structures
     return (
       <p key={i} className="text-sm leading-relaxed mb-2 last:mb-0">
         {formatInlineText(paragraph)}
       </p>
     );
   });
 };


 const formatInlineText = (text: string) => {
   const parts = text.split(/(\*\*[^*]+\*\*)/g);
   return parts.map((part, i) => {
     if (part.startsWith('**') && part.endsWith('**')) {
       return (
         <strong key={i} className="font-medium text-gray-900">
           {part.slice(2, -2)}
         </strong>
       );
     }
     return part;
   });
 };


 return (
   <div className={cn(
     "flex gap-4 py-6",
     isUser ? "justify-end" : "justify-start"
   )}>
     {!isUser && (
       <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
         <Bot className="w-4 h-4 text-white" />
       </div>
     )}


     <div className={cn(
       "max-w-[75%]",
       isUser ? "order-first" : ""
     )}>
       <div className={cn(
         "rounded-2xl px-4 py-3",
         isUser
           ? "bg-emerald-600 text-white ml-auto"
           : "bg-gray-50 text-gray-900 border border-gray-100"
       )}>
         <div>
           {isUser ? (
             <p className="text-sm leading-relaxed">{content}</p>
           ) : (
             <div className="space-y-4">
               {/* Show structured response first if available */}
               {structuredData && (
                 <StructuredResponse 
                   data={structuredData} 
                   onFollowUpClick={onFollowUpClick}
                 />
               )}
               
               {/* Show narrative content if available */}
               {content && (
                 <div className="text-sm leading-relaxed space-y-2">
                   <div dangerouslySetInnerHTML={{ __html: formattedContent }} />
                 </div>
               )}
             </div>
           )}
         </div>
         {isStreaming && (
           <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
         )}
       </div>
     </div>
    
     {isUser && (
       <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
         <User className="w-4 h-4 text-white" />
       </div>
     )}
   </div>
 );
};
