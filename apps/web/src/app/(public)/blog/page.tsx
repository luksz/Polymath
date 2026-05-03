import Link from "next/link";
import { contentApi } from "@/lib/api/content";

export const metadata = { title: "Writing" };

export default async function BlogPage() {
  let posts = [];
  try {
    posts = await contentApi.listPosts({ kind: "post" });
  } catch {
    // content-svc may not be running locally
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-20">
      <h1 className="text-3xl font-bold tracking-tight">Writing</h1>
      <p className="mt-3 text-muted-foreground">
        Essays, notes, and ideas on software, learning, and building.
      </p>

      <div className="mt-12 space-y-10">
        {posts.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing published yet.</p>
        ) : (
          posts.map((post) => (
            <article key={post.id} className="group space-y-2">
              <div className="flex items-baseline justify-between gap-4">
                <Link
                  href={`/blog/${post.slug}`}
                  className="text-lg font-semibold group-hover:underline underline-offset-4"
                >
                  {post.title}
                </Link>
                {post.published_at && (
                  <time className="flex-shrink-0 text-xs text-muted-foreground">
                    {new Date(post.published_at).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                  </time>
                )}
              </div>
              {post.summary && (
                <p className="text-sm text-muted-foreground">{post.summary}</p>
              )}
              <div className="flex gap-1.5">
                {post.tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-accent px-2 py-0.5 text-xs text-muted-foreground">
                    {tag}
                  </span>
                ))}
              </div>
            </article>
          ))
        )}
      </div>
    </div>
  );
}
