import { motion } from "framer-motion";
import { CheckCircle, AlertTriangle } from "lucide-react";
import { type Product } from "@/data/mockProducts";
import PillarBadge from "./PillarBadge";

interface ProductCardProps {
  product: Product;
}

const ProductCard = ({ product }: ProductCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="bg-card rounded-lg border shadow-card overflow-hidden"
    >
      {/* Header */}
      <div className="bg-primary px-5 py-4 flex items-center justify-between">
        <div>
          <p className="text-primary-foreground/60 text-xs font-medium tracking-wider uppercase">Product Classification</p>
          <h3 className="text-primary-foreground font-display text-lg font-bold mt-0.5">{product.name}</h3>
        </div>
        <span className="text-primary-foreground/70 font-mono text-sm font-semibold">{product.code}</span>
      </div>

      <div className="p-5 space-y-4">
        {/* Pillar & Status */}
        <div className="flex items-center justify-between">
          <PillarBadge pillar={product.pillar} />
          <span className={`flex items-center gap-1.5 text-xs font-medium ${
            product.status === "active" ? "text-emerald-600" : "text-amber-600"
          }`}>
            {product.status === "active" ? (
              <CheckCircle className="h-3.5 w-3.5" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5" />
            )}
            {product.status === "active" ? "Consistent with Accounting" : "Requires Review"}
          </span>
        </div>

        <p className="text-sm text-muted-foreground leading-relaxed">{product.description}</p>

        {/* Specs Grid */}
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(product.specifications).map(([key, value]) => (
            <div key={key} className="bg-muted rounded-md px-3 py-2">
              <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">{key}</p>
              <p className="text-sm font-semibold text-foreground mt-0.5">{value}</p>
            </div>
          ))}
        </div>

        {/* Tax & Accounting */}
        <div className="border-t pt-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Tax Code (HS)</span>
            <span className="font-mono font-semibold text-foreground">{product.taxCode}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Accounting Rule</span>
            <span className="font-medium text-foreground text-right max-w-[60%]">{product.accountingRule}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Vendor</span>
            <span className="font-medium text-foreground">{product.vendor}</span>
          </div>
        </div>

        {/* Feedback Buttons */}
        <div className="flex gap-2 pt-2">
          <button className="flex-1 py-2 px-4 rounded-md bg-primary text-primary-foreground text-xs font-semibold hover:opacity-90 transition-opacity">
            ✓ Consistent with Accounting
          </button>
          <button className="flex-1 py-2 px-4 rounded-md border-2 border-accent text-accent text-xs font-semibold hover:bg-accent hover:text-accent-foreground transition-colors">
            ⚠ Requires Review
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default ProductCard;
