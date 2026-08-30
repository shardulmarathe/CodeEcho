"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  getBudget,
  getHealth,
  warmBackend,
  type HealthStatus,
} from "@/lib/api";
import type { BudgetStatus } from "@/lib/types";

export type WakeState = "checking" | "waking" | "ready" | "unavailable";

export function useServiceReadiness() {
  const [wakeState, setWakeState] = useState<WakeState>("checking");
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [budget, setBudget] = useState<BudgetStatus | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const refreshBudget = useCallback(() => {
    getBudget().then(setBudget).catch(() => {});
  }, []);

  const check = useCallback(() => {
    warmBackend();
    const controller = new AbortController();
    const slowTimer = window.setTimeout(() => setWakeState("waking"), 1200);
    const timeoutTimer = window.setTimeout(() => controller.abort(), 70000);

    getHealth({ signal: controller.signal, cache: "no-store" })
      .then((result) => {
        setHealth(result);
        setError(null);
        setWakeState("ready");
        refreshBudget();
      })
      .catch((reason) => {
        const next =
          reason instanceof ApiError
            ? reason
            : new ApiError(
                "The free-tier server is still waking or unavailable. Wait a moment, then try again.",
                "server_unavailable"
              );
        setError(next);
        setWakeState("unavailable");
      })
      .finally(() => {
        window.clearTimeout(slowTimer);
        window.clearTimeout(timeoutTimer);
      });

    return () => {
      controller.abort();
      window.clearTimeout(slowTimer);
      window.clearTimeout(timeoutTimer);
    };
  }, [refreshBudget]);

  useEffect(() => check(), [check]);

  return { wakeState, health, budget, error, retry: check, refreshBudget };
}
