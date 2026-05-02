# 0007 — Next.js 15 for the frontend
**Date:** 2026-05-03
**Status:** Accepted

## Context
The owner's primary language is Python. However, the frontend needs server-side rendering for public pages (SEO, Lighthouse scores), a modern component ecosystem, and MDX support for the blog.

## Decision
Next.js 15 with App Router. Public-facing pages (blog, portfolio, games) use React Server Components for SSR. The authed dashboard uses client-side rendering with TanStack Query. UI: Tailwind CSS 4 + shadcn/ui.

## Consequences
- JavaScript/TypeScript context switching for a Python developer.
- Strong ecosystem; shadcn/ui avoids building a design system.
- App Router enables granular SSR/CSR per route group.
- Bundle size managed via `next/bundle-analyzer` and Lighthouse CI.
- Alternative (SvelteKit) considered but Next.js has a wider component ecosystem and stronger shadcn support.
