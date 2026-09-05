'use client';

import React, { useEffect, useState } from 'react';

interface NumberTickerProps {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  isCurrency?: boolean;
  className?: string;
}

export default function NumberTicker({
  value,
  prefix = '',
  suffix = '',
  decimals = 0,
  isCurrency = false,
  className = '',
}: NumberTickerProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTimestamp: number | null = null;
    const duration = 1200; // ms
    const startValue = 0;
    const endValue = value;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      // Ease out cubic
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = startValue + (endValue - startValue) * easeOut;
      setDisplayValue(current);

      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        setDisplayValue(endValue);
      }
    };

    window.requestAnimationFrame(step);
  }, [value]);

  const formatted = isCurrency
    ? displayValue.toLocaleString('en-IN', {
        maximumFractionDigits: decimals,
        minimumFractionDigits: decimals,
      })
    : decimals > 0
    ? displayValue.toFixed(decimals)
    : Math.round(displayValue).toLocaleString('en-IN');

  return (
    <span className={`inline-block tabular-nums font-bold ${className}`}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
}
