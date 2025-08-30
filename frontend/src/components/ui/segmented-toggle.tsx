import * as React from "react";
import { cn } from "../../lib/cn";

type Option<T extends string> = { label: string; value: T };

export function SegmentedToggle<T extends string>({
  options,
  value,
  onChange,
  className,
}: {
  options: Array<Option<T>>;
  value: T;
  onChange: (v: T) => void;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "relative inline-flex items-center gap-0.5 rounded-xl bg-white/30 p-1 text-xs shadow-md backdrop-blur-xl",
        className
      )}
      role="tablist"
    >
      {options.map((opt) => {
        const isActive = opt.value === value;
        return (
          <button
            key={opt.value}
            type="button"
            role="tab"
            aria-selected={isActive}
            className={cn(
              "relative flex-1 sm:flex-initial rounded-lg px-2 sm:px-3 py-1.5 transition-colors whitespace-nowrap",
              isActive
                ? "bg-gradient-to-br from-blue-600/90 to-indigo-600/90 text-white shadow-md"
                : "text-gray-700 hover:bg-white/40 hover:text-gray-900"
            )}
            onClick={() => onChange(opt.value)}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
