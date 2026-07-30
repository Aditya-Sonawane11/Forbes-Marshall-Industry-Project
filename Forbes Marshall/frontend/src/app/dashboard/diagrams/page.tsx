export default function DiagramsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Jig Diagrams</h1>
          <p className="mt-2 text-zinc-400">View and annotate PCB test jigs.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-md transition-all">
          Upload Diagram
        </button>
      </div>
      
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 min-h-[500px] flex items-center justify-center flex-col">
        <div className="text-zinc-500 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-white">No diagram loaded</h3>
        <p className="text-zinc-400 mt-2">Select a jig configuration to view its diagram</p>
      </div>
    </div>
  );
}
