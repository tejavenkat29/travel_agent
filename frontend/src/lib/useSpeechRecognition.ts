import { useCallback, useRef, useState } from "react";

// The Web Speech API is non-standard, so it isn't in the TS DOM lib. We access
// it loosely; `supported` guards every use.
type SpeechRecognitionCtor = new () => any;

function getCtor(): SpeechRecognitionCtor | null {
  const w = window as unknown as {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

/**
 * Browser-native voice dictation. No backend, no API key, no cost.
 * `supported` is false on browsers without the Web Speech API (e.g. Firefox).
 */
export function useSpeechRecognition(lang = "en-IN") {
  const Ctor = getCtor();
  const supported = Ctor !== null;
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recRef = useRef<any>(null);

  const stop = useCallback(() => {
    recRef.current?.stop();
    setListening(false);
  }, []);

  const start = useCallback(() => {
    if (!Ctor) return;
    const rec = new Ctor();
    rec.lang = lang;
    rec.interimResults = true;
    rec.continuous = false;

    rec.onresult = (event: any) => {
      let text = "";
      for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript;
      }
      setTranscript(text);
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);

    recRef.current = rec;
    setTranscript("");
    setListening(true);
    rec.start();
  }, [Ctor, lang]);

  return { supported, listening, transcript, start, stop };
}
