export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login/",
    REFRESH: "/auth/refresh/",
    LOGOUT: "/auth/logout/",
    ME: "/auth/me/",
  },
  RUNS: {
    LIST: "/runs/",
    DETAIL: (pk: number) => `/runs/${pk}/`,
    MULTIQC_REPORT: (pk: number) => `/runs/${pk}/multiqc-report/`,
    METRICS: (pk: number) => `/runs/${pk}/metrics/`,
    CHAT: (pk: number) => `/runs/${pk}/chat/`,
    CHAT_STREAM: (pk: number) => `/runs/${pk}/chat/stream/`,
  },
  HEALTH: "/health/",
} as const
