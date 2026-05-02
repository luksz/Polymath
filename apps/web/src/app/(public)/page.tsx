import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-32 text-center">
      <div className="max-w-2xl space-y-8">
        <div className="space-y-4">
          <h1 className="text-5xl font-bold tracking-tight text-foreground sm:text-6xl">
            Polymath
          </h1>
          <p className="text-xl text-muted-foreground leading-relaxed">
            A personal platform for writing, thinking, and building.
            <br />
            Where craft meets curiosity.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            href="/sign-in"
            className="inline-flex items-center justify-center rounded-md bg-foreground px-6 py-3 text-sm font-medium text-background transition-opacity hover:opacity-80"
          >
            Sign in
          </Link>
          <Link
            href="#writing"
            className="inline-flex items-center justify-center rounded-md border border-border px-6 py-3 text-sm font-medium text-foreground transition-colors hover:bg-muted"
          >
            Read the writing
          </Link>
        </div>
      </div>

      <div
        id="writing"
        className="mt-32 w-full max-w-2xl border-t border-border pt-16"
      >
        <p className="text-sm text-muted-foreground">
          Essays and notes coming soon.
        </p>
      </div>
    </div>
  );
}
