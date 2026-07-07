export default function UnderConstructionNotice() {
  return (
    <div className="pointer-events-none fixed inset-0 z-[80] grid place-items-center px-5 text-center">
      <p className="select-none rounded-xl border border-slate-300/80 bg-white/85 px-6 py-3 text-3xl font-black uppercase tracking-normal text-slate-950 shadow-xl shadow-slate-900/15 sm:text-5xl">
        Under Construction
      </p>
    </div>
  );
}
