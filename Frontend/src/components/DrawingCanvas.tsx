import { useRef, useState, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-react";

interface DrawingCanvasProps {
  onDrawUpdate: (imageData: ImageData) => void;
}

export function DrawingCanvas({ onDrawUpdate }: DrawingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasDrawn, setHasDrawn] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  const getCanvasSize = () => {
    if (containerRef.current) {
      const w = containerRef.current.clientWidth - 2;
      return Math.min(w, 400);
    }
    return 280;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const size = getCanvasSize();
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.fillStyle = "#0a0e1a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawGrid(ctx, canvas.width, canvas.height);

    const handleResize = () => {
      const newSize = getCanvasSize();
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = canvas.width;
      tempCanvas.height = canvas.height;
      tempCanvas.getContext("2d")?.putImageData(imageData, 0, 0);
      canvas.width = newSize;
      canvas.height = newSize;
      ctx.fillStyle = "#0a0e1a";
      ctx.fillRect(0, 0, newSize, newSize);
      ctx.drawImage(tempCanvas, 0, 0, tempCanvas.width, tempCanvas.height, 0, 0, newSize, newSize);
      drawGrid(ctx, newSize, newSize);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const drawGrid = (ctx: CanvasRenderingContext2D, w: number, h: number) => {
    ctx.strokeStyle = "rgba(120, 80, 255, 0.07)";
    ctx.lineWidth = 0.5;
    const step = w / 28;
    for (let i = 0; i <= 28; i++) {
      ctx.beginPath();
      ctx.moveTo(i * step, 0);
      ctx.lineTo(i * step, h);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * step);
      ctx.lineTo(w, i * step);
      ctx.stroke();
    }
  };

  const getPos = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const clientX = "touches" in e ? e.touches[0].clientX : e.clientX;
    const clientY = "touches" in e ? e.touches[0].clientY : e.clientY;
    return {
      x: (clientX - rect.left) * (canvas.width / rect.width),
      y: (clientY - rect.top) * (canvas.height / rect.height),
    };
  };

  const triggerPrediction = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    onDrawUpdate(ctx.getImageData(0, 0, canvas.width, canvas.height));
  }, [onDrawUpdate]);

  const debouncedPredict = useCallback(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(triggerPrediction, 300);
  }, [triggerPrediction]);

  const startDrawing = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx) return;
    setIsDrawing(true);
    setHasDrawn(true);
    const pos = getPos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
  }, []);

  const draw = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!isDrawing) return;
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx) return;
    const pos = getPos(e);
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = Math.max(14, canvasRef.current!.width / 18);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    debouncedPredict();
  }, [isDrawing, debouncedPredict]);

  const stopDrawing = useCallback(() => {
    if (isDrawing) {
      setIsDrawing(false);
      triggerPrediction();
    }
  }, [isDrawing, triggerPrediction]);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.fillStyle = "#0a0e1a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawGrid(ctx, canvas.width, canvas.height);
    setHasDrawn(false);
  };

  return (
    <div className="glass-panel p-5 sm:p-6 glass-panel-hover" ref={containerRef}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-foreground">Drawing Canvas</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Draw a digit (0–9)</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={clearCanvas}
          disabled={!hasDrawn}
          className="gap-2 text-xs rounded-xl hover:bg-primary/5 hover:text-primary hover:border-primary/30 transition-all"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Clear
        </Button>
      </div>

      <div className={`canvas-holo mx-auto w-fit ${isDrawing ? "drawing" : ""}`}>
        <canvas
          ref={canvasRef}
          width={280}
          height={280}
          className="relative rounded-2xl cursor-crosshair touch-none w-full max-w-[400px]"
          style={{ aspectRatio: "1/1" }}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
      </div>

      <p className="text-center text-[11px] text-muted-foreground/50 mt-3 font-medium">
        Prediction updates in real-time
      </p>
    </div>
  );
}
