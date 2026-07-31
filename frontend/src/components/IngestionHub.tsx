import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Upload, Play, Pause, Terminal, CheckCircle, 
  FileText, Code, RefreshCw, Settings, AlertTriangle, ShieldAlert
} from 'lucide-react';
import { getSyntheticConfig, toggleSyntheticConfig, ingestLogs } from '../utils/api';
import { useToast } from './Toast';

export default function IngestionHub() {
  const { addToast } = useToast();
  
  // Synthetic generator state
  const [isSyntheticEnabled, setIsSyntheticEnabled] = useState(false);
  const [isConfigLoading, setIsConfigLoading] = useState(false);

  // Upload/Streaming states
  const [logLines, setLogLines] = useState<string[]>([]);
  const [fileName, setFileName] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamIndex, setStreamIndex] = useState(0);
  const [streamSpeed, setStreamSpeed] = useState(500); // ms per line
  const [ingestStats, setIngestStats] = useState({ success: 0, failed: 0, total: 0 });
  const [dragActive, setDragActive] = useState(false);

  const streamIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamIndexRef = useRef(0);

  // Fetch synthetic config on load
  const fetchConfig = useCallback(async () => {
    setIsConfigLoading(true);
    try {
      const data = await getSyntheticConfig();
      setIsSyntheticEnabled(data.enabled);
    } catch {
      addToast({ type: 'error', title: 'Fetch Error', message: 'Failed to retrieve synthetic config.' });
    } finally {
      setIsConfigLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  // Handle synthetic toggle
  const handleToggleSynthetic = async () => {
    setIsConfigLoading(true);
    const nextState = !isSyntheticEnabled;
    try {
      const data = await toggleSyntheticConfig(nextState);
      setIsSyntheticEnabled(data.enabled);
      addToast({ 
        type: 'info', 
        title: nextState ? 'Generator Enabled' : 'Generator Disabled', 
        message: nextState ? 'Mock events will stream automatically.' : 'Dashboard is listening only for real ingest logs.' 
      });
    } catch {
      addToast({ type: 'error', title: 'Toggle Failed', message: 'Failed to update synthetic config.' });
    } finally {
      setIsConfigLoading(false);
    }
  };

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
      setLogLines(lines);
      setIngestStats({ success: 0, failed: 0, total: lines.length });
      setStreamIndex(0);
      streamIndexRef.current = 0;
      setIsStreaming(false);
      addToast({ type: 'success', title: 'File Parsed', message: `Loaded ${lines.length} log lines.` });
    };
    reader.readAsText(file);
  };

  // Ingest single log helper
  const ingestSingleLog = async (logLine: string) => {
    try {
      const res = await ingestLogs([logLine]);
      if (res.success) {
        setIngestStats(prev => ({ ...prev, success: prev.success + 1 }));
      } else {
        setIngestStats(prev => ({ ...prev, failed: prev.failed + 1 }));
      }
    } catch {
      setIngestStats(prev => ({ ...prev, failed: prev.failed + 1 }));
    }
  };

  // Control streaming
  const startStreaming = () => {
    if (logLines.length === 0) return;
    setIsStreaming(true);
    addToast({ type: 'info', title: 'Streaming Started', message: 'Tails are being ingested to backend in real-time.' });
  };

  const pauseStreaming = () => {
    setIsStreaming(false);
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
  };

  useEffect(() => {
    if (isStreaming) {
      streamIntervalRef.current = setInterval(async () => {
        const idx = streamIndexRef.current;
        if (idx < logLines.length) {
          await ingestSingleLog(logLines[idx]);
          setStreamIndex(idx + 1);
          streamIndexRef.current = idx + 1;
        } else {
          pauseStreaming();
          addToast({ type: 'success', title: 'Stream Completed', message: 'All logs successfully ingested.' });
        }
      }, streamSpeed);
    }
    return () => {
      if (streamIntervalRef.current) {
        clearInterval(streamIntervalRef.current);
      }
    };
  }, [isStreaming, logLines, streamSpeed]);

  // Batch Ingestion
  const handleBatchIngest = async () => {
    if (logLines.length === 0) return;
    const remaining = logLines.slice(streamIndex);
    try {
      addToast({ type: 'info', title: 'Batch Processing', message: `Ingesting remaining ${remaining.length} logs...` });
      const res = await ingestLogs(remaining);
      setIngestStats(prev => ({
        ...prev,
        success: prev.success + res.count,
        failed: prev.failed + (remaining.length - res.count)
      }));
      setStreamIndex(logLines.length);
      streamIndexRef.current = logLines.length;
      addToast({ type: 'success', title: 'Batch Completed', message: `Ingested ${res.count} logs successfully.` });
    } catch {
      addToast({ type: 'error', title: 'Batch Failed', message: 'Failed to execute batch ingestion.' });
    }
  };

  // API Documentation text
  const curlDocs = `curl -X POST "http://localhost:8000/api/alerts/ingest" \\
  -H "Authorization: Bearer ${localStorage.getItem('soc_token') || '<JWT_TOKEN>'}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "logs": [
      "Jul 31 18:22:00 workstation sshd[512]: Failed password for invalid user admin from 185.220.101.42 port 49120 ssh2",
      {
        "src_ip": "203.0.113.10",
        "dest_ip": "10.0.5.12",
        "event_type": "PORT_SCAN",
        "severity": "HIGH",
        "raw_log": "Port scan attack payload example"
      }
    ]
  }'`;

  const forwarderScript = `import time
import requests

API_URL = "http://localhost:8000/api/alerts/ingest"
TOKEN = "${localStorage.getItem('soc_token') || 'YOUR_JWT_TOKEN'}"
LOG_FILE = "/var/log/auth.log"  # Path to target log file

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def tail_file(filename):
    with open(filename, "r") as f:
        f.seek(0, 2)  # Go to the end of the file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line.strip()

print(f"Watching {LOG_FILE} and forwarding to Zenith SOC...")
for log_line in tail_file(LOG_FILE):
    try:
        response = requests.post(API_URL, json={"logs": [log_line]}, headers=headers)
        if response.status_code == 200:
            print(f"[+] Forwarded log: {log_line[:60]}...")
    except Exception as e:
        print(f"[-] Connection failed: {e}")`;

  return (
    <div className="flex-grow px-6 py-6 grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-0 overflow-y-auto">
      {/* Configuration & Uploader */}
      <div className="xl:col-span-6 flex flex-col gap-6">
        
        {/* Toggle Switch */}
        <div className="glassmorphism rounded-xl border border-zinc-800 p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="w-5 h-5 text-emerald-500 animate-spin-slow" />
            <div>
              <h2 className="text-sm font-bold tracking-wide text-zinc-200">DEMO MODE SYNTHETIC STREAM</h2>
              <p className="text-[11px] text-zinc-400">Toggle whether simulated network logs stream onto the incident triage feed.</p>
            </div>
          </div>
          <button
            onClick={handleToggleSynthetic}
            disabled={isConfigLoading}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer focus:outline-none ${
              isSyntheticEnabled ? 'bg-emerald-500' : 'bg-zinc-800'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                isSyntheticEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Drag and Drop Uploader */}
        <div className="glassmorphism rounded-xl border border-zinc-800 p-6 flex flex-col gap-4">
          <div className="border-b border-zinc-800/80 pb-3">
            <h2 className="text-sm font-bold tracking-wide text-zinc-200 uppercase flex items-center gap-2">
              <Upload className="w-4 h-4 text-emerald-500" />
              Real-Time Log Ingestion Uploader
            </h2>
            <p className="text-[11px] text-zinc-400 mt-1">Upload Linux logs, firewalls logs, or CSV/JSON files to analyze logs.</p>
          </div>

          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
              dragActive 
                ? 'border-emerald-500 bg-emerald-500/5' 
                : 'border-zinc-800 hover:border-zinc-700 bg-zinc-950/20'
            }`}
            onClick={() => document.getElementById('log-file-input')?.click()}
          >
            <input
              type="file"
              id="log-file-input"
              className="hidden"
              onChange={handleFileChange}
              accept=".log,.txt,.csv,.json"
            />
            <FileText className="w-8 h-8 text-zinc-500 mb-3" />
            <p className="text-xs font-semibold text-zinc-300">Drag and drop file here, or click to browse</p>
            <p className="text-[10px] text-zinc-500 mt-1">Accepts .log, .txt, .csv, or .json log files</p>
          </div>

          {fileName && (
            <div className="bg-zinc-950/40 border border-zinc-800/80 rounded-lg p-4 flex flex-col gap-3 font-mono text-xs">
              <div className="flex justify-between items-center border-b border-zinc-800/40 pb-2">
                <span className="text-zinc-300 font-bold flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-blue-500" />
                  {fileName}
                </span>
                <span className="text-[10px] text-zinc-500">
                  {logLines.length} lines parsed
                </span>
              </div>
              
              <div className="flex flex-col gap-1.5 text-zinc-400 text-[10px]">
                <div className="flex justify-between">
                  <span>Processed:</span>
                  <span className="text-zinc-200">{streamIndex} / {logLines.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Success Ingested:</span>
                  <span className="text-emerald-400 font-bold">{ingestStats.success}</span>
                </div>
                <div className="flex justify-between">
                  <span>Failed Ingested:</span>
                  <span className="text-rose-400 font-bold">{ingestStats.failed}</span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-zinc-800 rounded-full h-1.5 overflow-hidden">
                <div 
                  className="bg-emerald-500 h-1.5 transition-all duration-300"
                  style={{ width: `${(streamIndex / logLines.length) * 100}%` }}
                />
              </div>

              <div className="flex gap-2 mt-2">
                {!isStreaming ? (
                  <button
                    onClick={startStreaming}
                    disabled={streamIndex >= logLines.length}
                    className="flex-1 bg-emerald-600/90 hover:bg-emerald-500 text-white font-bold py-2 px-3 rounded flex items-center justify-center gap-1 cursor-pointer transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <Play className="w-3 h-3" />
                    Stream Ingest
                  </button>
                ) : (
                  <button
                    onClick={pauseStreaming}
                    className="flex-1 bg-amber-600/95 hover:bg-amber-500 text-white font-bold py-2 px-3 rounded flex items-center justify-center gap-1 cursor-pointer transition-colors"
                  >
                    <Pause className="w-3 h-3" />
                    Pause Ingest
                  </button>
                )}

                <button
                  onClick={handleBatchIngest}
                  disabled={streamIndex >= logLines.length}
                  className="flex-1 bg-blue-600/90 hover:bg-blue-500 text-white font-bold py-2 px-3 rounded flex items-center justify-center gap-1 cursor-pointer transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <CheckCircle className="w-3 h-3" />
                  Ingest All
                </button>
              </div>

              {/* Speed Controller */}
              <div className="flex items-center gap-3 mt-2 border-t border-zinc-800/40 pt-2.5">
                <label className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">Stream Speed:</label>
                <input
                  type="range"
                  min="50"
                  max="2000"
                  step="50"
                  value={streamSpeed}
                  onChange={(e) => setStreamSpeed(Number(e.target.value))}
                  className="flex-1 h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
                <span className="text-[10px] text-zinc-300 font-mono w-12 text-right">{streamSpeed}ms</span>
              </div>
            </div>
          )}

          {/* Current log line snapshot */}
          {isStreaming && logLines[streamIndex] && (
            <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-3 font-mono text-[10px] text-emerald-400 border-l-4 border-l-emerald-500 shadow-lg shadow-emerald-950/10">
              <div className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold mb-1">Ingesting line #{streamIndex + 1}</div>
              <div className="break-all line-clamp-2">{logLines[streamIndex]}</div>
            </div>
          )}
        </div>
      </div>

      {/* API documentation */}
      <div className="xl:col-span-6 flex flex-col gap-6">
        <div className="glassmorphism rounded-xl border border-zinc-800 p-6 flex flex-col gap-4">
          <div className="border-b border-zinc-800/80 pb-3 flex items-center justify-between">
            <h2 className="text-sm font-bold tracking-wide text-zinc-200 uppercase flex items-center gap-2">
              <Code className="w-4 h-4 text-purple-500" />
              SOC Log Forwarder Integration
            </h2>
            <span className="text-[10px] bg-purple-950/40 border border-purple-500/30 text-purple-300 px-2 py-0.5 rounded font-semibold uppercase tracking-wider">REST API</span>
          </div>

          <p className="text-[11px] text-zinc-400 leading-relaxed">
            Feed this Zenith SOC dashboard with live logs from your servers, firewalls, routers, or container clusters by posting payloads to the REST endpoint.
          </p>

          <div className="flex flex-col gap-1 text-xs">
            <div className="flex items-center gap-2 border-b border-zinc-800/40 pb-2 mb-2">
              <span className="bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded font-mono font-bold text-[10px] uppercase">POST</span>
              <code className="text-zinc-300 font-bold text-[11px]">/api/alerts/ingest</code>
            </div>

            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1">cURL Ingest Example</div>
            <pre className="bg-zinc-950 border border-zinc-800 text-[10px] text-zinc-300 rounded-lg p-3 font-mono overflow-x-auto whitespace-pre leading-relaxed select-all">
              {curlDocs}
            </pre>
          </div>

          <div className="flex flex-col gap-1 text-xs mt-2">
            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1 flex items-center gap-1">
              <Terminal className="w-3.5 h-3.5 text-purple-500" />
              Tail Log Forwarder (python script)
            </div>
            <pre className="bg-zinc-950 border border-zinc-800 text-[10px] text-zinc-300 rounded-lg p-3 font-mono overflow-x-auto whitespace-pre leading-relaxed select-all max-h-[220px] overflow-y-auto">
              {forwarderScript}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
