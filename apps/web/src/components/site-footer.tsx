export function SiteFooter() {
  return (
    <footer className="border-t border-border py-8">
      <div className="mx-auto max-w-4xl px-6 flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          © {new Date().getFullYear()} Polymath
        </p>
        <p className="text-xs text-muted-foreground">Built with curiosity.</p>
      </div>
    </footer>
  );
}
