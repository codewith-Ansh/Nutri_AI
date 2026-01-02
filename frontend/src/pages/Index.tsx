import { ChatContainer } from "@/components/ChatContainer";
import { useState } from "react";
import { Leaf, Sparkles } from "lucide-react";


const Index = () => {
 return (
   <div className="flex flex-col h-screen bg-white">
     {/* Minimal Header */}
     <header className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
       <div className="flex items-center gap-3">
         <div className="relative">
           <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
             <Leaf className="w-4 h-4 text-white" />
           </div>
           <div className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-blue-500 rounded-full flex items-center justify-center">
             <Sparkles className="w-1.5 h-1.5 text-white" />
           </div>
         </div>
         <span className="text-lg font-medium text-gray-900">NutriChat</span>
       </div>
     </header>
    
     <main className="flex-1 overflow-hidden">
       <ChatContainer />
     </main>
   </div>
 );
};


export default Index;
