import React, { Component, type ReactNode, type ErrorInfo } from 'react';
import { ShieldAlert, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught:', error, errorInfo);
    console.error('Error name:', error.name);
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    console.error('Component stack:', errorInfo.componentStack);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="flex flex-col items-center justify-center min-h-[300px] bg-zinc-900/40 rounded-xl border border-zinc-800 p-8 gap-4">
          <ShieldAlert className="w-10 h-10 text-rose-500" />
          <h2 className="text-sm font-semibold text-zinc-200">Something went wrong</h2>
          <p className="text-xs text-zinc-400 text-center max-w-md">
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <pre className="text-[9px] text-zinc-600 text-center max-w-lg max-h-32 overflow-auto whitespace-pre-wrap break-all font-mono">
            {this.state.error?.stack || 'No stack trace available'}
          </pre>
          <button
            onClick={this.handleRetry}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors text-xs cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
