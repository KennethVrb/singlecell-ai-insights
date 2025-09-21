import { useQuery } from "@tanstack/react-query";
import { fetchReports } from "../api";

export function useReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: fetchReports
  });
}
