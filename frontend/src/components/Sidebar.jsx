function Sidebar() {
  return (
    <aside className="w-64 min-h-screen border-r border-gray-200 bg-white p-6">
      <div className="mb-10">
        <h1 className="text-2xl font-bold">NetDoc AI</h1>
        <p className="text-sm text-gray-500">Network Intelligence</p>
      </div>

      <nav className="space-y-2">
        <p className="rounded-lg bg-gray-100 px-4 py-3 font-medium">
          Dashboard
        </p>

        <p className="px-4 py-3 text-gray-600">Projects</p>

        <p className="px-4 py-3 text-gray-600">Devices</p>

        <p className="px-4 py-3 text-gray-600">Analyzer</p>

        <p className="px-4 py-3 text-gray-600">Reports</p>

        <p className="px-4 py-3 text-gray-600">Settings</p>
      </nav>
    </aside>
  );
}

export default Sidebar;
