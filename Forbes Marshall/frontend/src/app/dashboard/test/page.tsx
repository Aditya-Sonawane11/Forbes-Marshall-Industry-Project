"use client";
import { useState } from "react";

export default function StartTestPage() {
  const [boardId, setBoardId] = useState("");
  
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Start New Test</h1>
        <p className="mt-2 text-zinc-400">Scan or enter the PCB barcode to begin.</p>
      </div>
      
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 space-y-6">
        <div className="space-y-4">
          <label className="text-sm font-medium text-zinc-300">Board Identifier (Barcode)</label>
          <div className="flex gap-4">
            <input
              type="text"
              value={boardId}
              onChange={(e) => setBoardId(e.target.value)}
              className="flex-1 px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder:text-zinc-500"
              placeholder="e.g. PCB-2023-XYZ"
              autoFocus
            />
            <button className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-lg shadow-blue-500/25 transition-all">
              Initialize Jig
            </button>
          </div>
        </div>
        
        <div className="p-6 bg-zinc-950 rounded-xl border border-dashed border-zinc-700 text-center text-zinc-500">
          Waiting for board initialization...
        </div>
      </div>
    </div>
  );
}
