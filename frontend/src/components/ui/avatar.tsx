import * as React from "react";
import { cn } from "../../lib/cn";

export function Avatar({
  src,
  alt,
  className,
}: {
  src?: string;
  alt?: string;
  className?: string;
}) {
  return (
    <img
      src={
        src ??
        `https://api.dicebear.com/9.x/initials/svg?seed=${encodeURIComponent(alt ?? "U")}`
      }
      alt={alt}
      className={cn("h-8 w-8 rounded-full object-cover", className)}
    />
  );
}
