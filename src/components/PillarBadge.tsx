import { type PillarType } from "@/data/mockProducts";

const PILLAR_STYLES: Record<PillarType, string> = {
  "Technology Integration": "bg-pillar-technology text-primary-foreground",
  "Cyber Security": "bg-pillar-security text-primary-foreground",
  "Software Integration": "bg-pillar-software text-primary-foreground",
  "Cloud Integration": "bg-pillar-cloud text-primary-foreground",
};

interface PillarBadgeProps {
  pillar: PillarType;
  size?: "sm" | "md";
}

const PillarBadge = ({ pillar, size = "md" }: PillarBadgeProps) => {
  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full ${PILLAR_STYLES[pillar]} ${
        size === "sm" ? "text-[10px] px-2.5 py-0.5" : "text-xs px-3 py-1"
      }`}
    >
      {pillar}
    </span>
  );
};

export default PillarBadge;
