// Utility functions for parsing AI responses and extracting structured data

export interface HealthScore {
  score: number;
  risks: Array<{
    type: 'high' | 'medium' | 'low';
    ingredient: string;
    concern: string;
    value?: string;
  }>;
  positives: Array<{
    ingredient: string;
    benefit: string;
  }>;
  alternative?: string;
}

export interface ConversationPattern {
  type: 'concern' | 'preference' | 'improvement';
  title: string;
  description: string;
  products: string[];
  suggestion: string;
  confidence: number;
}

// Extract health score - disabled since formatting handles display
export const extractHealthScore = (text: string): HealthScore | null => {
  return null; // Let the formatted display handle everything
};

// Format AI response text with proper visual formatting
export const formatAIResponse = (text: string): string => {
  let formatted = text;
  
  // Format health score header with prominent styling
  formatted = formatted.replace(
    /HEALTH RISK SCORE: (\d+\/100)/g, 
    '<div class="text-xl font-bold text-white bg-gradient-to-r from-primary to-safe p-4 rounded-lg text-center mb-4 shadow-lg">🏥 HEALTH RISK SCORE: $1</div>'
  );
  
  // Format warning bullet points with red styling
  formatted = formatted.replace(
    /^\s*•\s*⚠\s*\\([^]+)\\\s-\s*([^\n]+)/gm,
    '<div class="flex items-start gap-3 mb-3 p-3 bg-red-50 rounded-lg border-l-4 border-red-400"><span class="text-red-500 text-xl">⚠</span><div><strong class="text-red-700 font-semibold">$1</strong><br><span class="text-red-600 text-sm">$2</span></div></div>'
  );
  
  // Format positive bullet points with green styling
  formatted = formatted.replace(
    /^\s*•\s*✅\s*\\([^]+)\\\s-\s*([^\n]+)/gm,
    '<div class="flex items-start gap-3 mb-3 p-3 bg-green-50 rounded-lg border-l-4 border-green-400"><span class="text-green-500 text-xl">✅</span><div><strong class="text-green-700 font-semibold">$1</strong><br><span class="text-green-600 text-sm">$2</span></div></div>'
  );
  
  // Format better choice section with blue styling
  formatted = formatted.replace(
    /\\*Better Choice:\\\s([^\n]+)/g,
    '<div class="mt-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400"><div class="flex items-center gap-2 mb-2"><span class="text-blue-500 text-xl">💡</span><strong class="text-blue-700 font-semibold">Better Choice</strong></div><span class="text-blue-600">$1</span></div>'
  );
  
  // Clean up any remaining bold formatting
  formatted = formatted.replace(/\\([^]+)\\*/g, '<strong class="font-semibold">$1</strong>');
  
  // Handle line breaks properly
  formatted = formatted.replace(/\n\s*\n/g, '<div class="my-2"></div>');
  formatted = formatted.replace(/\n/g, ' ');
  
  return formatted.trim();
};

// Detect conversation patterns
export const detectPatterns = (messages: Array<{role: string, content: string}>): ConversationPattern | null => {
  const userMessages = messages.filter(m => m.role === 'user').map(m => m.content.toLowerCase());
  
  if (userMessages.length < 2) return null;

  // Detect high sodium concern pattern
  const sodiumProducts = ['maggi', 'kurkure', 'lays', 'chips', 'noodles'];
  const sodiumMentions = userMessages.filter(msg => 
    sodiumProducts.some(product => msg.includes(product))
  );

  if (sodiumMentions.length >= 2) {
    return {
      type: 'concern',
      title: 'High Sodium Pattern Detected',
      description: `You've asked about ${sodiumMentions.length} high-sodium products recently.`,
      products: sodiumProducts.filter(p => userMessages.some(msg => msg.includes(p))),
      suggestion: 'Try low-sodium alternatives like roasted nuts, fruits, or homemade snacks.',
      confidence: 85
    };
  }

  // Detect diabetes concern pattern
  const diabeticKeywords = ['diabetic', 'diabetes', 'sugar', 'blood sugar'];
  const diabeticMentions = userMessages.filter(msg =>
    diabeticKeywords.some(keyword => msg.includes(keyword))
  );

  if (diabeticMentions.length >= 2) {
    return {
      type: 'concern',
      title: 'Diabetes Management Focus',
      description: 'You seem focused on diabetes-friendly food choices.',
      products: [],
      suggestion: 'Look for products with low glycemic index and no added sugars.',
      confidence: 90
    };
  }

  return null;
};