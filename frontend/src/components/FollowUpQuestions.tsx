import { MessageCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FollowUpQuestionsProps {
  aiResponse: string;
  conversationHistory: Array<{role: string, content: string}>;
  onQuestionSelect: (question: string) => void;
}

export const FollowUpQuestions = ({ aiResponse, conversationHistory, onQuestionSelect }: FollowUpQuestionsProps) => {
  
  const generateQuestions = (): string[] => {
    const questions: string[] = [];
    const response = aiResponse.toLowerCase();
    
    // Extract specific ingredients mentioned in the response
    const mentionedIngredients = [];
    if (response.includes('sodium')) mentionedIngredients.push('sodium');
    if (response.includes('sugar')) mentionedIngredients.push('sugar');
    if (response.includes('trans fat')) mentionedIngredients.push('trans fats');
    if (response.includes('preservative')) mentionedIngredients.push('preservatives');
    if (response.includes('msg')) mentionedIngredients.push('MSG');
    if (response.includes('palm oil')) mentionedIngredients.push('palm oil');
    if (response.includes('artificial')) mentionedIngredients.push('artificial additives');
    
    // Extract product name from response
    let productName = '';
    if (response.includes('maggi')) productName = 'Maggi';
    else if (response.includes('parle')) productName = 'Parle-G';
    else if (response.includes('britannia')) productName = 'Britannia';
    else if (response.includes('kurkure')) productName = 'Kurkure';
    else if (response.includes('lays')) productName = 'Lays';
    else if (response.includes('biscuit')) productName = 'biscuits';
    else if (response.includes('noodles')) productName = 'noodles';
    
    // Get health score from response
    const scoreMatch = response.match(/(\d+)\/100/);
    const score = scoreMatch ? parseInt(scoreMatch[1]) : 50;
    
    // Generate questions based on actual response content
    if (score < 30) {
      questions.push(`Why is ${productName || 'this product'} so unhealthy?`);
      questions.push("What are the healthiest alternatives?");
      questions.push("Should I completely avoid this?");
    } else if (score < 50) {
      questions.push(`How can I make ${productName || 'this'} healthier?`);
      questions.push("What's the biggest concern here?");
    } else if (score > 70) {
      questions.push(`What makes ${productName || 'this'} healthy?`);
      questions.push("Can I eat this every day?");
    }
    
    // Questions based on specific ingredients mentioned
    if (mentionedIngredients.includes('sodium')) {
      questions.push("How much sodium should I have daily?");
      questions.push("Show me low-sodium alternatives");
    }
    
    if (mentionedIngredients.includes('sugar')) {
      questions.push("How does sugar affect my health?");
      questions.push("What are sugar-free options?");
    }
    
    if (mentionedIngredients.includes('trans fats')) {
      questions.push("Why are trans fats dangerous?");
      questions.push("Which foods have trans fats?");
    }
    
    if (mentionedIngredients.includes('MSG')) {
      questions.push("Is MSG really harmful?");
      questions.push("What foods contain MSG?");
    }
    
    if (mentionedIngredients.includes('palm oil')) {
      questions.push("Why is palm oil controversial?");
      questions.push("What are healthier oil alternatives?");
    }
    
    // Product-specific questions
    if (productName === 'Maggi') {
      questions.push("Compare Maggi with Top Ramen");
      questions.push("Are homemade noodles better?");
    } else if (productName === 'Parle-G') {
      questions.push("Compare Parle-G with Marie Gold");
      questions.push("Which biscuits are healthiest?");
    } else if (productName.includes('biscuit')) {
      questions.push("Are digestive biscuits healthier?");
      questions.push("What's the healthiest snack?");
    }
    
    // If response mentions alternatives, ask about them
    if (response.includes('alternative')) {
      questions.push("Tell me more about these alternatives");
      questions.push("Where can I buy healthier options?");
    }
    
    // Always add one scanning question
    questions.push("Scan another product to compare");
    
    // Remove duplicates and return max 4 questions for side-by-side layout
    return [...new Set(questions)].slice(0, 4);
  };

  const questions = generateQuestions();
  
  if (questions.length === 0) return null;

  return (
    <div className="p-6 bg-gradient-to-br from-primary/15 via-primary/10 to-safe/15 rounded-2xl border-2 border-primary/40 shadow-xl">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-full bg-gradient-to-r from-primary to-safe flex items-center justify-center shadow-lg">
          <MessageCircle className="h-5 w-5 text-white" />
        </div>
        <div>
          <span className="text-lg font-bold text-primary">🤖 Quick Questions</span>
          <p className="text-sm text-muted-foreground">Smart suggestions</p>
        </div>
      </div>
      
      <div className="space-y-2">
        {questions.slice(0, 4).map((question, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onQuestionSelect(question)}
            className="justify-start text-left h-auto p-3 text-xs font-medium bg-white/80 hover:bg-primary/20 hover:text-primary hover:border-primary/60 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] shadow-sm hover:shadow-md w-full"
          >
            <ArrowRight className="h-3 w-3 mr-2 flex-shrink-0 text-primary" />
            <span className="truncate">{question}</span>
          </Button>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <span className="text-xs text-primary/80 font-medium">✨ Click to explore</span>
      </div>
    </div>
  );
};