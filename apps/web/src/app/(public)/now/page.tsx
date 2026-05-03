import { contentApi } from "@/lib/api/content";

export const metadata = { title: "Now" };

export default async function NowPage() {
  let post = null;
  try {
    post = await contentApi.getPost("now");
  } catch {
    // not yet published
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-20">
      <h1 className="text-3xl font-bold tracking-tight">Now</h1>
      <p className="mt-2 text-xs text-muted-foreground">
        What I'm focused on right now.{" "}
        <a
          href="https://nownownow.com/about"
          target="_blank"
          rel="noopener noreferrer"
          className="underline underline-offset-4 hover:text-foreground"
        >
          What's a now page?
        </a>
      </p>

      <div className="mt-10">
        {post ? (
          <div className="prose prose-invert max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm leading-7 text-foreground">
              {post.body_mdx}
            </pre>
            {post.updated_at && (
              <p className="mt-8 text-xs text-muted-foreground">
                Last updated{" "}
                {new Date(post.updated_at).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Coming soon.</p>
        )}
      </div>
    </div>
  );
}
