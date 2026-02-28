import { NavLink } from "@/components/NavLink";
import { Brain, PenTool, BarChart3, Grid3X3, Zap, Menu, X, Sparkles } from "lucide-react";
import { useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";

const navItems = [
  { title: "Draw & Predict", url: "/", icon: PenTool },
  { title: "Model Training", url: "/training", icon: Brain },
  { title: "Evaluation", url: "/evaluation", icon: BarChart3 },
  { title: "Sample Gallery", url: "/gallery", icon: Grid3X3 },
];

export function AppSidebar() {
  const isMobile = useIsMobile();
  const [open, setOpen] = useState(false);

  if (isMobile) {
    return (
      <>
        <header className="fixed top-0 left-0 right-0 z-50 glass-panel rounded-none border-b border-border/50 flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center">
              <Zap className="w-4 h-4 text-primary" />
            </div>
            <span className="text-sm font-bold text-foreground tracking-tight">DigitVision</span>
          </div>
          <button onClick={() => setOpen(!open)} className="text-foreground p-1.5 rounded-xl hover:bg-muted transition-colors">
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </header>

        {open && (
          <div className="fixed inset-0 z-40 pt-14">
            <div className="absolute inset-0 bg-background/60 backdrop-blur-sm" onClick={() => setOpen(false)} />
            <nav className="relative glass-panel m-3 mt-1 p-3 flex flex-col gap-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.url}
                  to={item.url}
                  end={item.url === "/"}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-muted-foreground hover:text-foreground hover:bg-primary/5 transition-all duration-200"
                  activeClassName="bg-primary/10 text-primary font-semibold"
                  onClick={() => setOpen(false)}
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.title}</span>
                </NavLink>
              ))}
            </nav>
          </div>
        )}
        <div className="h-14" />
      </>
    );
  }

  return (
    <aside className="w-[260px] min-h-screen bg-card/80 backdrop-blur-xl border-r border-border/50 flex flex-col p-5 gap-2 shrink-0">
      <div className="flex items-center gap-3 px-2 py-4 mb-6">
        <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20">
          <Zap className="w-5 h-5 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-base font-bold text-foreground tracking-tight">DigitVision</h1>
          <p className="text-[11px] text-muted-foreground">ML-Powered Digit Classifier</p>
        </div>
      </div>

      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-muted-foreground/60 px-3 mb-2">Navigation</p>

      <nav className="flex flex-col gap-1">
        {navItems.map((item) => (
          <NavLink
            key={item.url}
            to={item.url}
            end={item.url === "/"}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-muted-foreground hover:text-foreground hover:bg-primary/5 transition-all duration-200 group"
            activeClassName="bg-primary/10 text-primary font-semibold shadow-sm"
          >
            <item.icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
            <span>{item.title}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto">
        <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/10 p-4 rounded-2xl">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-primary" />
            <p className="text-[11px] font-semibold text-foreground">Model Status</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
            <span className="text-xs text-muted-foreground">Ready for inference</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
