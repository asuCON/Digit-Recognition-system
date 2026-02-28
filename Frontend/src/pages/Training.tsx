import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Brain, Layers, Zap, TrendingUp, CloudOff, Play } from "lucide-react";
import { trainModel, getTrainingRuns, getTrainProgress } from "@/lib/api";

interface TrainingMetric {
  label: string;
  value: string;
  icon: typeof Brain;
  progress: number;
}

const Training = () => {
  const defaultIcons = [Layers, TrendingUp, Zap, Brain];
  const queryClient = useQueryClient();
  const [modelType, setModelType] = useState<"advanced" | "simple">("advanced");
  const [epochs, setEpochs] = useState(15);
  const [progress, setProgress] = useState<{
    status: string;
    message?: string;
    current_epoch?: number;
    total_epochs?: number;
    loss?: number;
    acc?: number;
    val_loss?: number;
    val_acc?: number;
    error?: string;
  } | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { data: runsData } = useQuery({
    queryKey: ["training-runs"],
    queryFn: getTrainingRuns,
    retry: false,
  });

  const trainMutation = useMutation({
    mutationFn: () => trainModel({ model_type: modelType, epochs }),
    onSuccess: () => {
      setProgress(null);
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
      queryClient.invalidateQueries({ queryKey: ["training-runs"] });
      queryClient.invalidateQueries({ queryKey: ["evaluate"] });
    },
    onError: () => {
      setProgress(null);
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    },
  });

  useEffect(() => {
    if (!trainMutation.isPending) return;
    setProgress({ status: "starting", message: "Starting training..." });
    const poll = () => {
      getTrainProgress()
        .then((p) => setProgress(p))
        .catch(() => {});
    };
    poll();
    pollRef.current = setInterval(poll, 1500);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [trainMutation.isPending]);

  const latestRun = runsData?.results?.[0];
  const metrics: TrainingMetric[] = latestRun
    ? [
        { label: "Test Accuracy", value: `${(latestRun.test_accuracy * 100).toFixed(2)}%`, icon: TrendingUp, progress: latestRun.test_accuracy * 100 },
        { label: "Test Loss", value: latestRun.test_loss.toFixed(4), icon: Zap, progress: Math.max(0, 100 - latestRun.test_loss * 50) },
        { label: "Model Type", value: latestRun.model_type, icon: Layers, progress: 100 },
        { label: "Epochs", value: String(latestRun.epochs), icon: Brain, progress: 100 },
      ]
    : [];
  const logs = runsData?.results ?? [];
  const hasData = metrics.length > 0;
  const hasLogs = logs.length > 0;

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground">
            Model <span className="text-primary glow-text">Training</span>
          </h1>
          <p className="text-muted-foreground mt-1">
            Monitor and configure model training parameters
          </p>
        </div>

        <div className="glass-panel p-6 mb-6 animate-fade-in">
          <h2 className="text-lg font-semibold text-foreground mb-4">Start Training</h2>
          <div className="flex flex-wrap gap-4 items-center">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Model</label>
              <select
                value={modelType}
                onChange={(e) => setModelType(e.target.value as "advanced" | "simple")}
                className="px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm"
              >
                <option value="advanced">Advanced CNN</option>
                <option value="simple">Simple CNN</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Epochs</label>
              <input
                type="number"
                min={1}
                max={50}
                value={epochs}
                onChange={(e) => setEpochs(Number(e.target.value))}
                className="px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm w-20"
              />
            </div>
            <Button
              onClick={() => trainMutation.mutate()}
              disabled={trainMutation.isPending}
              className="gap-2 mt-6"
            >
              <Play className="w-4 h-4" />
              {trainMutation.isPending ? "Training..." : "Train Model"}
            </Button>
          </div>
          {trainMutation.isPending && progress && (
            <div className="mt-4 p-4 rounded-lg bg-primary/5 border border-primary/20 font-mono-digit text-sm">
              <p className="font-semibold text-foreground mb-2">{progress.message ?? progress.status}</p>
              {progress.status === "training" && progress.current_epoch != null && progress.total_epochs != null && (
                <>
                  <p className="text-muted-foreground">
                    Epoch {progress.current_epoch} / {progress.total_epochs}
                  </p>
                  <p className="text-muted-foreground mt-1">
                    loss: {progress.loss?.toFixed(4) ?? "—"} | acc: {progress.acc != null ? (progress.acc * 100).toFixed(2) + "%" : "—"} | val_loss: {progress.val_loss?.toFixed(4) ?? "—"} | val_acc: {progress.val_acc != null ? (progress.val_acc * 100).toFixed(2) + "%" : "—"}
                  </p>
                  <Progress value={(progress.current_epoch / progress.total_epochs) * 100} className="h-2 mt-2" />
                </>
              )}
              {progress.status === "error" && progress.error && (
                <p className="text-destructive mt-2">{progress.error}</p>
              )}
            </div>
          )}
          {trainMutation.isError && (
            <div className="mt-4 p-4 rounded-lg bg-destructive/10 text-destructive text-sm font-mono-digit">
              {(() => {
                const err = trainMutation.error as { response?: { data?: { detail?: string } }; message?: string };
                return err?.response?.data?.detail ?? (err?.message ?? String(trainMutation.error));
              })()}
            </div>
          )}
        </div>

        {hasData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {metrics.map((metric, i) => (
              <div key={metric.label} className="glass-panel p-6 hover-lift animate-fade-in">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    {(() => {
                      const Icon = metric.icon || defaultIcons[i % defaultIcons.length];
                      return <Icon className="w-5 h-5 text-primary" />;
                    })()}
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider">{metric.label}</p>
                    <p className="font-mono-digit text-xl font-bold text-foreground">{metric.value}</p>
                  </div>
                </div>
                <Progress value={metric.progress} className="h-2" />
              </div>
            ))}
          </div>
        ) : (
          <div className="glass-panel p-12 animate-fade-in">
            <div className="empty-state">
              <CloudOff className="w-12 h-12 mb-4 text-muted-foreground/40" />
              <p className="text-lg font-medium">No Training Data</p>
              <p className="text-sm text-muted-foreground/60 mt-1 text-center max-w-sm">
                Click &quot;Train Model&quot; above to train and see metrics here.
              </p>
            </div>
          </div>
        )}

        <div className="glass-panel p-6 mt-6 animate-fade-in">
          <h2 className="text-lg font-semibold text-foreground mb-4">Training Log</h2>
          {hasLogs ? (
            <div className="font-mono-digit text-xs text-muted-foreground space-y-1 max-h-48 overflow-y-auto">
              {logs.map((run) => (
                <p key={run.id}>
                  [{run.created_at}] {run.model_type} — epochs: {run.epochs} — acc: {(run.test_accuracy * 100).toFixed(2)}% — loss: {run.test_loss.toFixed(4)}
                </p>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center py-8">
              <p className="text-sm text-muted-foreground/50 font-mono-digit">
                Waiting for training data...
              </p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default Training;
