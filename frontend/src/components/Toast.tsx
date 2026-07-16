import React, { createContext, useContext, useState, useCallback, useRef } from 'react';
import { X, CheckCircle, AlertTriangle, Info, XCircle } from 'lucide-react';
import type { ToastMessage } from '../types';

interface ToastContextType {
  addToast: (toast: Omit<ToastMessage, 'id'>) => void;
}

const ToastContext = createContext<ToastContextType>({ addToast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const counterRef = useRef(0);

  const addToast = useCallback((toast: Omit<ToastMessage, 'id'>) => {
    const id = `toast-${++counterRef.current}`;
    const newToast: ToastMessage = { ...toast, id, duration: toast.duration || 4000 };
    setToasts((prev) => [...prev.slice(-4), newToast]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, newToast.duration);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const iconMap = {
    success: <CheckCircle className="w-4 h-4 text-emerald-400" />,
    error: <XCircle className="w-4 h-4 text-rose-400" />,
    warning: <AlertTriangle className="w-4 h-4 text-amber-400" />,
    info: <Info className="w-4 h-4 text-blue-400" />,
  };

  const borderMap = {
    success: 'border-emerald-500/30',
    error: 'border-rose-500/30',
    warning: 'border-amber-500/30',
    info: 'border-blue-500/30',
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto bg-zinc-900 border ${borderMap[toast.type]} rounded-lg p-3 pl-4 pr-8 shadow-2xl animate-slide-in flex items-start gap-3 min-w-[280px] max-w-[380px]`}
          >
            <span className="mt-0.5 flex-shrink-0">{iconMap[toast.type]}</span>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-zinc-100">{toast.title}</div>
              {toast.message && <div className="text-[11px] text-zinc-400 mt-0.5 leading-relaxed">{toast.message}</div>}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="absolute top-2 right-2 text-zinc-500 hover:text-zinc-300 transition-colors cursor-pointer"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
