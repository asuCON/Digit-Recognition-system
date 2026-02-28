import { Clock, Sparkles } from "lucide-react";

interface HistoryEntry {
  digit: number;
  confidence: number;
  timestamp: Date;
}

interface PredictionHistoryProps {
  history: HistoryEntry[];
}

export function PredictionHistory({ history }: PredictionHistoryProps) {
  return (
    <div className="glass-panel p-5 sm:p-6 glass-panel-hover animate-fade-in" style={{ animationDelay: "0.2s" }}>
      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-4 h-4 text-muted-foreground" />
        <h2 className="text-base sm:text-lg font-bold text-foreground">History</h2>
        {history.length > 0 && (
          <span className="ml-auto text-[10px] font-mono-digit font-bold text-primary bg-primary/10 px-2.5 py-0.5 rounded-full border border-primary/15">
            {history.length}
          </span>
        )}
      </div>

      {history.length === 0 ? (
        <div className="text-center py-8 sm:py-10">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-primary/5 border border-primary/10 flex items-center justify-center mb-3">
            <Sparkles className="w-6 h-6 text-primary/30" />
          </div>
          <p className="text-sm font-medium text-muted-foreground">No predictions yet</p>
          <p className="text-xs text-muted-foreground/50 mt-1">Start drawing to see results</p>
        </div>
      ) : (
        <div className="space-y-1.5 max-h-48 sm:max-h-64 overflow-y-auto pr-1 scrollbar-thin">
          {history.map((entry, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-2.5 sm:p-3 rounded-xl bg-muted/30 hover:bg-primary/5 transition-all duration-300 border border-transparent hover:border-primary/10 hover:shadow-md group cursor-default animate-slide-up"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <div className="flex items-center gap-2.5 sm:gap-3">
                <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-primary/15 to-secondary/10 flex items-center justify-center group-hover:from-primary/20 group-hover:to-secondary/15 transition-all border border-primary/10">
                  <span className="font-mono-digit text-lg sm:text-xl font-bold text-primary">
                    {entry.digit}
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground font-mono-digit">
                  {entry.timestamp.toLocaleTimeString()}
                </p>
              </div>
              <span className={`font-mono-digit text-xs sm:text-sm font-semibold ${
                entry.confidence > 0.8 ? "text-primary" : entry.confidence > 0.5 ? "text-foreground" : "text-accent"
              }`}>
                {(entry.confidence * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
