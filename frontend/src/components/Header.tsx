import { Share2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";

interface HeaderProps {
  onClearChat?: () => void;
  onShare?: () => void;
}

export const Header = ({ onClearChat, onShare }: HeaderProps) => {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm transition-colors duration-300">
      <div className="mx-auto max-w-5xl px-3 sm:px-4 h-14 flex items-center justify-between">
        {/* Logo - Full color */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          <div className="relative w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-card ring-1 ring-primary/20 flex items-center justify-center overflow-hidden">
            <img
              src="/assets/nutri-chat-logo.png"
              alt="NutriChat Logo"
              className="w-5 h-5 sm:w-6 sm:h-6 object-cover"
            />
          </div>
          <span className="text-sm sm:text-base font-semibold text-foreground tracking-tight">NutriChat</span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          <LanguageToggle />
          <ThemeToggle />

          {onShare && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onShare}
              className="h-10 w-10 sm:h-8 sm:w-8 p-0 text-muted-foreground hover:text-primary hover:bg-muted"
            >
              <Share2 className="h-4 w-4" />
            </Button>
          )}
          {onClearChat && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearChat}
              className="h-10 w-10 sm:h-8 sm:w-8 p-0 text-muted-foreground hover:text-destructive hover:bg-muted"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};
