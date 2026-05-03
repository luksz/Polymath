"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { notesApi, type NoteCreate } from "@/lib/api/notes";
import { Plus, Search, FileText, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function NotesPage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["notes", search],
    queryFn: async () => {
      const token = await getToken();
      return notesApi.list(token!, search ? { q: search } : undefined);
    },
  });

  const createMutation = useMutation({
    mutationFn: async (note: NoteCreate) => {
      const token = await getToken();
      return notesApi.create(token!, note);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notes"] });
      setCreating(false);
      setNewTitle("");
      setNewBody("");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const token = await getToken();
      return notesApi.delete(token!, id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notes"] });
      setSelected(null);
    },
  });

  const notes = data?.items ?? [];
  const selectedNote = notes.find((n) => n.id === selected);

  return (
    <div className="flex h-full gap-6">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 space-y-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold">Notes</h1>
          <button
            onClick={() => setCreating(true)}
            className="rounded-md p-1.5 hover:bg-accent transition-colors"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search notes..."
            className="w-full rounded-md border border-border bg-background pl-8 pr-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          </div>
        ) : notes.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">No notes yet.</p>
        ) : (
          <ul className="space-y-1">
            {notes.map((note) => (
              <li key={note.id}>
                <button
                  onClick={() => setSelected(note.id)}
                  className={cn(
                    "w-full rounded-md px-3 py-2 text-left text-sm transition-colors",
                    selected === note.id
                      ? "bg-accent text-accent-foreground"
                      : "hover:bg-accent/50 text-muted-foreground"
                  )}
                >
                  <p className="font-medium truncate text-foreground">{note.title}</p>
                  <p className="text-xs truncate mt-0.5">{note.body_md.slice(0, 60)}</p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      {/* Main area */}
      <div className="flex-1">
        {creating ? (
          <div className="space-y-4 max-w-2xl">
            <h2 className="text-base font-semibold">New note</h2>
            <input
              autoFocus
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Title"
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <textarea
              value={newBody}
              onChange={(e) => setNewBody(e.target.value)}
              placeholder="Write in Markdown..."
              rows={12}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-ring resize-none"
            />
            <div className="flex gap-2">
              <button
                onClick={() => createMutation.mutate({ title: newTitle, body_md: newBody })}
                disabled={!newTitle || createMutation.isPending}
                className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background disabled:opacity-50"
              >
                {createMutation.isPending ? "Saving..." : "Save"}
              </button>
              <button
                onClick={() => setCreating(false)}
                className="rounded-md border border-border px-4 py-2 text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : selectedNote ? (
          <div className="space-y-4 max-w-2xl">
            <div className="flex items-start justify-between">
              <h2 className="text-xl font-semibold">{selectedNote.title}</h2>
              <button
                onClick={() => deleteMutation.mutate(selectedNote.id)}
                className="text-xs text-muted-foreground hover:text-destructive transition-colors"
              >
                Delete
              </button>
            </div>
            {selectedNote.tags.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {selectedNote.tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-accent px-2 py-0.5 text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            )}
            <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-muted-foreground">
              {selectedNote.body_md}
            </pre>
          </div>
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-muted-foreground">
            <FileText className="h-10 w-10 opacity-20" />
            <p className="text-sm">Select a note or create one</p>
          </div>
        )}
      </div>
    </div>
  );
}
