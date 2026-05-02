import { auth, currentUser } from "@clerk/nextjs/server";

export const metadata = { title: "Dashboard" };

export default async function DashboardPage() {
  const { userId } = await auth();
  const user = await currentUser();
  const firstName = user?.firstName ?? "there";

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Good to see you, {firstName}.
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          User ID: <code className="font-mono text-xs">{userId}</code>
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          { label: "LLM spend today", value: "$0.00", sub: "of $5.00 daily cap" },
          { label: "Notes", value: "0", sub: "no notes yet" },
          { label: "Habits", value: "0 / 0", sub: "set up habits to track" },
        ].map((card) => (
          <div
            key={card.label}
            className="rounded-lg border border-border bg-card p-5 space-y-1"
          >
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {card.label}
            </p>
            <p className="text-2xl font-semibold">{card.value}</p>
            <p className="text-xs text-muted-foreground">{card.sub}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
