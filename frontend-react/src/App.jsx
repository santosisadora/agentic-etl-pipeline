import { useState, useEffect } from 'react';
import {
  Play, Zap, FileText, Mail, MessageSquare, AlertCircle,
  Search, Copy, Terminal, Sparkles
} from 'lucide-react';

export default function App() {
  const [rawText, setRawText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const [activeLeftTab, setActiveLeftTab] = useState('raw');
  const [activeRightTab, setActiveRightTab] = useState('json');
  const [iteration, setIteration] = useState('-');

  // --- PRESET DATA ---
  const trickyText = "Log entry 402: We saw the thing again. Locals call it the 'Swamp Stalker'. It had glowing eyes and could turn invisible. Spooked us near Blackwood Ridge. Threat level is definitely a 'High'. Nobody died but two guys twisted their ankles running.";

  const audioLogText = "Audio log 88: We found the campsite completely destroyed. Huge claw marks on the trees. The locals call this thing the 'Timber Terror'. It was incredibly fast and seemed to manipulate the shadows, literally blending into the darkness. We were up near the old radio tower on Mount Washington. Threat level is a solid 9 out of 10. Thankfully, everyone made it out alive, so no casualties, but my partner is pretty shaken up.";

  const emailText = "Subject: URGENT: Sighting in the sewers!\nGuys, I just saw it. The 'Gutter Creeper'. It was spewing acid and crawling on the ceiling! This happened right under Main Street station. Two maintenance workers are missing and presumed dead. Threat level? I'd say it's an absolute maximum, like a ten! Send backup now!";

  const socialText = "Just saw the Frost Walker near the frozen lake. It breathes actual ice and moves without making a sound. So scary. Threat level 7 easily. Stay away from the woods!";

  const handleExtract = async () => {
    if (!rawText) return;
    setLoading(true);
    setResult(null);
    setError(null);
    setIteration('1');

    try {
      const response = await fetch("http://localhost:8000/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_text: rawText }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Server error");
      }

      setResult(data);
      setIteration(data.retries_attempted?.toString() || '1');
    } catch (err) {
      setError(err.message);
      setIteration('Failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setIteration(prev => prev === '-' ? '1' : (parseInt(prev) + 1).toString());
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [loading]);

  return (
    <div className="min-h-screen bg-[#0a0a0a] p-4 md:p-8 flex items-center justify-center font-sans text-sm">
      <div className="w-full max-w-[1400px] h-[85vh] bg-[#0f0f0f] rounded-xl border border-zinc-800 overflow-hidden shadow-2xl flex flex-col flex-nowrap">

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-[#141414] border-b border-zinc-800 shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
            <div className="flex items-center gap-2 text-zinc-300 ml-2">
              <Sparkles size={16} className="text-blue-400" />
              <span className="font-semibold tracking-wide text-zinc-100">Self-Healing ETL</span>
              <span className="text-zinc-600">/</span>
              <span className="text-zinc-400">Agentic Pipeline</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-zinc-400 text-xs">
              <div className={`w-2 h-2 rounded-full ${loading ? 'bg-yellow-500 animate-pulse' : 'bg-zinc-600'}`}></div>
              {loading ? 'Processing' : 'Idle'}
            </div>
            <input type="text" readOnly value="http://localhost:8000" className="bg-[#0a0a0a] border border-zinc-800 rounded px-3 py-1 text-zinc-500 w-48 text-xs focus:outline-none" />

            <button onClick={() => setRawText(trickyText)} className="flex items-center gap-2 bg-yellow-950/20 border border-yellow-900/50 text-yellow-500 hover:bg-yellow-900/40 px-3 py-1.5 rounded text-xs font-medium transition-colors">
              <Zap size={14} /> Demo Mode
            </button>

            <button onClick={handleExtract} disabled={loading || !rawText} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white px-4 py-1.5 rounded text-xs font-medium transition-colors">
              <Play size={14} /> Run Pipeline
            </button>
          </div>
        </div>

        <div className="flex flex-1 min-h-0 overflow-hidden">
          {/* LEFT PANE */}
          <div className="w-1/2 flex flex-col border-r border-zinc-800 bg-[#0f0f0f]">
            <div className="flex px-4 border-b border-zinc-800 bg-[#121212] pt-2 shrink-0">
              <button className="px-4 py-2 text-xs font-medium border-b-2 border-blue-500 text-zinc-100">Raw Input</button>
              <button className="px-4 py-2 text-xs font-medium border-b-2 border-transparent text-zinc-500">Schema</button>
            </div>

            <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800/50 bg-[#0a0a0a] shrink-0">
              <span className="text-xs text-zinc-600 font-mono">document.raw</span>
              {/* WIRED UP BUTTONS */}
              <div className="flex gap-2">
                <button onClick={() => setRawText(audioLogText)} className="flex items-center gap-1 text-[11px] text-zinc-400 hover:text-zinc-200 border border-zinc-800 px-2 py-1 rounded bg-[#141414] transition-colors"><FileText size={12}/> Audio Log</button>
                <button onClick={() => setRawText(emailText)} className="flex items-center gap-1 text-[11px] text-zinc-400 hover:text-zinc-200 border border-zinc-800 px-2 py-1 rounded bg-[#141414] transition-colors"><Mail size={12}/> Urgent Email</button>
                <button onClick={() => setRawText(socialText)} className="flex items-center gap-1 text-[11px] text-zinc-400 hover:text-zinc-200 border border-zinc-800 px-2 py-1 rounded bg-[#141414] transition-colors"><MessageSquare size={12}/> Social Post</button>
                <button onClick={() => setRawText(trickyText)} className="flex items-center gap-1 text-[11px] text-rose-400 hover:text-rose-300 border border-rose-900/30 px-2 py-1 rounded bg-rose-950/10 transition-colors"><AlertCircle size={12}/> Tricky</button>
              </div>
            </div>

            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste raw text, HTML, or unstructured data here..."
              className="flex-1 w-full bg-transparent p-4 text-zinc-300 font-mono text-sm resize-none focus:outline-none custom-scrollbar"
              spellCheck="false"
            />
          </div>

          {/* RIGHT PANE */}
          <div className="w-1/2 flex flex-col bg-[#0a0a0a]">
            <div className="flex items-center justify-between px-4 border-b border-zinc-800 bg-[#121212] pt-2 shrink-0">
              <div className="flex">
                <button className="px-4 py-2 text-xs font-medium border-b-2 border-blue-500 text-zinc-100">Extracted JSON</button>
              </div>
              <div className="flex items-center gap-4 text-xs font-mono text-zinc-500 mb-1">
                <span>Iteration: <span className="text-zinc-300">{iteration}</span></span>
                <span>State: <span className={loading ? 'text-yellow-500' : result ? 'text-green-500' : error ? 'text-red-500' : 'text-zinc-300'}>
                  {loading ? 'extracting' : result ? 'success' : error ? 'failed' : 'idle'}
                </span></span>
              </div>
            </div>

            <div className="flex-1 overflow-auto relative">
              {!result && !loading && !error && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-500">
                  <div className="bg-[#141414] border border-zinc-800 p-4 rounded-xl shadow-lg mb-4">
                    <Search size={24} className="text-blue-400" />
                  </div>
                  <p className="font-medium text-zinc-400">No extraction yet</p>
                </div>
              )}

              {loading && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-500 font-mono text-xs">
                  <Terminal size={24} className="text-yellow-500 animate-pulse mb-4" />
                  <p className="text-zinc-400">Calling LLM parser (Attempt {iteration})</p>
                </div>
              )}

              {error && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-red-500 p-8 text-center font-mono text-xs">
                  <AlertCircle size={32} className="mb-4" />
                  <p className="font-bold text-sm">Pipeline Failed</p>
                  <p className="mt-2 text-red-400/80">{error}</p>
                </div>
              )}

              {result && !loading && (
                <pre className="p-4 text-emerald-400 font-mono text-[13px] leading-relaxed custom-scrollbar h-full">
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}