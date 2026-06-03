import React, { useState, useRef, useEffect } from 'react';
import { Send, Cpu, Terminal, Sparkles, MessageSquare } from 'lucide-react';

function AICopilot({ onSendMessage, chatHistory, isSendingMessage }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const quickQuestions = [
    'Recommend triage next steps',
    'What is the top threat type?',
    'Any critical alerts in the system?',
    'List all unique attacking IPs',
  ];

  const handleSend = (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isSendingMessage) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickQuestionClick = (q) => {
    if (isSendingMessage) return;
    onSendMessage(q);
  };

  // Scroll chat window to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isSendingMessage]);

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 h-[350px] flex flex-col relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-emerald-500" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase flex items-center gap-1.5">
            Aegis AI Copilot
          </h3>
        </div>
        <div className="font-mono text-[9px] text-zinc-500">
          Model: Gemini 2.5
        </div>
      </div>

      {/* Terminal Message Stream */}
      <div className="flex-1 overflow-y-auto space-y-3 font-mono text-[11px] pr-1 mb-3">
        {chatHistory.length > 0 ? (
          chatHistory.map((msg, index) => {
            const isUser = msg.sender === 'user';
            return (
              <div
                key={index}
                className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div className="flex items-center gap-1 text-[9px] text-zinc-500 uppercase">
                  <span>{isUser ? 'Analyst' : 'Aegis Copilot'}</span>
                  {!isUser && msg.context_alerts_used > 0 && (
                    <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-1 rounded text-[8px]">
                      RAG Context: {msg.context_alerts_used}
                    </span>
                  )}
                </div>
                <div
                  className={`p-2.5 rounded-lg border max-w-[85%] leading-relaxed ${isUser ? 'bg-blue-500/10 border-blue-500/25 text-zinc-200' : 'bg-zinc-900/60 border-zinc-800 text-zinc-300'}`}
                >
                  {isUser ? (
                    msg.text
                  ) : (
                    <div className="whitespace-pre-wrap font-sans leading-relaxed text-xs">{msg.text}</div>
                  )}
                </div>
              </div>
            );
          })
        ) : (
          <div className="h-full flex flex-col justify-center items-center gap-2 text-zinc-500 text-center font-sans">
            <MessageSquare className="w-5 h-5 text-zinc-600" />
            <div>
              AI Copilot Assistant
              <p className="text-[9px] text-zinc-500 uppercase mt-1">
                Ask about current threat trends, attackers, or playbook suggestions
              </p>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {isSendingMessage && (
          <div className="flex flex-col gap-1 items-start">
            <div className="text-[9px] text-zinc-500 uppercase animate-pulse">Aegis copilot typing...</div>
            <div className="bg-zinc-900/60 border border-zinc-800 p-2.5 rounded-lg flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce"></span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Questions Chips */}
      {chatHistory.length === 0 && !isSendingMessage && (
        <div className="flex flex-wrap gap-1.5 mb-3 font-sans text-[10px] z-10">
          {quickQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickQuestionClick(q)}
              className="bg-zinc-900/60 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 rounded-lg px-2.5 py-1 text-zinc-400 hover:text-white transition-colors cursor-pointer"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Text Input Footer Form */}
      <form onSubmit={handleSend} className="flex gap-2 items-center border-t border-zinc-800/80 pt-3 z-10">
        <span className="text-zinc-500 pl-1">
          <Terminal className="w-4 h-4" />
        </span>
        <input
          type="text"
          placeholder="Ask copilot a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isSendingMessage}
          className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 font-sans text-xs rounded-lg px-3 py-1.5 flex-1 focus:outline-none focus:border-zinc-700 disabled:opacity-40 transition-colors"
        />
        <button
          type="submit"
          disabled={!input.trim() || isSendingMessage}
          className="bg-emerald-600 hover:bg-emerald-500 text-white p-1.5 rounded-lg transition-colors disabled:opacity-30 cursor-pointer"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

export default AICopilot;
