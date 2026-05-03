"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { contentApi, type Post } from "@/lib/api/content";
import { Plus, FileText, Globe, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function WritingPage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ slug: "", kind: "post", title: "", body_mdx: "", summary: "" });

  const { data: posts, isLoading } = useQuery({
    queryKey: ["writing"],
    queryFn: async () => {
      const token = await getToken();
      return contentApi.listPosts();
    },
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      return contentApi.createPost(token!, { slug: form.slug, kind: form.kind, title: form.title, body_mdx: form.body_mdx, summary: form.summary });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["writing"] });
      setCreating(false);
      setForm({ slug: "", kind: "post", title: "", body_mdx: "", summary: "" });
    },
  });

  const publishMutation = useMutation({
    mutationFn: async (postId: string) => {
      const token = await getToken();
      return contentApi.publishPost(token!, postId);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["writing"] }),
  });

  const allPosts: Post[] = posts ?? [];
  const selectedPost = allPosts.find((p) => p.id === selected);

  return (
    <div className="flex h-full gap-6">
      <aside className="w-64 flex-shrink-0 space-y-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold">Writing</h1>
          <button onClick={() => setCreating(true)} className="rounded-md p-1.5 hover:bg-accent transition-colors">
            <Plus className="h-4 w-4" />
          </button>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="h-4 w-4 animate-spin text-muted-foreground" /></div>
        ) : allPosts.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">No posts yet.</p>
        ) : (
          <ul className="space-y-1">
            {allPosts.map((post) => (
              <li key={post.id}>
                <button
                  onClick={() => setSelected(post.id)}
                  className={cn(
                    "w-full rounded-md px-3 py-2 text-left text-sm transition-colors",
                    selected === post.id ? "bg-accent text-accent-foreground" : "hover:bg-accent/50 text-muted-foreground"
                  )}
                >
                  <div className="flex items-center gap-2">
                    {post.status === "published" ? <Globe className="h-3 w-3 text-green-500 flex-shrink-0" /> : <FileText className="h-3 w-3 flex-shrink-0" />}
                    <span className="truncate font-medium text-foreground">{post.title}</span>
                  </div>
                  <p className="text-xs mt-0.5 pl-5 capitalize">{post.kind} · {post.status}</p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <div className="flex-1">
        {creating ? (
          <div className="space-y-4 max-w-2xl">
            <h2 className="text-base font-semibold">New post</h2>
            <div className="grid grid-cols-2 gap-3">
              <input placeholder="slug (e.g. my-first-post)" value={form.slug}
                onChange={(e) => setForm({ ...form, slug: e.target.value })}
                className="col-span-2 rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              <input placeholder="Title" value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="col-span-2 rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
              <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}
                className="rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none">
                <option value="post">Post</option>
                <option value="project">Project</option>
                <option value="page">Page</option>
                <option value="log">Log</option>
              </select>
              <input placeholder="Summary (optional)" value={form.summary}
                onChange={(e) => setForm({ ...form, summary: e.target.value })}
                className="rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
            </div>
            <textarea placeholder="Write in MDX..." value={form.body_mdx}
              onChange={(e) => setForm({ ...form, body_mdx: e.target.value })}
              rows={14}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-ring resize-none" />
            <div className="flex gap-2">
              <button onClick={() => createMutation.mutate()} disabled={!form.slug || !form.title || createMutation.isPending}
                className="rounded-md bg-foreground px-4 py-2 text-sm font-medium text-background disabled:opacity-50">
                {createMutation.isPending ? "Saving..." : "Save draft"}
              </button>
              <button onClick={() => setCreating(false)} className="rounded-md border border-border px-4 py-2 text-sm">Cancel</button>
            </div>
          </div>
        ) : selectedPost ? (
          <div className="space-y-4 max-w-2xl">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-semibold">{selectedPost.title}</h2>
                <p className="text-xs text-muted-foreground mt-1 capitalize">{selectedPost.kind} · {selectedPost.status}</p>
              </div>
              {selectedPost.status === "draft" && (
                <button onClick={() => publishMutation.mutate(selectedPost.id)}
                  disabled={publishMutation.isPending}
                  className="flex items-center gap-1.5 rounded-md bg-foreground px-3 py-1.5 text-xs font-medium text-background disabled:opacity-50">
                  <Globe className="h-3 w-3" />
                  {publishMutation.isPending ? "Publishing..." : "Publish"}
                </button>
              )}
            </div>
            <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-muted-foreground">
              {selectedPost.body_mdx ?? "No content."}
            </pre>
          </div>
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-muted-foreground">
            <FileText className="h-10 w-10 opacity-20" />
            <p className="text-sm">Select a post or create one</p>
          </div>
        )}
      </div>
    </div>
  );
}
