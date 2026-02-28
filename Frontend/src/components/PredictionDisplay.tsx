interface PredictionDisplayProps {
  prediction: number | null;
  confidence: number[];
  isLoading?: boolean;
}

export function PredictionDisplay({ prediction, confidence, isLoading }: PredictionDisplayProps) {
  const maxConfidence = Math.max(...confidence, 0);
  const sortedDigits = confidence
    .map((conf, digit) => ({ digit, conf }))
    .sort((a, b) => b.conf - a.conf);

  return (
    <div className="glass-panel p-5 sm:p-6 glass-panel-hover animate-fade-in" style={{ animationDelay: "0.1s" }}>
      <h2 className="text-base sm:text-lg font-bold text-foreground mb-4">Prediction</h2>

      <div className="flex items-center justify-center mb-6">
        {prediction !== null ? (
          <div className="text-center animate-digit-pop">
            <div className="relative inline-block">
              <div
                className="absolute inset-0 rounded-full blur-3xl scale-[2.5] confidence-pulse"
                style={{
                  background: `radial-gradient(circle, hsl(250 85% 60% / ${maxConfidence * 0.3}) 0%, transparent 70%)`,
                }}
              />
              <span className="relative font-mono-digit text-7xl sm:text-8xl lg:text-9xl font-bold gradient-text drop-shadow-lg" style={{ filter: "none", WebkitTextFillColor: "transparent" }}>
                {prediction}
              </span>
            </div>
            <p className="text-sm text-muted-foreground mt-4">
              <span className="font-mono-digit font-bold text-primary">{(maxConfidence * 100).toFixed(1)}%</span>
              <span className="ml-1.5">confidence</span>
            </p>
          </div>
        ) : (
          <div className="text-center py-6 sm:py-8">
            <span className="font-mono-digit text-5xl sm:text-6xl text-muted-foreground/20">?</span>
            <p className="text-sm text-muted-foreground mt-3">
              {isLoading ? (
                <span className="inline-flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                  Analyzing...
                </span>
              ) : (
                "Draw a digit to predict"
              )}
            </p>
          </div>
        )}
      </div>

      <div className="space-y-2">
        <h3 className="text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-[0.15em] mb-3">
          Confidence Distribution
        </h3>
        {sortedDigits.map(({ digit, conf }, index) => {
          const isPredicted = digit === prediction;
          const barWidth = conf * 100;
          return (
            <div key={digit} className="flex items-center gap-2 sm:gap-3 group">
              <span className={`font-mono-digit text-xs w-4 transition-all duration-300 ${isPredicted ? "text-primary font-bold scale-110" : "text-muted-foreground"}`}>
                {digit}
              </span>
              <div className="h-2 sm:h-2.5 flex-1 rounded-full bg-muted/60 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700 ease-out"
                  style={{
                    width: `${barWidth}%`,
                    background: isPredicted
                      ? "linear-gradient(90deg, hsl(250 85% 60%), hsl(195 90% 50%))"
                      : conf > 0
                        ? "linear-gradient(90deg, hsl(250 85% 60% / 0.25), hsl(195 90% 50% / 0.2))"
                        : "transparent",
                  }}
                />
              </div>
              <span className="font-mono-digit text-[11px] w-12 text-right text-muted-foreground tabular-nums">
                {(conf * 100).toFixed(1)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
