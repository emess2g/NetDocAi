function StatCard({ title, value }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#0d131d] px-4 py-3">
      <p className="text-xs font-medium text-slate-500">{title}</p>

      <p className="mt-1 text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

export default StatCard;
