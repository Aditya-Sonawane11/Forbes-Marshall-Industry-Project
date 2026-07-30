"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { name: "Overview", path: "/dashboard" },
  { name: "Start Test", path: "/dashboard/test" },
  { name: "Test Cases", path: "/dashboard/test-cases" },
  { name: "History", path: "/dashboard/history" },
  { name: "Stages", path: "/dashboard/stages" },
  { name: "Advanced", path: "/dashboard/advanced" },
  { name: "Diagrams", path: "/dashboard/diagrams" },
  { name: "Config", path: "/dashboard/config" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen bg-zinc-900 border-r border-zinc-800 flex flex-col fixed left-0 top-0">
      <div className="h-16 flex items-center px-6 border-b border-zinc-800">
        <span className="font-bold text-lg text-white tracking-wide">PCB TESTER</span>
      </div>
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.path;
          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive
                  ? "bg-blue-600/10 text-blue-500 font-medium"
                  : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
              }`}
            >
              {item.name}
            </Link>
          );
        })}
      </div>
      <div className="p-4 border-t border-zinc-800">
        <Link
          href="/login"
          className="flex items-center justify-center w-full px-4 py-2 text-sm text-zinc-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
        >
          Logout
        </Link>
      </div>
    </aside>
  );
}
