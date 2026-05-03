import { apiRequest } from "../api-client";

export type Note = {
  id: string;
  user_id: string;
  title: string;
  body_md: string;
  tags: string[];
  created_at: string;
  updated_at: string;
};

export type NoteListResponse = {
  items: Note[];
  total: number;
};

export type NoteCreate = {
  title: string;
  body_md: string;
  tags?: string[];
};

export type NoteUpdate = {
  title?: string;
  body_md?: string;
  tags?: string[];
};

export const notesApi = {
  list: (token: string, params?: { q?: string; tag?: string; limit?: number; offset?: number }) =>
    apiRequest<NoteListResponse>(`/v1/notes?${new URLSearchParams(params as Record<string, string>)}`, { token }),

  get: (token: string, id: string) =>
    apiRequest<Note>(`/v1/notes/${id}`, { token }),

  create: (token: string, body: NoteCreate) =>
    apiRequest<Note>("/v1/notes", { method: "POST", body, token }),

  update: (token: string, id: string, body: NoteUpdate) =>
    apiRequest<Note>(`/v1/notes/${id}`, { method: "PUT", body, token }),

  delete: (token: string, id: string) =>
    apiRequest<void>(`/v1/notes/${id}`, { method: "DELETE", token }),

  search: (token: string, query: string, mode: "fts" | "semantic" | "hybrid" = "fts") =>
    apiRequest<Note[]>("/v1/notes/search", { method: "POST", body: { query, mode }, token }),
};
