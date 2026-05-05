"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { digestApi, type DigestListItem } from "@/lib/api/digest";
import { Loader2, Play, ExternalLink, Lightbulb, Zap, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 8 ? "bg-green-500/20 text-green-400" :
    score >= 5 ? "bg-yellow-500/20 text-yellow-400" :
    "bg-muted text-muted-foreground";
  return (
    <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", color)}>
      {score}/10
    </span>
  );
}

export default function DigestPage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const { data: list, isLoading: listLoading } = useQuery({
    queryKey: ["digests"],
    queryFn: async () => {
      const token = await getToken();
      return digestApi.list(token!);
    },
  });

  const todayStr = new Date().toISOString().split("T")[0];
  const activeDate = selectedDate ?? todayStr;

  const { data: digest, isLoading: digestLoading } = useQuery({
    queryKey: ["digest", activeDate],
    queryFn: async () => {
      const token = await getToken();
      return digestApi.getByDate(token!, activeDate);
    },
    retry: false,
  });

  const triggerMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      return digestApi.triggerRun(token!);
    },
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["digest", activeDate] });
        queryClient.invalidateQueries({ queryKey: ["digests"] });
      }, 3000);
    },
  });

  return (
    <div className="flex h-full gap-6">
      {/* Calendar sidebar */}
      <aside className="w-52 flex-shrink-0 space-y-3">
        <h1 className="text-lg font-semibold">Daily Digest</h1>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Top research papers condensed to a 5-min read, delivered every morning.
        </p>

        <button
          onClick={() => triggerMutation.mutate()}
          disabled={triggerMutation.isPending || digest?.status === "running"}
          className="flex w-full items-center gap-2 rounded-md bg-foreground px-3 py-2 text-xs font-medium text-background disabled:opacity-50 transition-opacity"
        >
          {triggerMutation.isPending || digest?.status === "running" ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <Play className="h-3 w-3" />
          )}
          Run now
        </button>

        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-1">History</p>
          {listLoading ? (
            <Loader2 className="h-3 w-3 animate-spin text-muted-foreground ml-1" />
          ) : !list?.length ? (
            <p className="text-xs text-muted-foreground px-1">No digests yet.</p>
          ) : (
            list.map((item: DigestListItem) => (
              <button
                key={item.id}
                onClick={() => setSelectedDate(item.for_date)}
                className={cn(
                  "w-full rounded-md px-3 py-2 text-left transition-colors",
                  activeDate === item.for_date
                    ? "bg-accent text-accent-foreground"
                    : "hover:bg-accent/50 text-muted-foreground"
                )}
              >
                <p className="text-xs font-medium text-foreground">{item.for_date}</p>
                <p className="text-xs">
                  {item.paper_count} paper{item.paper_count !== 1 ? "s" : ""} · {item.status}
                </p>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 overflow-y-auto space-y-6">
        {digestLoading ? (
          <div className="flex h-40 items-center justify-center">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        ) : !digest ? (
          <div className="flex h-40 flex-col items-center justify-center gap-3 text-muted-foreground">
            <BookOpen className="h-10 w-10 opacity-20" />
            <p className="text-sm">No digest for {activeDate} yet.</p>
            <p className="text-xs">Hit "Run now" to generate one.</p>
          </div>
        ) : digest.status === "running" || digest.status === "pending" ? (
          <div className="flex h-40 flex-col items-center justify-center gap-3 text-muted-foreground">
            <Loader2 className="h-8 w-8 animate-spin opacity-40" />
            <p className="text-sm">Fetching and summarising papers…</p>
            <p className="text-xs">This takes about 30–60 seconds.</p>
          </div>
        ) : digest.status === "failed" ? (
          <div className="flex h-40 flex-col items-center justify-center gap-3 text-muted-foreground">
            <p className="text-sm text-red-400">Digest failed. Try running again.</p>
          </div>
        ) : (
          <>
            <div>
              <h2 className="text-xl font-semibold">
                {new Date(digest.for_date).toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {digest.papers.length} papers · topics: {digest.topic_tags.join(", ")}
              </p>
            </div>

            {digest.papers.map((paper, i) => (
              <article
                key={paper.id}
                className="rounded-lg border border-border p-6 space-y-4"
              >
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 flex-shrink-0 text-xs font-bold text-muted-foreground w-5">
                    #{i + 1}
                  </span>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-start gap-2 flex-wrap">
                      <h3 className="text-base font-semibold leading-snug">{paper.title}</h3>
                      <ScoreBadge score={paper.relevance_score} />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {paper.authors.slice(0, 3).join(", ")}
                      {paper.authors.length > 3 ? " et al." : ""}
                    </p>
                  </div>
                  <a
                    href={paper.arxiv_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>

                <p className="text-sm font-medium text-foreground pl-8">{paper.summary_headline}</p>

                <p className="text-sm text-muted-foreground leading-relaxed pl-8">
                  {paper.summary_body}
                </p>

                {(paper.key_insight || paper.why_it_matters) && (
                  <div className="pl-8 grid gap-3 sm:grid-cols-2">
                    {paper.key_insight && (
                      <div className="rounded-md bg-accent/50 p-3 space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
                          <Lightbulb className="h-3 w-3" /> Key insight
                        </div>
                        <p className="text-xs text-muted-foreground">{paper.key_insight}</p>
                      </div>
                    )}
                    {paper.why_it_matters && (
                      <div className="rounded-md bg-accent/50 p-3 space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
                          <Zap className="h-3 w-3" /> Why it matters
                        </div>
                        <p className="text-xs text-muted-foreground">{paper.why_it_matters}</p>
                      </div>
                    )}
                  </div>
                )}
              </article>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
