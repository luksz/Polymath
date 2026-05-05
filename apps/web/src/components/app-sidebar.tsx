"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  StickyNote,
  CheckSquare,
  BarChart2,
  Gamepad2,
  Settings,
  ChevronDown,
  BookOpen,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

type NavItem = {
  label: string;
  href: string;
  icon: React.ElementType;
};

type NavGroup = {
  label: string;
  items: NavItem[];
};

const navGroups: NavGroup[] = [
  {
    label: "Overview",
    items: [{ label: "Dashboard", href: "/dashboard", icon: LayoutDashboard }],
  },
  {
    label: "AI",
    items: [
      { label: "Chat", href: "/chat", icon: MessageSquare },
      { label: "Prompts", href: "/prompts", icon: FileText },
      { label: "Digest", href: "/digest", icon: BookOpen },
    ],
  },
  {
    label: "Content",
    items: [
      { label: "Writing", href: "/writing", icon: FileText },
    ],
  },
  {
    label: "Productivity",
    items: [
      { label: "Notes", href: "/notes", icon: StickyNote },
      { label: "Habits", href: "/habits", icon: CheckSquare },
    ],
  },
  {
    label: "Analytics",
    items: [{ label: "Analytics", href: "/analytics", icon: BarChart2 }],
  },
  {
    label: "Games",
    items: [{ label: "Games", href: "/games", icon: Gamepad2 }],
  },
];

function NavGroupSection({ group }: { group: NavGroup }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(true);
  const isActive = group.items.some((i) => pathname.startsWith(i.href));

  return (
    <div className="space-y-0.5">
      <button
        onClick={() => setOpen(!open)}
        className={cn(
          "flex w-full items-center justify-between px-3 py-1.5 text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors",
          isActive && "text-foreground"
        )}
      >
        {group.label}
        <ChevronDown
          className={cn(
            "h-3 w-3 transition-transform",
            open ? "rotate-0" : "-rotate-90"
          )}
        />
      </button>
      {open &&
        group.items.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-accent text-accent-foreground font-medium"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
    </div>
  );
}

export function AppSidebar() {
  return (
    <aside className="flex h-screen w-56 flex-col border-r border-border bg-background">
      <div className="flex h-14 items-center border-b border-border px-4">
        <Link href="/" className="text-sm font-semibold tracking-tight">
          Polymath
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-4">
        {navGroups.map((group) => (
          <NavGroupSection key={group.label} group={group} />
        ))}
      </nav>

      <div className="border-t border-border p-3">
        <Link
          href="/settings"
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
        >
          <Settings className="h-4 w-4" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
