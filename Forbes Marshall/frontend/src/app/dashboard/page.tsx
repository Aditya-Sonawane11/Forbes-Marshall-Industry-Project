export default function DashboardOverviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Welcome back, Admin</h1>
        <p className="mt-2 text-zinc-400">Here's what's happening with your PCB testing system today.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl shadow-sm">
          <h3 className="text-zinc-400 text-sm font-medium">Total Tests Today</h3>
          <p className="text-4xl font-bold text-white mt-2">124</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl shadow-sm">
          <h3 className="text-zinc-400 text-sm font-medium">Pass Rate</h3>
          <p className="text-4xl font-bold text-green-400 mt-2">92.5%</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl shadow-sm">
          <h3 className="text-zinc-400 text-sm font-medium">Active Jigs</h3>
          <p className="text-4xl font-bold text-blue-400 mt-2">3</p>
        </div>
      </div>
    </div>
  );
}
