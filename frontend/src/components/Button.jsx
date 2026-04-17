import { cn } from "../lib/utils";
import { ArrowRight } from "lucide-react";

export const Button = ({ children, variant = "primary", size = "default", className, showIcon = true, ...props }) => {
  const variants = {
    primary: "bg-accent text-white shadow-pop hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[6px_6px_0px_0px_#1E293B] active:translate-x-[2px] active:translate-y-[2px] active:shadow-[2px_2px_0px_0px_#1E293B]",
    secondary: "bg-white text-fg shadow-pop hover:bg-tertiary",
    ghost: "bg-transparent text-fg hover:text-accent font-bold",
    candy: "bg-secondary text-white shadow-pop hover:bg-pink-400",
  };

  const sizes = {
    default: "h-14 px-8 text-lg font-bold",
    lg: "h-16 px-10 text-xl font-extrabold",
    sm: "h-12 px-6 text-base font-bold",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-full border-2 border-[#1E293B] transition-all duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)] disabled:opacity-50 disabled:pointer-events-none",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
      {showIcon && variant === "primary" && (
        <div className="ml-3 bg-white text-accent p-1 rounded-full border-2 border-[#1E293B]">
          <ArrowRight size={18} strokeWidth={3} />
        </div>
      )}
    </button>
  );
};
