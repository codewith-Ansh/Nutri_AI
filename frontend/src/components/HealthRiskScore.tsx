import { AlertTriangle, CheckCircle, XCircle, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

interface HealthRiskScoreProps {
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

export const HealthRiskScore = ({ score, risks, positives, alternative }: HealthRiskScoreProps) => {
  const getRiskColor = (score: number) => {
    if (score >= 70) return "text-safe";
    if (score >= 40) return "text-caution";
    return "text-destructive";
  };

  const getRiskBg = (score: number) => {
    if (score >= 70) return "bg-safe";
    if (score >= 40) return "bg-caution";
    return "bg-destructive";
  };

  const getRiskIcon = (type: string) => {
    switch (type) {
      case 'high': return <XCircle className="h-4 w-4 text-destructive" />;
      case 'medium': return <AlertTriangle className="h-4 w-4 text-caution" />;
      case 'low': return <CheckCircle className="h-4 w-4 text-safe" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  return (
    <Card className="p-4 my-4 border-l-4 border-l-primary">
      {/* Health Score Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-full ${getRiskBg(score)} flex items-center justify-center`}>
            <span className="text-white font-bold text-lg">{score}</span>
          </div>
          <div>
            <h3 className="font-semibold text-lg">Health Score</h3>
            <p className={`text-sm font-medium ${getRiskColor(score)}`}>
              {score >= 70 ? 'Good Choice' : score >= 40 ? 'Moderate Risk' : 'High Risk'}
            </p>
          </div>
        </div>
        <TrendingUp className={`h-6 w-6 ${getRiskColor(score)}`} />
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <Progress value={score} className="h-2" />
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>0</span>
          <span>50</span>
          <span>100</span>
        </div>
      </div>

      {/* Risk Factors */}
      {risks.length > 0 && (
        <div className="mb-4">
          <h4 className="font-medium text-sm mb-2 text-muted-foreground">CONCERNS</h4>
          <div className="space-y-2">
            {risks.map((risk, index) => (
              <div key={index} className="flex items-start gap-2 text-sm">
                {getRiskIcon(risk.type)}
                <div className="flex-1">
                  <span className="font-medium">{risk.ingredient}</span>
                  {risk.value && <span className="text-muted-foreground"> ({risk.value})</span>}
                  <p className="text-muted-foreground text-xs">{risk.concern}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Positive Aspects */}
      {positives.length > 0 && (
        <div className="mb-4">
          <h4 className="font-medium text-sm mb-2 text-muted-foreground">GOOD POINTS</h4>
          <div className="space-y-2">
            {positives.map((positive, index) => (
              <div key={index} className="flex items-start gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-safe" />
                <div>
                  <span className="font-medium">{positive.ingredient}</span>
                  <p className="text-muted-foreground text-xs">{positive.benefit}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alternative Suggestion */}
      {alternative && (
        <div className="bg-primary/5 rounded-lg p-3 border border-primary/20">
          <div className="flex items-start gap-2">
            <TrendingUp className="h-4 w-4 text-primary mt-0.5" />
            <div>
              <p className="font-medium text-sm text-primary">Better Alternative</p>
              <p className="text-sm text-muted-foreground">{alternative}</p>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};