export default function StagesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Stage Builder</h1>
          <p className="mt-2 text-zinc-400">Design and configure test stages.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-md transition-all">
          + New Stage
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 flex flex-col justify-between min-h-[200px]">
          <div>
            <h3 className="text-lg font-bold text-white">Stage 1: Power On Validation</h3>
            <p className="text-sm text-zinc-400 mt-2">Checks if the 5V and 3.3V rails are stable within 5% tolerance before proceeding.</p>
          </div>
          <div className="flex items-center justify-between mt-6">
            <span className="text-xs px-2 py-1 bg-zinc-800 rounded-md text-zinc-300">2 Test Cases</span>
            <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">Edit Sequence</button>
          </div>
        </div>
        
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 flex flex-col justify-between min-h-[200px]">
          <div>
            <h3 className="text-lg font-bold text-white">Stage 2: Serial Communication</h3>
            <p className="text-sm text-zinc-400 mt-2">Validates UART TX/RX lines and ensures firmware is responding to standard ping.</p>
          </div>
          <div className="flex items-center justify-between mt-6">
            <span className="text-xs px-2 py-1 bg-zinc-800 rounded-md text-zinc-300">4 Test Cases</span>
            <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">Edit Sequence</button>
          </div>
        </div>
      </div>
    </div>
  );
}
