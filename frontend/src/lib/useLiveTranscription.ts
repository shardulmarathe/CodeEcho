"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type SpeechRecognitionCtor = new () => SpeechRecognition;

function getSpeechRecognition(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as Window & {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

export function useLiveTranscription() {
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [interimText, setInterimText] = useState("");
  const [finalText, setFinalText] = useState("");
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const finalTextRef = useRef("");

  useEffect(() => {
    setSupported(!!getSpeechRecognition());
  }, []);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    setListening(false);
    setInterimText("");
  }, []);

  const start = useCallback(() => {
    const Ctor = getSpeechRecognition();
    if (!Ctor) return false;

    stop();
    finalTextRef.current = "";
    setFinalText("");
    setInterimText("");

    const recognition = new Ctor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0]?.transcript ?? "";
        if (result.isFinal) {
          finalTextRef.current = `${finalTextRef.current} ${text}`.trim();
          setFinalText(finalTextRef.current);
        } else {
          interim += text;
        }
      }
      setInterimText(interim.trim());
    };

    recognition.onerror = () => {
      // Browser may fire errors when mic is released; ignore during normal stop.
    };

    recognition.onend = () => {
      if (recognitionRef.current === recognition) {
        recognitionRef.current = null;
        setListening(false);
        setInterimText("");
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
    return true;
  }, [stop]);

  const reset = useCallback(() => {
    stop();
    finalTextRef.current = "";
    setFinalText("");
    setInterimText("");
  }, [stop]);

  const displayText = [finalText, interimText].filter(Boolean).join(" ").trim();

  return {
    supported,
    listening,
    finalText,
    interimText,
    displayText,
    start,
    stop,
    reset,
  };
}
