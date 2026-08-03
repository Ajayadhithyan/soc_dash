import { createContext, useContext } from 'react';
import type { ToastMessage } from '../types';

interface ToastContextType {
  addToast: (toast: Omit<ToastMessage, 'id'>) => void;
}

export const ToastContext = createContext<ToastContextType>({
  addToast: () => {}
});

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
