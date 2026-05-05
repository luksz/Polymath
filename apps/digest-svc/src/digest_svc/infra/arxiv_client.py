import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx


@dataclass
class ArxivPaper:
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    arxiv_url: str


class ArxivClient:
    BASE_URL = "https://export.arxiv.org/api/query"

    async def fetch_recent(self, topics: list[str], max_results: int = 20) -> list[ArxivPaper]:
        """Fetch papers published in the last 24h for the given topic categories."""
        category_filter = " OR ".join(f"cat:{t}" for t in topics)
        params = {
            "search_query": category_filter,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
        return self._parse_atom(resp.text)

    def _parse_atom(self, xml_text: str) -> list[ArxivPaper]:
        """Parse Atom XML response from arXiv API."""
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        root = ET.fromstring(xml_text)
        papers = []
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            abstract_el = entry.find("atom:summary", ns)
            id_el = entry.find("atom:id", ns)
            authors = [
                a.find("atom:name", ns).text or ""
                for a in entry.findall("atom:author", ns)
                if a.find("atom:name", ns) is not None
            ]
            if title_el is None or abstract_el is None or id_el is None:
                continue
            raw_id = id_el.text or ""
            arxiv_id = raw_id.split("/abs/")[-1].strip()
            papers.append(
                ArxivPaper(
                    arxiv_id=arxiv_id,
                    title=title_el.text.strip().replace("\n", " "),
                    authors=authors[:5],  # cap at 5 names
                    abstract=abstract_el.text.strip().replace("\n", " "),
                    arxiv_url=raw_id.strip(),
                )
            )
        return papers
