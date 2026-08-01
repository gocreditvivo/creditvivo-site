import { useEffect, useRef, useState, type ReactNode, type CSSProperties } from 'react';

type RevealVariant = 'up' | 'left' | 'right' | 'scale' | 'fade';

interface ScrollRevealProps {
  children: ReactNode;
  variant?: RevealVariant;
  delay?: number;
  className?: string;
  threshold?: number;
  rootMargin?: string;
}

const variantClass: Record<RevealVariant, string> = {
  up: 'reveal',
  left: 'reveal reveal-reveal-left',
  right: 'reveal reveal-reveal-right',
  scale: 'reveal reveal-scale',
  fade: 'reveal reveal-fade',
};

export default function ScrollReveal({
  children,
  variant = 'up',
  delay = 0,
  className = '',
  threshold = 0.15,
  rootMargin = '0px 0px -60px 0px',
}: ScrollRevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold, rootMargin }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  const style: CSSProperties = delay > 0
    ? { animationDelay: `${delay}s` }
    : {};

  return (
    <div
      ref={ref}
      className={`${variantClass[variant]} ${visible ? 'reveal-visible' : ''} ${className}`}
      style={style}
    >
      {children}
    </div>
  );
}
