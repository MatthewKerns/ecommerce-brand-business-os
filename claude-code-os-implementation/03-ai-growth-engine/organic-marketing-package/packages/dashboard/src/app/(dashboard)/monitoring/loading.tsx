export default function MonitoringLoading() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 animate-pulse rounded-lg bg-slate-200" />
        <div className="space-y-2">
          <div className="h-7 w-48 animate-pulse rounded bg-slate-200" />
          <div className="h-4 w-72 animate-pulse rounded bg-slate-200" />
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-28 animate-pulse rounded-lg bg-slate-100" />
        ))}
      </div>
      <div className="h-56 animate-pulse rounded-lg bg-slate-100" />
    </div>
  )
}
