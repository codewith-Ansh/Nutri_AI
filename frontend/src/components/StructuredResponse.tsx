import { AlertTriangle, CheckCircle, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface StructuredResponseProps {
  data: {
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

export const StructuredResponse = ({ data, onFollowUpClick }: StructuredResponseProps) => {
  const [showAlternatives, setShowAlternatives] = useState(false);
  
  const getRiskIcon = (level: string) => {
    switch (level) {
      case "Low":
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "Moderate":
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case "High":
        return <XCircle className="w-4 h-4 text-red-600" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-600" />;
    }
  };
  
  const getRiskColor = (level: string) => {
    switch (level) {
      case "Low":
        return "bg-green-50 border-green-200";
      case "Moderate":
        return "bg-yellow-50 border-yellow-200";
      case "High":
        return "bg-red-50 border-red-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="w-full max-w-6xl">
      {/* Main Cards - 2x2 Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Ingredients Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 h-36 overflow-hidden">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <h3 className="font-medium text-base text-gray-900">Ingredients</h3>
          </div>
          <div className="flex flex-wrap gap-2 h-24 overflow-hidden">
            {data.ingredients.slice(0, 4).map((ingredient, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm"
              >
                {ingredient.length > 20 ? ingredient.substring(0, 20) + '...' : ingredient}
              </span>
            ))}
            {data.ingredients.length > 4 && (
              <span className="text-sm text-gray-500">+{data.ingredients.length - 4} more</span>
            )}
          </div>
        </div>

        {/* Risk Card */}
        <div className={cn(
          "rounded-lg border p-4 h-36 overflow-hidden",
          getRiskColor(data.risk.level)
        )}>
          <div className="flex items-center gap-2 mb-3">
            {getRiskIcon(data.risk.level)}
            <h3 className="font-medium text-base">
              {data.risk.level} Risk
            </h3>
          </div>
          <div className="h-24 overflow-hidden">
            <p className="text-sm leading-relaxed">
              {data.risk.description.length > 120 ? data.risk.description.substring(0, 120) + '...' : data.risk.description}
            </p>
          </div>
        </div>

        {/* Reasons Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 h-36 overflow-hidden">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <h3 className="font-medium text-base text-gray-900">Key Points</h3>
          </div>
          <div className="h-24 overflow-hidden">
            <ul className="space-y-2">
              {data.reasons.slice(0, 3).map((reason, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 bg-purple-400 rounded-full mt-2 flex-shrink-0"></span>
                  <span className="text-sm text-gray-700 leading-relaxed">
                    {reason.length > 60 ? reason.substring(0, 60) + '...' : reason}
                  </span>
                </li>
              ))}
              {data.reasons.length > 3 && (
                <li className="text-sm text-gray-500">+{data.reasons.length - 3} more points</li>
              )}
            </ul>
          </div>
        </div>

        {/* Alternatives Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 h-36 overflow-hidden">
          <button
            onClick={() => setShowAlternatives(!showAlternatives)}
            className="w-full flex items-center justify-between text-left mb-3"
          >
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></div>
              <h3 className="font-medium text-base text-gray-900">Alternatives</h3>
            </div>
            {showAlternatives ? (
              <ChevronUp className="w-4 h-4 text-gray-500 flex-shrink-0" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500 flex-shrink-0" />
            )}
          </button>
          
          <div className="h-24 overflow-hidden">
            {data.alternatives && data.alternatives.length > 0 ? (
              showAlternatives ? (
                <div className="space-y-2">
                  {data.alternatives.slice(0, 3).map((alternative, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-green-400 rounded-full mt-2 flex-shrink-0"></span>
                      <span className="text-sm text-gray-700 leading-relaxed">
                        {alternative.length > 50 ? alternative.substring(0, 50) + '...' : alternative}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  {data.alternatives.length} option{data.alternatives.length > 1 ? 's' : ''} available - click to view
                </p>
              )
            ) : (
              <p className="text-sm text-gray-500">No alternatives suggested</p>
            )}
          </div>
        </div>
      </div>

      {/* Follow-up Questions */}
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-3">
        <h3 className="font-medium text-sm text-gray-900 mb-2">Quick Questions</h3>
        <div className="flex flex-wrap gap-2">
          {data.suggested_followup.map((question, index) => (
            <button
              key={index}
              onClick={() => onFollowUpClick?.(question)}
              className="px-3 py-1.5 bg-white border border-gray-300 rounded-full text-xs text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-colors"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};