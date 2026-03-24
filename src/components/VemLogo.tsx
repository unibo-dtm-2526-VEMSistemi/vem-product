interface VemLogoProps {
  className?: string;
  variant?: "dark" | "light";
}

const VemLogo = ({ className = "", variant = "dark" }: VemLogoProps) => {
  const fill = variant === "light" ? "#FFFFFF" : "#003056";
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg viewBox="0 0 120 40" className="h-8 w-auto" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5 8L20 32L35 8H28L20 22L12 8H5Z" fill={fill} />
        <path d="M40 8V32H62V26H47V23H59V17H47V14H61V8H40Z" fill={fill} />
        <path d="M67 8V32H74V18L82 28L90 18V32H97V8H90L82 20L74 8H67Z" fill={fill} />
      </svg>
      <div className="flex flex-col leading-none">
        <span className={`text-[10px] font-bold tracking-[0.2em] ${variant === "light" ? "text-primary-foreground" : "text-primary"}`}>
          DRIVING
        </span>
        <span className={`text-[10px] font-bold tracking-[0.2em] ${variant === "light" ? "text-primary-foreground" : "text-primary"}`}>
          DIGITAL
        </span>
      </div>
    </div>
  );
};

export default VemLogo;
