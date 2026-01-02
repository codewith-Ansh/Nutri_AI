// AI-native conversation utilities - no scores, no technical indicators


// Format AI response for natural conversation flow
export const formatAIResponse = (text: string): string => {
 let formatted = text;
  // Format reasoning sections with subtle visual hierarchy
 formatted = formatted.replace(
   /\*\*Why this matters:\*\*([^\n]+)/g,
   '<div class="mb-3 p-3 bg-blue-50 rounded-lg border-l-2 border-blue-300"><div class="text-sm font-medium text-blue-800 mb-1">Why this matters</div><div class="text-blue-700">$1</div></div>'
 );
  formatted = formatted.replace(
   /\*\*Trade-offs:\*\*([^\n]+)/g,
   '<div class="mb-3 p-3 bg-amber-50 rounded-lg border-l-2 border-amber-300"><div class="text-sm font-medium text-amber-800 mb-1">Trade-offs to consider</div><div class="text-amber-700">$1</div></div>'
 );
  formatted = formatted.replace(
   /\*\*Uncertainty:\*\*([^\n]+)/g,
   '<div class="mb-3 p-3 bg-gray-50 rounded-lg border-l-2 border-gray-300"><div class="text-sm font-medium text-gray-800 mb-1">Where I\'m uncertain</div><div class="text-gray-700">$1</div></div>'
 );
  // Clean up formatting
 formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-medium">$1</strong>');
 formatted = formatted.replace(/\n\s*\n/g, '<div class="my-2"></div>');
 formatted = formatted.replace(/\n/g, ' ');
  return formatted.trim();
};


// Generate natural follow-up questions based on conversation context
export const generateNaturalFollowUps = (aiResponse: string, conversationHistory: Array<{role: string, content: string}>): string[] => {
 const response = aiResponse.toLowerCase();
 const questions: string[] = [];
  // Context-aware follow-ups that feel conversational
 if (response.includes('child') || response.includes('kid')) {
   questions.push('Is this mainly for kids or adults?');
 }
  if (response.includes('occasional') || response.includes('regular')) {
   questions.push('How often would you have this?');
 }
  if (response.includes('uncertain') || response.includes('depends')) {
   questions.push('What matters most to you here?');
 }
  // Default gentle follow-ups
 if (questions.length === 0) {
   const defaults = [
     'Want me to focus on anything specific?',
     'Any particular concerns I should know about?'
   ];
   questions.push(defaults[Math.floor(Math.random() * defaults.length)]);
 }
  return questions.slice(0, 2); // Max 2 follow-ups
};
