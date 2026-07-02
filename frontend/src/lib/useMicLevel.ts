"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export function useMicLevel() {
  const [level, setLevel] = useState(0);
  const [active, setActive] = useState(false);
  const rafRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const smoothRef = useRef(0);
  const peakRef = useRef(0);
  const meterStreamRef = useRef<MediaStream | null>(null);

  const getPeak = useCallback(() => peakRef.current, []);

  const stop = useCallback(() => {
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    analyserRef.current = null;
    meterStreamRef.current?.getTracks().forEach((t) => t.stop());
    meterStreamRef.current = null;
    if (audioContextRef.current) {
      void audioContextRef.current.close();
      audioContextRef.current = null;
    }
    smoothRef.current = 0;
    peakRef.current = 0;
    setActive(false);
    setLevel(0);
  }, []);

  const start = useCallback(
    async (stream: MediaStream) => {
      stop();

      // Meter uses a clone so AudioContext teardown never affects MediaRecorder.
      const meterStream = stream.clone();
      meterStreamRef.current = meterStream;

      const audioContext = new AudioContext();
      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.75;
      const source = audioContext.createMediaStreamSource(meterStream);
      source.connect(analyser);
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      setActive(true);

      const data = new Uint8Array(analyser.fftSize);
      const tick = () => {
        if (!analyserRef.current) return;
        analyser.getByteTimeDomainData(data);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
          const v = (data[i] - 128) / 128;
          sum += v * v;
        }
        const rms = Math.sqrt(sum / data.length);
        const instant = Math.min(1, rms * 8);

        const prev = smoothRef.current;
        const smooth =
          instant > prev
            ? prev * 0.3 + instant * 0.7
            : prev * 0.85 + instant * 0.15;
        smoothRef.current = smooth;

        if (instant > peakRef.current) {
          peakRef.current = instant;
        }

        setLevel(smooth);
        rafRef.current = requestAnimationFrame(tick);
      };
      rafRef.current = requestAnimationFrame(tick);
    },
    [stop]
  );

  useEffect(() => () => stop(), [stop]);

  return { level, active, getPeak, start, stop };
}
