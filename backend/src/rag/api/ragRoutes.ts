import type { RagQuery } from "../types";
import { AccountingAdvisorService } from "../service/accountingAdvisorService";

export function createRagHandlers(service: AccountingAdvisorService) {
  return {
    advise: async (payload: RagQuery) => service.advise(payload),
  };
}

