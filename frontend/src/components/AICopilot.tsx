import React, { useState, useRef, useEffect, memo } from 'react';
import { Send, Cpu, Terminal, MessageSquare, FileText } from 'lucide-react';

import type { ChatMessage } from '../types';

interface AICopilotProps {
  onSendMessage: (msg: string) => void;
  chatHistory: ChatMessage[];
  isSendingMessage: boolean;
}

function AICopilot({ onSendMessage, chatHistory, isSendingMessage }: AICopilotProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickQuestions = [
    'Recommend triage next steps',
    'What is the top threat type?',
    'Any critical alerts in the system?',
    'List all unique attacking IPs',
  ];

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSendingMessage) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickQuestionClick = (q: string) => {
    if (isSendingMessage) return;
    onSendMessage(q);
  };

  const handleExportTranscript = () => {
    if (chatHistory.length === 0) return;

    let mdContent = `# Zenith AI SOC Threat Assessment Report\n`;
    mdContent += `Generated: ${new Date().toLocaleString()}\n`;
    mdContent += `=========================================\n\n`;

    chatHistory.forEach((msg) => {
      const isUser = msg.sender === 'user';
      mdContent += `### [${isUser ? 'ANALYST QUESTION' : 'ZENITH COPILOT RESPONSE'}]\n`;
      if (!isUser && msg.context_alerts_used > 0) {
        mdContent += `*RAG Security Context Alerts Referenced: ${msg.context_alerts_used}*\n\n`;
      }
      mdContent += `${msg.text}\n\n---\n\n`;
    });

    const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `zenith_soc_report_${new Date().toISOString().slice(0, 10)}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const parseInlineMarkdown = (inlineText: string) => {
    const regex = /(\*\*.*?\*\*|`.*?`)/g;
    const parts = inlineText.split(regex);

    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index} className="font-semibold text-zinc-100">{part.slice(2, -2)}</strong>;
      } else if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={index} className="bg-zinc-950 border border-zinc-800 text-purple-400 font-mono text-[10px] px-1 py-0.5 rounded">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  const renderParsedText = (text: string) => {
    if (!text) return null;

    const parts = text.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        const match = part.match(/```(\w*)\n([\s\S]*?)```/);
        const lang = match ? match[1] : '';
        const code = match ? match[2] : part.slice(3, -3);

        return (
          <div key={index} className="my-3 border border-zinc-800 bg-zinc-950/90 rounded-lg p-3 font-mono text-[10px] relative group overflow-x-auto">
            <div className="flex justify-between items-center text-[9px] text-zinc-500 uppercase border-b border-zinc-900 pb-1 mb-2">
              <span>{lang || 'code segment'}</span>
              <button onClick={() => navigator.clipboard.writeText(code.trim())} className="hover:text-zinc-300 transition-colors cursor-pointer" title="Copy code to clipboard">Copy Code</button>
            </div>
            <pre className="text-emerald-400 whitespace-pre leading-relaxed">{code.trim()}</pre>
          </div>
        );
      } else {
        const lines = part.split('\n');
        return (
          <div key={index} className="space-y-1.5 text-zinc-300 font-sans text-xs">
            {lines.map((line, lineIdx) => {
              const trimmed = line.trim();
              if (trimmed.startsWith('###')) {
                return <h4 key={lineIdx} className="text-zinc-100 font-semibold text-[11px] mt-3 mb-1.5 font-sans border-l-2 border-emerald-500 pl-2 uppercase tracking-wide">{parseInlineMarkdown(trimmed.replace(/^###\s*/, ''))}</h4>;
              }
              if (trimmed.startsWith('##')) {
                return <h3 key={lineIdx} className="text-white font-bold text-xs mt-4 mb-2 font-sans border-l-2 border-purple-500 pl-2 uppercase tracking-wider">{parseInlineMarkdown(trimmed.replace(/^##\s*/, ''))}</h3>;
              }
              if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                return <li key={lineIdx} className="list-disc ml-4 pl-1 text-zinc-300 leading-relaxed">{parseInlineMarkdown(trimmed.replace(/^[-*]\s*/, ''))}</li>;
              }
              if (trimmed === '') return <div key={lineIdx} className="h-1.5" />;
              return <p key={lineIdx} className="leading-relaxed">{parseInlineMarkdown(line)}</p>;
            })}
          </div>
        );
      }
    });
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isSendingMessage]);

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 h-[350px] flex flex-col relative overflow-hidden">
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-emerald-500" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Zenith AI Copilot</h3>
        </div>
        <div className="flex items-center gap-3">
          {chatHistory.length > 0 && (
            <button onClick={handleExportTranscript} className="text-[9px] text-zinc-400 hover:text-white border border-zinc-850 hover:border-zinc-700 bg-zinc-950/40 px-2 py-0.5 rounded flex items-center gap-1 cursor-pointer transition-colors" title="Download Incident Report">
              <FileText className="w-3 h-3 text-purple-400" />Export Report
            </button>
          )}
          <div className="font-mono text-[9px] text-zinc-500">Model: Gemini 2.5</div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 font-mono text-[11px] pr-1 mb-3">
        {chatHistory.length > 0 ? (
          chatHistory.map((msg, index) => {
            const isUser = msg.sender === 'user';
            return (
              <div key={index} className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
                <div className="flex items-center gap-1 text-[9px] text-zinc-500 uppercase">
                  <span>{isUser ? 'Analyst' : 'Zenith Copilot'}</span>
                  {!isUser && msg.context_alerts_used > 0 && (
                    <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-1.5 py-0.5 rounded text-[8px]">RAG Context: {msg.context_alerts_used}</span>
                  )}
                </div>
                <div className={`p-2.5 rounded-lg border max-w-[85%] leading-relaxed ${isUser ? 'bg-blue-500/10 border-blue-500/25 text-zinc-200' : 'bg-zinc-900/60 border-zinc-800 text-zinc-300'}`}>
                  {isUser ? msg.text : <div className="whitespace-normal">{renderParsedText(msg.text)}</div>}
                </div>
              </div>
            );
          })
        ) : (
          <div className="h-full flex flex-col justify-center items-center gap-2 text-zinc-500 text-center font-sans">
            <MessageSquare className="w-5 h-5 text-zinc-600" />
            <div>
              AI Copilot Assistant
              <p className="text-[9px] text-zinc-500 uppercase mt-1">Ask about current threat trends, attackers, or playbook suggestions</p>
            </div>
          </div>
        )}

        {/* Typing Indicator */}
        {isSendingMessage && (
          <div className="flex flex-col gap-1 items-start">
            <div className="text-[9px] text-zinc-500 uppercase">Zenith Copilot thinking</div>
            <div className="bg-zinc-900/60 border border-zinc-800 p-2.5 rounded-lg flex items-center gap-1.5">
              <span className="typing-dot w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span className="typing-dot w-1.5 h-1.5 rounded-full bg-emerald-500" style={{ animationDelay: '0.2s' }}></span>
              <span className="typing-dot w-1.5 h-1.5 rounded-full bg-emerald-500" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {chatHistory.length === 0 && !isSendingMessage && (
        <div className="flex flex-wrap gap-1.5 mb-3 font-sans text-[10px] z-10">
          {quickQuestions.map((q, idx) => (
            <button key={idx} onClick={() => handleQuickQuestionClick(q)} className="bg-zinc-900/60 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 rounded-lg px-2.5 py-1 text-zinc-400 hover:text-white transition-colors cursor-pointer">{q}</button>
          ))}
        </div>
      )}

      <form onSubmit={handleSend} className="flex gap-2 items-center border-t border-zinc-800/80 pt-3 z-10">
        <span className="text-zinc-500 pl-1"><Terminal className="w-4 h-4" /></span>
        <input type="text" placeholder="Ask copilot a question..." value={input} onChange={(e) => setInput(e.target.value)} disabled={isSendingMessage} className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 font-sans text-xs rounded-lg px-3 py-1.5 flex-1 focus:outline-none focus:border-zinc-700 disabled:opacity-40 transition-colors" />
        <button type="submit" disabled={!input.trim() || isSendingMessage} className="bg-emerald-600 hover:bg-emerald-500 text-white p-1.5 rounded-lg transition-colors disabled:opacity-30 cursor-pointer">
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

export default memo(AICopilot);
