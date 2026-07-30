"use client";
export default function ConfigPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Communication Configuration</h1>
        <p className="mt-2 text-zinc-400">Configure hardware serial ports and baud rates.</p>
      </div>
      
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 space-y-8">
        <div>
          <h2 className="text-xl font-semibold text-white border-b border-zinc-800 pb-2 mb-4">Serial Port Settings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">Port (COM/TTY)</label>
              <select className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-white">
                <option>COM3</option>
                <option>COM4</option>
                <option>/dev/ttyUSB0</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">Baud Rate</label>
              <select className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-white">
                <option>9600</option>
                <option>19200</option>
                <option>38400</option>
                <option>115200</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">Data Bits</label>
              <select className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-white">
                <option>8</option>
                <option>7</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300">Parity</label>
              <select className="w-full px-4 py-3 bg-zinc-800/50 border border-zinc-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-white">
                <option>None</option>
                <option>Even</option>
                <option>Odd</option>
              </select>
            </div>
          </div>
        </div>
        
        <div className="flex gap-4 justify-end border-t border-zinc-800 pt-6">
          <button className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white font-medium rounded-xl border border-zinc-700 transition-all">
            Test Connection
          </button>
          <button className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-lg transition-all">
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}
