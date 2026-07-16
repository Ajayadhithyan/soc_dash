import React from 'react';

interface SkeletonProps {
  className?: string;
  count?: number;
}

export function Skeleton({ className = '', count = 1 }: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`animate-pulse bg-zinc-800/60 rounded ${className}`} />
      ))}
    </>
  );
}

export function AlertTableSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div className="flex flex-col gap-1">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 py-3 px-3 border-b border-zinc-800/30">
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-4 w-16 rounded-full" />
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-3 w-24" />
          <div className="ml-auto"><Skeleton className="h-3 w-10" /></div>
        </div>
      ))}
    </div>
  );
}

export function OverviewCardsSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-6 py-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5">
          <Skeleton className="h-3 w-24 mb-3" />
          <Skeleton className="h-8 w-20 mb-2" />
          <Skeleton className="h-3 w-32" />
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 h-[260px]">
      <Skeleton className="h-4 w-40 mb-4" />
      <Skeleton className="h-full w-full rounded-lg" />
    </div>
  );
}

export function SidebarSkeleton() {
  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-full gap-4">
      <Skeleton className="h-4 w-36" />
      <Skeleton className="h-20 w-full rounded-xl" />
      <div className="flex gap-2">
        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-8 flex-1" />)}
      </div>
      <Skeleton className="h-24 w-full rounded-xl" />
      <Skeleton className="h-24 w-full rounded-xl" />
    </div>
  );
}
