export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Results History</h1>
          <p className="mt-2 text-zinc-400">View and export past PCB test results.</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white font-medium rounded-xl border border-zinc-700 transition-all">
            Filter
          </button>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-md transition-all">
            Export CSV
          </button>
        </div>
      </div>
      
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
        <table className="w-full text-left text-sm text-zinc-300">
          <thead className="bg-zinc-800/50 text-zinc-400 font-medium">
            <tr>
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4">Board ID</th>
              <th className="px-6 py-4">Tester</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            <tr className="hover:bg-zinc-800/30 transition-colors">
              <td className="px-6 py-4">2023-10-25 14:30</td>
              <td className="px-6 py-4 font-medium text-white">PCB-2023-001</td>
              <td className="px-6 py-4">admin</td>
              <td className="px-6 py-4"><span className="px-2 py-1 bg-green-500/10 text-green-400 rounded-md text-xs">PASS</span></td>
              <td className="px-6 py-4 text-right text-blue-400 hover:text-blue-300 cursor-pointer">View</td>
            </tr>
            <tr className="hover:bg-zinc-800/30 transition-colors">
              <td className="px-6 py-4">2023-10-25 15:15</td>
              <td className="px-6 py-4 font-medium text-white">PCB-2023-002</td>
              <td className="px-6 py-4">tester1</td>
              <td className="px-6 py-4"><span className="px-2 py-1 bg-red-500/10 text-red-400 rounded-md text-xs">FAIL</span></td>
              <td className="px-6 py-4 text-right text-blue-400 hover:text-blue-300 cursor-pointer">View</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
