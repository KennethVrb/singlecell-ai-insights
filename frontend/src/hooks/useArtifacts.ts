import { useQuery } from "@tanstack/react-query";
import { fetchArtifacts } from "../api";

export function useArtifacts(reportId: string | null) {
  return useQuery({
    queryKey: ["artifacts", reportId],
    queryFn: () => {
      if (!reportId) {
        throw new Error("reportId is required");
      }
      return fetchArtifacts(reportId);
    },
    enabled: Boolean(reportId)
  });
}
