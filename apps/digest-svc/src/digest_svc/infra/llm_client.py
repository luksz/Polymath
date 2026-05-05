import json

import httpx
import structlog

logger = structlog.get_logger()


class DigestLLMClient:
    def __init__(self, llm_gateway_url: str) -> None:
        self._base = llm_gateway_url.rstrip("/")

    async def score_relevance(self, title: str, abstract: str) -> int:
        """Score paper relevance 1-10 for a software engineer interested in AI/ML."""
        prompt = (
            f"Rate the relevance of this paper 1-10 for a software engineer who builds AI products "
            f"and is interested in LLMs, ML systems, and developer tools. "
            f"Respond with ONLY a single integer 1-10.\n\n"
            f"Title: {title}\n\nAbstract: {abstract[:800]}"
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self._base}/v1/complete",
                    json={
                        "model": "claude-haiku-4-5-20251001",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 5,
                    },
                    headers={"X-Polymath-User-Id": "digest-svc"},
                )
                resp.raise_for_status()
                text = resp.json().get("content", "5").strip()
                return max(1, min(10, int(text)))
        except Exception as e:
            logger.warning("relevance_score_failed", error=str(e))
            return 5

    async def summarise(self, title: str, abstract: str) -> dict[str, str]:
        """Return structured summary: headline, body_md, key_insight, why_it_matters."""
        prompt = (
            f"You are summarising a research paper for a busy software engineer. "
            f"Return a JSON object with exactly these keys:\n"
            f"- headline: one punchy sentence (max 15 words)\n"
            f"- body_md: 5-minute read in markdown (300-400 words, no headers, just prose)\n"
            f"- key_insight: the single most important finding (1-2 sentences)\n"
            f"- why_it_matters: why a software engineer building AI products should care (1-2 sentences)\n\n"
            f"Paper title: {title}\n\nAbstract: {abstract[:1500]}\n\n"
            f"Return valid JSON only, no markdown fences."
        )
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self._base}/v1/complete",
                    json={
                        "model": "claude-sonnet-4-6",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 800,
                    },
                    headers={"X-Polymath-User-Id": "digest-svc"},
                )
                resp.raise_for_status()
                text = resp.json().get("content", "{}")
                data = json.loads(text)
                return {
                    "headline": data.get("headline", title[:80]),
                    "body_md": data.get("body_md", abstract),
                    "key_insight": data.get("key_insight", ""),
                    "why_it_matters": data.get("why_it_matters", ""),
                }
        except Exception as e:
            logger.warning("summarise_failed", error=str(e))
            return {
                "headline": title[:80],
                "body_md": abstract,
                "key_insight": "",
                "why_it_matters": "",
            }
