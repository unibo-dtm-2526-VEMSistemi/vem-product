import { useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import { type Product } from "@/data/mockProducts";
import PillarBadge from "./PillarBadge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

interface ProductCardProps {
  product: Product;
  onReviewSubmit?: (product: Product, problem: string) => void;
}

const ProductCard = ({ product, onReviewSubmit }: ProductCardProps) => {
  const [isReviewDialogOpen, setIsReviewDialogOpen] = useState(false);
  const [reviewProblem, setReviewProblem] = useState("");
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isReportedForReview, setIsReportedForReview] = useState(false);
  const isUnderReview = product.status === "review" || isReportedForReview;

  const handleSendReview = () => {
    const problem = reviewProblem.trim();
    if (!problem) return;

    onReviewSubmit?.(product, problem);
    setIsReportedForReview(true);
    setReviewProblem("");
    setIsReviewDialogOpen(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="bg-card rounded-lg border shadow-card overflow-hidden"
    >
      <button
        type="button"
        onClick={() => setIsCollapsed((prev) => !prev)}
        className="w-full bg-primary px-5 py-4 flex items-center justify-between text-left hover:opacity-95 transition-opacity"
        aria-expanded={!isCollapsed}
      >
        <div>
          <p className="text-primary-foreground/60 text-xs font-medium tracking-wider uppercase">
            Product Classification
          </p>
          <h3 className="text-primary-foreground font-display text-lg font-bold mt-0.5">{product.name}</h3>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-primary-foreground/70 font-mono text-sm font-semibold">{product.code}</span>
          {isCollapsed ? (
            <ChevronDown className="h-4 w-4 text-primary-foreground/80" />
          ) : (
            <ChevronUp className="h-4 w-4 text-primary-foreground/80" />
          )}
        </div>
      </button>

      {!isCollapsed && (
        <div className="p-5 space-y-4">
          <div className="flex items-center justify-between">
            <PillarBadge pillar={product.pillar} />
          <span
            className={`flex items-center gap-1.5 text-xs font-medium ${
              isUnderReview ? "text-amber-600" : "text-emerald-600"
            }`}
          >
            {isUnderReview ? (
              <AlertTriangle className="h-3.5 w-3.5" />
            ) : (
              <CheckCircle className="h-3.5 w-3.5" />
            )}
            {isUnderReview ? "To be reviewed" : "Consistent with Accounting"}
          </span>
        </div>

          <p className="text-sm text-muted-foreground leading-relaxed">{product.description}</p>

          <div className="grid grid-cols-2 gap-2">
            {Object.entries(product.specifications).map(([key, value]) => (
              <div key={key} className="bg-muted rounded-md px-3 py-2">
                <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">{key}</p>
                <p className="text-sm font-semibold text-foreground mt-0.5">{value}</p>
              </div>
            ))}
          </div>

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

          <div className="flex gap-2 pt-2">
            <button
              onClick={() => setIsCollapsed(true)}
              className="flex-1 py-2 px-4 rounded-md bg-primary text-primary-foreground text-xs font-semibold hover:opacity-90 transition-opacity"
            >
              Consistent with Accounting
            </button>
            <button
              onClick={() => setIsReviewDialogOpen(true)}
              disabled={isUnderReview}
              className="flex-1 py-2 px-4 rounded-md border-2 border-accent text-accent text-xs font-semibold hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              {isUnderReview ? "To be reviewed" : "Requires Review"}
            </button>
          </div>
        </div>
      )}

      <Dialog open={isReviewDialogOpen} onOpenChange={setIsReviewDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Describe problem</DialogTitle>
            <DialogDescription>
              Explain why this product classification should be reviewed.
            </DialogDescription>
          </DialogHeader>

          <Textarea
            value={reviewProblem}
            onChange={(event) => setReviewProblem(event.target.value)}
            placeholder="Write the issue details..."
            rows={5}
          />

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsReviewDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSendReview} disabled={!reviewProblem.trim()}>
              Send
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
};

export default ProductCard;
