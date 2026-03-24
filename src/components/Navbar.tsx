import { ExternalLink } from "lucide-react";
import VemLogo from "./VemLogo";

interface NavbarProps {
  variant?: "light" | "dark";
}

const Navbar = ({ variant = "dark" }: NavbarProps) => {
  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-between px-8 ${
      variant === "dark" ? "bg-primary/95 backdrop-blur-md" : "bg-background/95 backdrop-blur-md border-b"
    }`}>
      <VemLogo variant={variant === "dark" ? "light" : "dark"} />
      <a
        href="https://vfrfrgtcjhfxfgxd.lovable.app"
        target="_blank"
        rel="noopener noreferrer"
        className={`flex items-center gap-1.5 text-sm font-medium transition-colors hover:opacity-80 ${
          variant === "dark" ? "text-primary-foreground/80 hover:text-primary-foreground" : "text-muted-foreground hover:text-foreground"
        }`}
      >
        Sustainability Report 2024
        <ExternalLink className="h-3.5 w-3.5" />
      </a>
    </nav>
  );
};

export default Navbar;
