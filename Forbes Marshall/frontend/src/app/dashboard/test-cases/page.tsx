"use client";
export default function TestCasesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Test Cases</h1>
          <p className="mt-2 text-zinc-400">Manage and configure automated test cases.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-md transition-all">
          + New Test Case
        </button>
      </div>
      
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
        <table className="w-full text-left text-sm text-zinc-300">
          <thead className="bg-zinc-800/50 text-zinc-400 font-medium">
            <tr>
              <th className="px-6 py-4">ID</th>
              <th className="px-6 py-4">Name</th>
              <th className="px-6 py-4">Stage</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            <tr className="hover:bg-zinc-800/30 transition-colors">
              <td className="px-6 py-4">TC-001</td>
              <td className="px-6 py-4 font-medium text-white">Voltage Check - 5V Rail</td>
              <td className="px-6 py-4">Power On</td>
              <td className="px-6 py-4"><span className="px-2 py-1 bg-green-500/10 text-green-400 rounded-md text-xs">Active</span></td>
              <td className="px-6 py-4 text-right text-blue-400 hover:text-blue-300 cursor-pointer">Edit</td>
            </tr>
            <tr className="hover:bg-zinc-800/30 transition-colors">
              <td className="px-6 py-4">TC-002</td>
              <td className="px-6 py-4 font-medium text-white">Communication Ping</td>
              <td className="px-6 py-4">Diagnostics</td>
              <td className="px-6 py-4"><span className="px-2 py-1 bg-green-500/10 text-green-400 rounded-md text-xs">Active</span></td>
              <td className="px-6 py-4 text-right text-blue-400 hover:text-blue-300 cursor-pointer">Edit</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
