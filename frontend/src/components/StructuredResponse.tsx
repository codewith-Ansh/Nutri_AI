import React from "react";
import { CheckCircle, AlertTriangle, Info, Lightbulb, TrendingUp, TrendingDown } from "lucide-react";

interface StructuredInsight {
  ai_insight_title: string;
  quick_verdict: string;
  why_this_matters: string[];
  trade_offs: {
    positives: string[];
    negatives: string[];
  };
  uncertainty: string;
  ai_advice: string;
}

interface StructuredResponseProps {
  data: StructuredInsight;
}

export const StructuredResponse = ({ data }: StructuredResponseProps) => {
  return (
    <div className="space-y-3 text-sm">
      {/* Title - Compact with subtle green tint */}
      <div className="bg-primary/5 dark:bg-card border-none dark:border-l-2 dark:border-primary rounded-lg px-3 py-2 shadow-sm dark:shadow-none">
        <p className="font-medium text-foreground text-sm">{data.ai_insight_title}</p>
      </div>

      {/* Quick Verdict - Inline with green icon */}
      <div className="flex items-start gap-2 px-3 py-2 bg-primary/5 dark:bg-card rounded-lg border-none dark:border dark:border-border shadow-sm dark:shadow-none">
        <CheckCircle className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
        <p className="text-sm text-foreground">{data.quick_verdict}</p>
      </div>

      {/* Why This Matters - Light Yellow/Caution tint */}
      <div className="px-3 py-2 bg-caution/5 dark:bg-card rounded-lg border-none dark:border dark:border-border shadow-sm dark:shadow-none">
        <div className="flex items-center gap-2 mb-1.5">
          <Info className="h-3.5 w-3.5 text-caution dark:text-primary" />
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Why this matters</p>
        </div>
        <ul className="space-y-1 ml-5">
          {data.why_this_matters.map((matter, index) => (
            <li key={index} className="text-xs text-foreground flex items-start gap-1.5">
              <span className="text-caution dark:text-primary text-xs font-bold">•</span>
              <span>{matter}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Trade-offs - Two Columns with colored icons only */}
      <div className="grid md:grid-cols-2 gap-2">
        {/* Positives - Green tint */}
        <div className="px-3 py-2 bg-primary/5 dark:bg-card rounded-lg border-none dark:border dark:border-border shadow-sm dark:shadow-none">
          <div className="flex items-center gap-1.5 mb-1.5">
            <TrendingUp className="h-3.5 w-3.5 text-primary" />
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Positives</p>
          </div>
          <ul className="space-y-1">
            {data.trade_offs.positives.map((positive, index) => (
              <li key={index} className="text-xs text-foreground flex items-start gap-1.5">
                <span className="text-primary text-xs">✓</span>
                <span>{positive}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Concerns - Pink/Red tint */}
        <div className="px-3 py-2 bg-destructive/5 dark:bg-card rounded-lg border-none dark:border dark:border-border shadow-sm dark:shadow-none">
          <div className="flex items-center gap-1.5 mb-1.5">
            <TrendingDown className="h-3.5 w-3.5 text-destructive dark:text-caution" />
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Concerns</p>
          </div>
          <ul className="space-y-1">
            {data.trade_offs.negatives.map((negative, index) => (
              <li key={index} className="text-xs text-foreground flex items-start gap-1.5">
                <span className="text-destructive dark:text-caution text-xs">!</span>
                <span>{negative}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Uncertainty - Lavender/Purple tint */}
      {data.uncertainty && (
        <div className="flex items-start gap-2 px-3 py-2 bg-purple-500/5 dark:bg-card rounded-lg border-none dark:border dark:border-border/50 shadow-sm dark:shadow-none">
          <AlertTriangle className="h-3.5 w-3.5 text-purple-500 dark:text-purple-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-0.5">Keep in mind</p>
            <p className="text-xs text-muted-foreground italic">{data.uncertainty}</p>
          </div>
        </div>
      )}

      {/* AI Advice - Green tint */}
      <div className="flex items-start gap-2 px-3 py-2 bg-primary/5 dark:bg-card rounded-lg border-none dark:border-l-2 dark:border-primary shadow-sm dark:shadow-none">
        <Lightbulb className="h-3.5 w-3.5 text-primary mt-0.5 flex-shrink-0" />
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-0.5">Our advice</p>
          <p className="text-sm text-foreground">{data.ai_advice}</p>
        </div>
      </div>
    </div>
  );
};