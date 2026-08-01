import { useEffect, useRef, useState } from 'react';

interface ProgressBarProps {
  percent: number;
  label?: string;
  className?: string;
  height?: string;
}

export default function ProgressBar({
  percent,
  label,
  className = '',
  height = 'h-2',
}: ProgressBarProps) {
  const [width, setWidth] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setWidth(percent);
          observer.unobserve(el);
        }
      },
      { threshold: 0.3 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [percent]);

  return (
    <div ref={ref} className={className}>
      {label && (
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-semibold text-navy-600">{label}</span>
          <span className="text-[11px] font-bold text-emerald-700">{percent}%</span>
        </div>
      )}
      <div className={`progress-bar-track ${height}`}>
        <div
          className="progress-bar-fill"
          style={{ width: `${width}%`, transition: 'width 1.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
        />
      </div>
    </div>
  );
}
