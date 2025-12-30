import { Leaf, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  showTest: boolean;
  setShowTest: (show: boolean) => void;
}

export const Header = ({ showTest, setShowTest }: HeaderProps) => {
  return (
    <header className="sticky top-0 z-50 glass border-b border-border/50">
      <div className="container max-w-4xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-glow">
                <Leaf className="w-5 h-5 text-primary-foreground" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-safe rounded-full flex items-center justify-center">
                <Sparkles className="w-2.5 h-2.5 text-safe-foreground" />
              </div>
            </div>
            <div>
              <h1 className="font-display font-bold text-lg text-foreground">NutriChat</h1>
              <p className="text-xs text-muted-foreground">AI Ingredient Interpreter</p>
            </div>
          </div>

          {/* Health Score Button */}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setShowTest(!showTest)}
            className="text-xs font-medium"
          >
            HEALTH SCORE
          </Button>
        </div>
      </div>
    </header>
  );
};
