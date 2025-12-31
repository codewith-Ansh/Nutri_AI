interface SuggestionChipsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}

export const SuggestionChips = ({ suggestions, onSelect }: SuggestionChipsProps) => {
  return (
    <div className="overflow-x-auto scrollbar-hide">
      <div className="flex gap-2 pb-2" style={{minWidth: 'max-content'}}>
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSelect(suggestion)}
            className="px-3 py-2 text-xs bg-emerald-50 border border-emerald-200 rounded-full hover:border-emerald-300 hover:shadow-sm transition-all duration-200 text-emerald-700 hover:text-emerald-800 whitespace-nowrap flex-shrink-0"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};
