import { useQuery } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";
import { useState } from "react";
import { CloudOff } from "lucide-react";
import { getSamples } from "@/lib/api";

interface GallerySample {
  id: number;
  digit: number;
  confidence: number;
  imageData?: string;
}

const Gallery = () => {
  const [filter, setFilter] = useState<number | null>(null);
  const { data, isLoading, error } = useQuery({
    queryKey: ["samples", filter],
    queryFn: () => getSamples(24, filter ?? undefined),
    retry: false,
  });

  const samples: GallerySample[] = (data?.samples ?? []).map((s, i) => ({
    id: i,
    digit: s.label,
    confidence: 1,
    imageData: s.image_base64 ? `data:image/png;base64,${s.image_base64}` : undefined,
  }));

  const hasData = samples.length > 0;
  const filtered = hasData
    ? filter !== null
      ? samples.filter((s) => s.digit === filter)
      : samples
    : [];

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto">
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground">
            Sample <span className="text-primary glow-text">Gallery</span>
          </h1>
          <p className="text-muted-foreground mt-1">
            Browse MNIST sample predictions
          </p>
        </div>

        {hasData ? (
          <>
            <div className="flex gap-2 mb-6 flex-wrap animate-fade-in">
              <button
                onClick={() => setFilter(null)}
                className={`px-3 py-1.5 rounded-lg font-mono-digit text-sm transition-all ${filter === null ? "bg-primary text-primary-foreground glow-button" : "bg-accent/50 text-muted-foreground hover:text-foreground"}`}
              >
                All
              </button>
              {Array.from({ length: 10 }, (_, i) => (
                <button
                  key={i}
                  onClick={() => setFilter(i)}
                  className={`px-3 py-1.5 rounded-lg font-mono-digit text-sm transition-all ${filter === i ? "bg-primary text-primary-foreground glow-button" : "bg-accent/50 text-muted-foreground hover:text-foreground"}`}
                >
                  {i}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-6 gap-4 animate-fade-in">
              {filtered.map((sample) => (
                <div
                  key={sample.id}
                  className="glass-panel p-4 flex flex-col items-center hover-lift cursor-pointer"
                >
                  <div className="w-14 h-14 bg-muted rounded-md flex items-center justify-center mb-2">
                    {sample.imageData ? (
                      <img src={sample.imageData} alt={`Digit ${sample.digit}`} className="w-full h-full rounded-md" />
                    ) : (
                      <span className="font-mono-digit text-2xl font-bold text-foreground">
                        {sample.digit}
                      </span>
                    )}
                  </div>
                  <span className="font-mono-digit text-lg font-bold text-primary">
                    {sample.digit}
                  </span>
                  <span className={`font-mono-digit text-xs ${sample.confidence > 0.95 ? "text-primary" : "text-muted-foreground"}`}>
                    {(sample.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="glass-panel p-12 animate-fade-in">
            <div className="empty-state">
              <CloudOff className="w-12 h-12 mb-4 text-muted-foreground/40" />
              <p className="text-lg font-medium">
                {isLoading ? "Loading..." : error ? "Could not load samples" : "No Samples Yet"}
              </p>
              <p className="text-sm text-muted-foreground/60 mt-1 text-center max-w-sm">
                {error ? "Ensure the backend is running and the model is trained." : "Start making predictions from the Draw & Predict page to populate the gallery."}
              </p>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default Gallery;
