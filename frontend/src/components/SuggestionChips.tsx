interface SuggestionChipsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}

export const SuggestionChips = ({ suggestions, onSelect }: SuggestionChipsProps) => {
  // Show only first 3 suggestions for cleaner layout
  const displaySuggestions = suggestions.slice(0, 3);

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full">
        {displaySuggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSelect(suggestion)}
            className="group px-4 py-3 bg-card border border-border rounded-xl hover:border-primary/50 hover:bg-muted transition-all duration-300 flex items-center justify-center text-center shadow-sm hover:shadow-primary/10 hover:shadow-lg"
          >
            <span className="text-sm text-foreground/80 group-hover:text-primary font-medium leading-relaxed">
              {suggestion}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};
