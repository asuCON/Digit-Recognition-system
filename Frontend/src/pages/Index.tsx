import { useState, useCallback } from "react";
import { DrawingCanvas } from "@/components/DrawingCanvas";
import { PredictionDisplay } from "@/components/PredictionDisplay";
import { PredictionHistory } from "@/components/PredictionHistory";
import { AppLayout } from "@/components/AppLayout";
import { Sparkles } from "lucide-react";
import { predictFromBase64 } from "@/lib/api";

interface HistoryEntry {
  digit: number;
  confidence: number;
  timestamp: Date;
}

const Index = () => {
  const [prediction, setPrediction] = useState<number | null>(null);
  const [confidence, setConfidence] = useState<number[]>(Array(10).fill(0));
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrawUpdate = useCallback(async (imageData: ImageData) => {
    // Convert ImageData -> base64 PNG
    const canvas = document.createElement("canvas");
    canvas.width = imageData.width;
    canvas.height = imageData.height;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.putImageData(imageData, 0, 0);
    const dataUrl = canvas.toDataURL("image/png");
    const base64 = dataUrl.includes(",") ? dataUrl.split(",")[1] : dataUrl;
    if (!base64) return;

    setLoading(true);
    setError(null);
    try {
      const result = await predictFromBase64(base64);
      setPrediction(result.digit);
      setConfidence(result.probabilities);
      setHistory((prev) => [
        { digit: result.digit, confidence: result.confidence, timestamp: new Date() },
        ...prev.slice(0, 49),
      ]);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setError(msg || (err instanceof Error ? err.message : "Prediction failed"));
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-6 sm:mb-8 animate-fade-in">
          <div className="flex items-center gap-2 mb-1.5">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-primary/70">
              Digit Recognition
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground">
            Draw & <span className="gradient-text">Predict</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-1.5 max-w-md">
            Draw a digit on the canvas and let the neural network classify it in real-time
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
          <div className="md:col-span-1">
            <DrawingCanvas onDrawUpdate={handleDrawUpdate} />
          </div>
          <div className="md:col-span-1">
            <PredictionDisplay
              prediction={prediction}
              confidence={confidence}
              isLoading={loading}
            />
          </div>
          <div className="md:col-span-2 lg:col-span-1">
            <PredictionHistory history={history} />
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default Index;
