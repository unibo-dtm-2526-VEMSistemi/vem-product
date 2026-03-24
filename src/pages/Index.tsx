import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Shield, Server, Code, Cloud } from "lucide-react";
import Navbar from "@/components/Navbar";
import heroBg from "@/assets/vem-hero-bg.jpg";

const PILLARS = [
  { icon: Server, title: "Technology Integration", tip: "Hardware infrastructure, networking equipment, and physical technology solutions." },
  { icon: Shield, title: "Cyber Security", tip: "Security monitoring, threat detection, and compliance solutions." },
  { icon: Code, title: "Software Integration", tip: "Software licensing, custom development, and application integration." },
  { icon: Cloud, title: "Cloud Integration", tip: "Cloud hosting, migration services, and managed cloud infrastructure." },
];

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      <Navbar variant="dark" />

      {/* Hero */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        <img
          src={heroBg}
          alt=""
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-primary/70" />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="relative z-10 text-center max-w-3xl px-6"
        >
          <h1 className="font-display text-4xl md:text-6xl font-bold text-primary-foreground leading-tight">
            VEM Driving Digital:
            <br />
            <span className="text-accent">Smart Inventory Assistant</span>
          </h1>
          <p className="mt-6 text-lg text-primary-foreground/70 max-w-xl mx-auto">
            Empowering Human Value through AI-driven Competence
          </p>
          <button
            onClick={() => navigate("/chat")}
            className="mt-10 inline-flex items-center gap-2 bg-accent text-accent-foreground px-8 py-4 rounded-lg text-base font-semibold hover:opacity-90 transition-opacity shadow-elevated"
          >
            Analyze Product Code
            <ArrowRight className="h-5 w-5" />
          </button>
        </motion.div>
      </section>

      {/* Pillars */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.h2
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="font-display text-3xl font-bold text-foreground text-center"
          >
            4 Pillar Strategy
          </motion.h2>
          <p className="text-center text-muted-foreground mt-3 max-w-lg mx-auto">
            Classify and retrieve product data aligned with VEM Group's strategic pillars.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-14">
            {PILLARS.map((p, i) => (
              <motion.div
                key={p.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group bg-card border rounded-xl p-6 hover:shadow-elevated transition-shadow cursor-default"
              >
                <div className="w-12 h-12 rounded-lg bg-primary flex items-center justify-center mb-4 group-hover:bg-accent transition-colors">
                  <p.icon className="h-6 w-6 text-primary-foreground" />
                </div>
                <h3 className="font-display font-semibold text-foreground text-sm">{p.title}</h3>
                <p className="text-xs text-muted-foreground mt-2 leading-relaxed">{p.tip}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
