import { Brain, TrendingUp, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PatternInsightProps {
  pattern: {
    type: 'concern' | 'preference' | 'improvement';
    title: string;
    description: string;
    products: string[];
    suggestion: string;
    confidence: number;
  };
}

export const PatternInsight = ({ pattern }: PatternInsightProps) => {
  const getPatternIcon = (type: string) => {
    switch (type) {
      case 'concern': return <AlertCircle className="h-5 w-5 text-caution" />;
      case 'improvement': return <TrendingUp className="h-5 w-5 text-safe" />;
      default: return <Brain className="h-5 w-5 text-primary" />;
    }
  };

  const getPatternColor = (type: string) => {
    switch (type) {
      case 'concern': return 'border-l-caution bg-caution/5';
      case 'improvement': return 'border-l-safe bg-safe/5';
      default: return 'border-l-primary bg-primary/5';
    }
  };

  return (
    <Card className={`p-4 my-4 border-l-4 ${getPatternColor(pattern.type)}`}>
      <div className="flex items-start gap-3">
        {getPatternIcon(pattern.type)}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-sm">AI Pattern Detected</h3>
            <Badge variant="secondary" className="text-xs">
              {pattern.confidence}% confident
            </Badge>
          </div>
          
          <h4 className="font-medium mb-2">{pattern.title}</h4>
          <p className="text-sm text-muted-foreground mb-3">{pattern.description}</p>
          
          {pattern.products.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-muted-foreground mb-1">PRODUCTS ANALYZED:</p>
              <div className="flex flex-wrap gap-1">
                {pattern.products.map((product, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {product}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          
          <div className="bg-card rounded-lg p-3 border">
            <p className="text-sm font-medium text-primary mb-1">💡 AI Suggestion</p>
            <p className="text-sm text-muted-foreground">{pattern.suggestion}</p>
          </div>
        </div>
      </div>
    </Card>
  );
};