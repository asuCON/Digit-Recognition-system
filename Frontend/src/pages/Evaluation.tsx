import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { CloudOff } from "lucide-react";
import { getEvaluate } from "@/lib/api";

const Evaluation = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ["evaluate"],
    queryFn: getEvaluate,
    retry: false,
  });

  const confusionMatrix = data?.confusion_matrix;
  const report = data?.classification_report;
  const weighted = report && typeof report === "object" && "weighted avg" in report
    ? (report["weighted avg"] as Record<string, unknown>)
    : null;
  const precision = weighted?.precision != null ? String(Number(weighted.precision).toFixed(3)) : data?.precision ?? "—";
  const recall = weighted?.recall != null ? String(Number(weighted.recall).toFixed(3)) : data?.recall ?? "—";
  const f1Score = weighted?.["f1-score"] != null ? String(Number(weighted["f1-score"]).toFixed(3)) : data?.f1_score ?? "—";

  const hasData = confusionMatrix && confusionMatrix.length > 0;

  const getColor = (val: number) => {
    if (val > 90) return "bg-primary/80 text-primary-foreground";
    if (val > 5) return "bg-primary/20 text-foreground";
    if (val > 0) return "bg-destructive/20 text-destructive";
    return "bg-transparent text-muted-foreground/30";
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground">
            Model <span className="text-primary glow-text">Evaluation</span>
          </h1>
          <p className="text-muted-foreground mt-1">
            Confusion matrix and classification performance
          </p>
        </div>

        {hasData ? (
          <>
            <div className="glass-panel p-6 animate-fade-in overflow-x-auto">
              <h2 className="text-lg font-semibold text-foreground mb-4">Confusion Matrix</h2>
              <div className="inline-block">
                <div className="flex items-center gap-1 mb-1 pl-8">
                  {Array.from({ length: 10 }, (_, i) => (
                    <div key={i} className="w-10 h-6 flex items-center justify-center">
                      <span className="font-mono-digit text-xs text-muted-foreground">{i}</span>
                    </div>
                  ))}
                </div>
                {confusionMatrix.map((row, ri) => (
                  <div key={ri} className="flex items-center gap-1">
                    <span className="font-mono-digit text-xs text-muted-foreground w-6 text-right">{ri}</span>
                    {row.map((val, ci) => (
                      <div
                        key={ci}
                        className={`w-10 h-10 rounded-md flex items-center justify-center font-mono-digit text-xs transition-colors ${getColor(val)}`}
                        title={`True: ${ri}, Predicted: ${ci}, Count: ${val}`}
                      >
                        {val > 0 ? val : "·"}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground mt-4">
                Rows = true labels, Columns = predicted labels
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              {[
                { label: "Precision", value: precision || "—" },
                { label: "Recall", value: recall || "—" },
                { label: "F1-Score", value: f1Score || "—" },
              ].map((m) => (
                <div key={m.label} className="glass-panel p-4 text-center hover-lift animate-fade-in">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">{m.label}</p>
                  <p className="font-mono-digit text-2xl font-bold text-primary mt-1">{m.value}</p>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="glass-panel p-12 animate-fade-in">
            <div className="empty-state">
              <CloudOff className="w-12 h-12 mb-4 text-muted-foreground/40" />
              <p className="text-lg font-medium">
                {isLoading ? "Loading..." : error ? "Model not loaded" : "No Evaluation Data"}
              </p>
              <p className="text-sm text-muted-foreground/60 mt-1 text-center max-w-sm">
                {error
                  ? "Train a model first from the Training page, then view metrics here."
                  : "Run model evaluation from your backend to see the confusion matrix and metrics here."}
              </p>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default Evaluation;
