"use client";
export default function AdvancedTestPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Advanced Testing</h1>
        <p className="mt-2 text-zinc-400">Manual diagnostics and raw communication tools.</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-xl font-semibold text-white border-b border-zinc-800 pb-2">Manual Commands</h2>
          <div className="space-y-4">
            <div className="flex gap-4">
              <input
                type="text"
                className="flex-1 px-4 py-2 bg-zinc-800/50 border border-zinc-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder:text-zinc-500"
                placeholder="Enter raw command (e.g. AT+PING)"
              />
              <button className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white font-medium rounded-lg transition-all border border-zinc-700">
                Send
              </button>
            </div>
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
          <h2 className="text-xl font-semibold text-white border-b border-zinc-800 pb-2">Terminal Output</h2>
          <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800 font-mono text-xs h-64 overflow-y-auto">
            <div className="text-zinc-500">System ready. Waiting for serial data...</div>
            <div className="text-green-400 mt-2">&gt; AT+PING</div>
            <div className="text-zinc-300">OK</div>
          </div>
        </div>
      </div>
    </div>
  );
}
