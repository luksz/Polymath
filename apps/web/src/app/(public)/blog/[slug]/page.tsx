import { notFound } from "next/navigation";
import Link from "next/link";
import { contentApi } from "@/lib/api/content";

type Props = { params: Promise<{ slug: string }> };

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;

  let post;
  try {
    post = await contentApi.getPost(slug);
  } catch {
    notFound();
  }

  if (!post) notFound();

  return (
    <div className="mx-auto max-w-2xl px-6 py-20">
      <Link
        href="/blog"
        className="text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        ← Writing
      </Link>

      <div className="mt-8 space-y-4">
        <h1 className="text-3xl font-bold tracking-tight">{post.title}</h1>
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          {post.published_at && (
            <time>
              {new Date(post.published_at).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </time>
          )}
          {post.reading_minutes && <span>{post.reading_minutes} min read</span>}
        </div>
        {post.tags.length > 0 && (
          <div className="flex gap-1.5">
            {post.tags.map((tag) => (
              <span key={tag} className="rounded-full bg-accent px-2 py-0.5 text-xs">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-10 prose prose-invert max-w-none">
        <pre className="whitespace-pre-wrap font-sans text-sm leading-7 text-foreground">
          {post.body_mdx}
        </pre>
      </div>
    </div>
  );
}
