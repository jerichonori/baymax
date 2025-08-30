import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

interface AudioVisualizerProps {
  isRecording: boolean;
  stream: MediaStream | null;
}

export function AudioVisualizer({ isRecording, stream }: AudioVisualizerProps) {
  const [audioLevels, setAudioLevels] = useState<number[]>([0, 0, 0, 0, 0, 0, 0]);
  const animationFrameRef = useRef<number>();
  const audioContextRef = useRef<AudioContext>();
  const analyserRef = useRef<AnalyserNode>();

  useEffect(() => {
    if (!isRecording || !stream) {
      setAudioLevels([0, 0, 0, 0, 0, 0, 0]);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      return;
    }

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    
    analyser.fftSize = 512;
    analyser.smoothingTimeConstant = 0.3;
    analyser.minDecibels = -90;
    analyser.maxDecibels = -10;
    source.connect(analyser);
    
    audioContextRef.current = audioContext;
    analyserRef.current = analyser;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    
    const updateLevels = () => {
      if (!analyserRef.current) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      
      const barCount = 7;
      const newLevels: number[] = [];
      
      // Focus on voice frequency range (80Hz to 8kHz)
      const voiceStartBin = Math.floor(80 * analyser.frequencyBinCount / (audioContext.sampleRate / 2));
      const voiceEndBin = Math.floor(8000 * analyser.frequencyBinCount / (audioContext.sampleRate / 2));
      const voiceRange = voiceEndBin - voiceStartBin;
      const chunkSize = Math.floor(voiceRange / barCount);
      
      for (let i = 0; i < barCount; i++) {
        let sum = 0;
        let maxVal = 0;
        const start = voiceStartBin + (i * chunkSize);
        const end = start + chunkSize;
        
        for (let j = start; j < end && j < dataArray.length; j++) {
          sum += dataArray[j];
          maxVal = Math.max(maxVal, dataArray[j]);
        }
        
        const average = sum / chunkSize;
        // Use a combination of average and peak for better responsiveness
        const combined = (average * 0.7 + maxVal * 0.3);
        // More aggressive normalization with lower threshold
        const normalized = Math.min(1, Math.pow(combined / 180, 0.8));
        // Add a small random variation for visual interest
        const withVariation = normalized + (normalized > 0.1 ? Math.random() * 0.05 : 0);
        newLevels.push(Math.min(1, withVariation));
      }
      
      setAudioLevels(newLevels);
      animationFrameRef.current = requestAnimationFrame(updateLevels);
    };
    
    updateLevels();
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [isRecording, stream]);

  return (
    <div className="flex items-end justify-center gap-1.5 h-16">
      {audioLevels.map((level, index) => (
        <motion.div
          key={index}
          className="w-2 bg-gradient-to-t from-blue-600 to-indigo-400 rounded-full relative"
          initial={{ height: 8 }}
          animate={{
            height: isRecording ? Math.max(12, 12 + level * 52) : 12,
            opacity: isRecording ? 0.7 + level * 0.3 : 0.4,
            scale: isRecording ? 1 + level * 0.1 : 1,
          }}
          transition={{
            height: { 
              type: "spring",
              stiffness: 300,
              damping: 20,
              mass: 0.5
            },
            opacity: { duration: 0.05 },
            scale: { duration: 0.1 },
          }}
          style={{
            boxShadow: isRecording && level > 0.2 
              ? `0 0 ${level * 25}px rgba(59, 130, 246, ${level * 0.6}), inset 0 0 ${level * 10}px rgba(255, 255, 255, ${level * 0.3})`
              : "none",
            filter: isRecording && level > 0.5 ? `brightness(${1 + level * 0.3})` : "none",
          }}
        />
      ))}
    </div>
  );
}

export function CircularAudioVisualizer({ isRecording, stream }: AudioVisualizerProps) {
  const [audioLevel, setAudioLevel] = useState(0);
  const animationFrameRef = useRef<number>();
  const audioContextRef = useRef<AudioContext>();
  const analyserRef = useRef<AnalyserNode>();

  useEffect(() => {
    if (!isRecording || !stream) {
      setAudioLevel(0);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      return;
    }

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.4;
    analyser.minDecibels = -90;
    analyser.maxDecibels = -10;
    source.connect(analyser);
    
    audioContextRef.current = audioContext;
    analyserRef.current = analyser;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    
    const updateLevel = () => {
      if (!analyserRef.current) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      
      // Focus on voice frequency range
      const voiceStartBin = Math.floor(80 * analyser.frequencyBinCount / (audioContext.sampleRate / 2));
      const voiceEndBin = Math.floor(4000 * analyser.frequencyBinCount / (audioContext.sampleRate / 2));
      
      let sum = 0;
      let maxVal = 0;
      let count = 0;
      
      for (let i = voiceStartBin; i < voiceEndBin && i < dataArray.length; i++) {
        sum += dataArray[i];
        maxVal = Math.max(maxVal, dataArray[i]);
        count++;
      }
      
      const average = count > 0 ? sum / count : 0;
      // Combine average and peak for better responsiveness
      const combined = (average * 0.6 + maxVal * 0.4);
      // More sensitive normalization
      const normalized = Math.min(1, Math.pow(combined / 150, 0.7));
      
      setAudioLevel(normalized);
      animationFrameRef.current = requestAnimationFrame(updateLevel);
    };
    
    updateLevel();
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [isRecording, stream]);

  return (
    <div className="relative">
      {[0.3, 0.6, 1].map((scale, index) => (
        <motion.div
          key={index}
          className="absolute inset-0 rounded-full"
          style={{
            background: `radial-gradient(circle, transparent 40%, rgba(239, 68, 68, ${0.15 - index * 0.05}) 100%)`,
          }}
          initial={{ scale: 1 }}
          animate={{
            scale: isRecording ? 1 + audioLevel * scale : 1,
            opacity: isRecording ? 0.3 + audioLevel * 0.5 : 0,
          }}
          transition={{
            scale: { duration: 0.15, ease: "easeOut" },
            opacity: { duration: 0.15 },
          }}
        />
      ))}
    </div>
  );
}

export function WaveformVisualizer({ isRecording, stream }: AudioVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();
  const audioContextRef = useRef<AudioContext>();
  const analyserRef = useRef<AnalyserNode>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (!isRecording || !stream) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      return;
    }

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.85;
    source.connect(analyser);
    
    audioContextRef.current = audioContext;
    analyserRef.current = analyser;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!analyserRef.current) return;
      
      animationFrameRef.current = requestAnimationFrame(draw);
      analyserRef.current.getByteTimeDomainData(dataArray);

      ctx.fillStyle = "rgba(255, 255, 255, 0.05)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.lineWidth = 2;
      ctx.strokeStyle = "rgb(59, 130, 246)";
      ctx.beginPath();

      const sliceWidth = (canvas.width * 1.0) / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };

    draw();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [isRecording, stream]);

  return (
    <canvas
      ref={canvasRef}
      width={300}
      height={100}
      className="w-full h-full rounded-lg"
      style={{ background: "linear-gradient(to bottom, #f0f9ff, #e0f2fe)" }}
    />
  );
}