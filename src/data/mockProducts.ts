export type PillarType = "Technology Integration" | "Cyber Security" | "Software Integration" | "Cloud Integration";

export interface Product {
  code: string;
  name: string;
  pillar: PillarType;
  description: string;
  taxCode: string;
  accountingRule: string;
  vendor: string;
  status: "active" | "review";
  specifications: Record<string, string>;
}

export const PILLAR_CONFIG: Record<PillarType, { color: string; icon: string; description: string }> = {
  "Technology Integration": {
    color: "pillar-technology",
    icon: "🔧",
    description: "Hardware infrastructure, networking equipment, and physical technology solutions.",
  },
  "Cyber Security": {
    color: "pillar-security",
    icon: "🛡️",
    description: "Security monitoring, threat detection, and compliance solutions.",
  },
  "Software Integration": {
    color: "pillar-software",
    icon: "💻",
    description: "Software licensing, custom development, and application integration.",
  },
  "Cloud Integration": {
    color: "pillar-cloud",
    icon: "☁️",
    description: "Cloud hosting, migration services, and managed cloud infrastructure.",
  },
};

export const MOCK_PRODUCTS: Product[] = [
  {
    code: "VEM-TECH-X",
    name: "Cisco Nexus Switch",
    pillar: "Technology Integration",
    description: "Enterprise-grade data center switching platform with high-density 100G ports for mission-critical workloads.",
    taxCode: "8471.50.00",
    accountingRule: "Capitalized – 5yr straight-line depreciation (Hardware Asset)",
    vendor: "Cisco Systems",
    status: "active",
    specifications: {
      "Model": "Nexus 9300-GX",
      "Ports": "36x 100G QSFP28",
      "Throughput": "3.6 Tbps",
      "PoE Budget": "N/A",
      "Form Factor": "1RU",
    },
  },
  {
    code: "VEM-CYBER-S",
    name: "Certego Sentinel",
    pillar: "Cyber Security",
    description: "AI-powered threat detection and response platform with 24/7 SOC monitoring and automated incident response.",
    taxCode: "8523.49.45",
    accountingRule: "OpEx – Annual subscription (SaaS Security Service)",
    vendor: "Certego S.r.l.",
    status: "active",
    specifications: {
      "Coverage": "Endpoint + Network",
      "SLA": "99.95% uptime",
      "Response Time": "< 15 min (P1)",
      "Compliance": "ISO 27001, GDPR",
      "Integration": "SIEM, SOAR compatible",
    },
  },
  {
    code: "VEM-SOFT-M",
    name: "MyDav License",
    pillar: "Software Integration",
    description: "Enterprise collaboration and document management platform with advanced workflow automation capabilities.",
    taxCode: "8523.49.31",
    accountingRule: "OpEx – Monthly license per-seat (Software License)",
    vendor: "MyDev S.r.l.",
    status: "active",
    specifications: {
      "Users": "Unlimited",
      "Storage": "500 GB included",
      "API Access": "RESTful + GraphQL",
      "SSO": "SAML 2.0 / OIDC",
      "Deployment": "SaaS / On-premise",
    },
  },
  {
    code: "VEM-CLOUD-01",
    name: "Neen Managed Cloud",
    pillar: "Cloud Integration",
    description: "Fully managed private cloud infrastructure with auto-scaling, backup, and disaster recovery included.",
    taxCode: "8471.49.00",
    accountingRule: "OpEx – Monthly consumption-based (IaaS)",
    vendor: "Neen S.r.l.",
    status: "review",
    specifications: {
      "Provider": "Multi-cloud (AWS / Azure)",
      "vCPU Range": "2–128 cores",
      "RAM Range": "4–512 GB",
      "Backup": "Daily + 30-day retention",
      "DR": "Active-passive failover",
    },
  },
];

export function findProduct(code: string): Product | undefined {
  return MOCK_PRODUCTS.find(
    (p) => p.code.toLowerCase() === code.trim().toLowerCase()
  );
}

export function searchProducts(query: string): Product[] {
  const q = query.toLowerCase();
  return MOCK_PRODUCTS.filter(
    (p) =>
      p.code.toLowerCase().includes(q) ||
      p.name.toLowerCase().includes(q) ||
      p.pillar.toLowerCase().includes(q)
  );
}
