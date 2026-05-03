import Link from "next/link";
import { SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-4xl items-center justify-between px-6">
        <Link
          href="/"
          className="text-sm font-semibold tracking-tight text-foreground hover:opacity-80"
        >
          Polymath
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/blog" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Writing</Link>
          <Link href="/projects" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Projects</Link>
          <Link href="/now" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Now</Link>
          <SignedOut>
            <Link
              href="/sign-in"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Sign in
            </Link>
          </SignedOut>
          <SignedIn>
            <Link
              href="/dashboard"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Dashboard
            </Link>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </nav>
      </div>
    </header>
  );
}
