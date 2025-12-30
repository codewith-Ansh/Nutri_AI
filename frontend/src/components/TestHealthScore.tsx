import { HealthRiskScore } from "./HealthRiskScore";

// Test component to verify health scoring works
export const TestHealthScore = () => {
  const testScore = {
    score: 25,
    risks: [
      {
        type: 'high' as const,
        ingredient: 'High Sodium',
        value: '820mg',
        concern: '55% of daily limit for adults'
      },
      {
        type: 'high' as const,
        ingredient: 'Trans Fats',
        value: '2g',
        concern: 'Linked to heart disease'
      },
      {
        type: 'medium' as const,
        ingredient: 'TBHQ Preservative',
        concern: 'Some studies suggest concerns'
      }
    ],
    positives: [
      {
        ingredient: 'Good Protein',
        benefit: 'Helps with satiety (8g)'
      }
    ],
    alternative: 'Try whole wheat noodles with 60% less sodium'
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4">HEALTH SCORE</h2>
      <HealthRiskScore
        score={testScore.score}
        risks={testScore.risks}
        positives={testScore.positives}
        alternative={testScore.alternative}
      />
    </div>
  );
};