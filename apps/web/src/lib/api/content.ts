import { apiRequest } from "../api-client";

export type Post = {
  id: string;
  slug: string;
  kind: "post" | "project" | "page" | "log";
  title: string;
  summary: string | null;
  tags: string[];
  status: string;
  published_at: string | null;
  cover_image_url: string | null;
  reading_minutes: number | null;
  created_at: string;
  updated_at: string;
};

export type PostDetail = Post & { body_mdx: string };

export type ReadingLogEntry = {
  id: string;
  title: string;
  url: string | null;
  source: string | null;
  finished_on: string | null;
  rating: number | null;
  notes_md: string | null;
  tags: string[];
  created_at: string;
};

export const contentApi = {
  listPosts: (params?: { kind?: string; tag?: string; limit?: number }) =>
    apiRequest<Post[]>(`/v1/content/posts?${new URLSearchParams(params as Record<string, string>)}`),

  getPost: (slug: string) =>
    apiRequest<PostDetail>(`/v1/content/posts/${slug}`),

  createPost: (token: string, body: { slug: string; kind: string; title: string; body_mdx: string; summary?: string; tags?: string[] }) =>
    apiRequest<Post>("/v1/content/posts", { method: "POST", body, token }),

  updatePost: (token: string, id: string, body: Partial<{ title: string; body_mdx: string; summary: string; tags: string[]; status: string }>) =>
    apiRequest<Post>(`/v1/content/posts/${id}`, { method: "PUT", body, token }),

  publishPost: (token: string, id: string) =>
    apiRequest<Post>(`/v1/content/posts/${id}/publish`, { method: "POST", token }),

  listReadingLog: () =>
    apiRequest<ReadingLogEntry[]>("/v1/content/reading-log"),

  addReadingLog: (token: string, body: { title: string; url?: string; source?: string; finished_on?: string; rating?: number; notes_md?: string }) =>
    apiRequest<ReadingLogEntry>("/v1/content/reading-log", { method: "POST", body, token }),
};
