import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import type { Language } from "@/hooks/useLanguage";

const languages: Array<{ code: Language; label: string }> = [
  { code: "en" as const, label: "EN" },
  { code: "hi" as const, label: "हिंदी" },
  { code: "hinglish" as const, label: "Hinglish" },
  { code: "gu" as const, label: "ગુજરાતી" }
];

export const LanguageToggle = () => {
  const [currentLang, setCurrentLang] = useState<Language>("en");

  useEffect(() => {
    const saved = localStorage.getItem("nutri-language") as Language;
    if (saved && languages.find(l => l.code === saved)) {
      setCurrentLang(saved);
    }
  }, []);

  const handleLanguageChange = (lang: Language) => {
    setCurrentLang(lang);
    localStorage.setItem("nutri-language", lang);
    window.dispatchEvent(new CustomEvent("languageChange", { detail: lang }));
  };

  return (
    <div className="overflow-x-auto overflow-y-hidden max-w-full" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none', WebkitOverflowScrolling: 'touch' }}>
      <div className="flex items-center border border-border rounded-md whitespace-nowrap">
        {languages.map((lang) => (
          <Button
            key={lang.code}
            variant="ghost"
            size="sm"
            onClick={() => handleLanguageChange(lang.code)}
            className={`h-7 px-1.5 sm:px-2 text-xs rounded-none border-0 shrink-0 ${currentLang === lang.code
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
          >
            {lang.label}
          </Button>
        ))}
      </div>
    </div>
  );
};