export default function UnderConstructionNotice() {
  return (
    <div className="pointer-events-none fixed inset-0 z-[60] grid place-items-center px-5 text-center">
      <p className="select-none rounded-lg bg-white/45 px-5 py-3 text-3xl font-extrabold uppercase tracking-normal text-slate-600/85 shadow-sm sm:text-5xl">
        Under Construction
      </p>
    </div>
  );
}
