import { apiRequest } from "../api-client";

export type DigestPaper = {
  id: string;
  arxiv_id: string;
  title: string;
  authors: string[];
  arxiv_url: string;
  relevance_score: number;
  summary_headline: string;
  summary_body: string;
  key_insight: string;
  why_it_matters: string;
  created_at: string;
};

export type Digest = {
  id: string;
  for_date: string;
  topic_tags: string[];
  status: "pending" | "running" | "done" | "failed";
  created_at: string;
  papers: DigestPaper[];
};

export type DigestListItem = {
  id: string;
  for_date: string;
  status: string;
  paper_count: number;
  created_at: string;
};

export const digestApi = {
  list: (token: string) =>
    apiRequest<DigestListItem[]>("/v1/digests", { token }),

  getToday: (token: string) =>
    apiRequest<Digest>("/v1/digests/today", { token }),

  getByDate: (token: string, date: string) =>
    apiRequest<Digest>(`/v1/digests/${date}`, { token }),

  triggerRun: (token: string) =>
    apiRequest<{ status: string }>("/v1/digests/run", { method: "POST", token }),
};
