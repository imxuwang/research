#!/usr/bin/env python3
"""Zero-key scientific literature search and citation verifier.

Queries public APIs using Python stdlib only:
  - arXiv Atom API (CS, Physics, Math, q-Bio, Stat)
  - PubMed E-utilities (Biomedicine, Life Sciences)
  - Semantic Scholar Graph API (Cross-disciplinary)
  - OpenAlex Works API (250M+ general scientific works, generous unauthenticated limits)
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any


USER_AGENT = "Antigravity-CoScientist/1.0 (mailto:research-agent@localhost)"
TIMEOUT_SEC = 15


def http_get(url: str, accept: str = "application/json") -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": accept,
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        return resp.read()


def clean_ws(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def reconstruct_openalex_abstract(inv_idx: dict[str, list[int]] | None) -> str:
    if not inv_idx:
        return ""
    pos_to_word: dict[int, str] = {}
    for word, positions in inv_idx.items():
        for pos in positions:
            pos_to_word[pos] = word
    if not pos_to_word:
        return ""
    max_pos = max(pos_to_word)
    words = [pos_to_word.get(i, "") for i in range(max_pos + 1)]
    return clean_ws(" ".join(words))


def search_arxiv(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    encoded = urllib.parse.quote(query)
    url = f"https://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results={max_results}&sortBy=relevance"
    raw = http_get(url, accept="application/atom+xml")
    root = ET.fromstring(raw)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results = []
    for entry in root.findall("atom:entry", ns):
        id_url = clean_ws(entry.findtext("atom:id", default="", namespaces=ns))
        arxiv_id = id_url.rsplit("/abs/", 1)[-1] if "/abs/" in id_url else id_url
        published = clean_ws(entry.findtext("atom:published", default="", namespaces=ns))
        year = int(published[:4]) if len(published) >= 4 and published[:4].isdigit() else None
        authors = [
            clean_ws(a.findtext("atom:name", default="", namespaces=ns))
            for a in entry.findall("atom:author", ns)
        ]
        results.append(
            {
                "source": "arxiv",
                "id": f"arxiv:{arxiv_id}",
                "title": clean_ws(entry.findtext("atom:title", default="", namespaces=ns)),
                "authors": authors[:6],
                "year": year,
                "venue": "arXiv",
                "url": id_url,
                "abstract": clean_ws(entry.findtext("atom:summary", default="", namespaces=ns))[:900],
            }
        )
    return results


def search_pubmed(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    esearch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        + urllib.parse.urlencode({"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json", "sort": "relevance"})
    )
    search_data = json.loads(http_get(esearch_url).decode("utf-8"))
    id_list = search_data.get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return []

    time.sleep(0.35)  # Respect NCBI 3 req/s unauthenticated rate limit
    efetch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
        + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(id_list), "retmode": "xml"})
    )
    xml_bytes = http_get(efetch_url, accept="application/xml")
    root = ET.fromstring(xml_bytes)

    results = []
    for article in root.findall(".//PubmedArticle"):
        pmid = clean_ws(article.findtext(".//MedlineCitation/PMID", default=""))
        title = clean_ws("".join(article.find(".//ArticleTitle").itertext())) if article.find(".//ArticleTitle") is not None else ""
        abs_elems = article.findall(".//Abstract/AbstractText")
        abstract = clean_ws(" ".join("".join(el.itertext()) for el in abs_elems))
        journal = clean_ws(article.findtext(".//Journal/Title", default="PubMed"))
        year_txt = (
            article.findtext(".//JournalIssue/PubDate/Year")
            or article.findtext(".//ArticleDate/Year")
            or ""
        )
        year = int(year_txt) if year_txt.isdigit() else None
        authors = []
        for au in article.findall(".//AuthorList/Author"):
            last = clean_ws(au.findtext("LastName", default=""))
            fore = clean_ws(au.findtext("ForeName", default=""))
            if last or fore:
                authors.append(f"{fore} {last}".strip())
        doi = ""
        for aid in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if aid.attrib.get("IdType") == "doi":
                doi = clean_ws(aid.text)
                break
        results.append(
            {
                "source": "pubmed",
                "id": f"pmid:{pmid}",
                "doi": doi,
                "title": title,
                "authors": authors[:6],
                "year": year,
                "venue": journal,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "abstract": abstract[:900],
            }
        )
    return results


def search_semantic_scholar(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "query": query,
            "limit": max_results,
            "fields": "title,authors,year,venue,externalIds,url,abstract,citationCount",
        }
    )
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    data = json.loads(http_get(url).decode("utf-8"))
    results = []
    for item in data.get("data", []):
        ext = item.get("externalIds") or {}
        doi = ext.get("DOI", "")
        arxiv_id = ext.get("ArXiv", "")
        pmid = ext.get("PubMed", "")
        pid = (
            f"doi:{doi}"
            if doi
            else (f"arxiv:{arxiv_id}" if arxiv_id else (f"pmid:{pmid}" if pmid else f"s2:{item.get('paperId', '')}"))
        )
        results.append(
            {
                "source": "semantic_scholar",
                "id": pid,
                "doi": doi,
                "title": clean_ws(item.get("title")),
                "authors": [a.get("name", "") for a in (item.get("authors") or [])[:6]],
                "year": item.get("year"),
                "venue": clean_ws(item.get("venue")),
                "citation_count": item.get("citationCount"),
                "url": item.get("url") or (f"https://doi.org/{doi}" if doi else ""),
                "abstract": clean_ws(item.get("abstract"))[:900],
            }
        )
    return results


def search_openalex(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"search": query, "per-page": max_results})
    url = f"https://api.openalex.org/works?{params}"
    data = json.loads(http_get(url).decode("utf-8"))
    results = []
    for work in data.get("results", []):
        doi_url = work.get("doi") or ""
        doi = doi_url.replace("https://doi.org/", "") if doi_url else ""
        oa_id = (work.get("id") or "").rsplit("/", 1)[-1]
        loc = work.get("primary_location") or {}
        src = loc.get("source") or {}
        authors = [
            (a.get("author") or {}).get("display_name", "")
            for a in (work.get("authorships") or [])[:6]
        ]
        abstract = reconstruct_openalex_abstract(work.get("abstract_inverted_index"))
        results.append(
            {
                "source": "openalex",
                "id": f"doi:{doi}" if doi else f"openalex:{oa_id}",
                "doi": doi,
                "title": clean_ws(work.get("display_name") or work.get("title")),
                "authors": [a for a in authors if a],
                "year": work.get("publication_year"),
                "venue": clean_ws(src.get("display_name")),
                "citation_count": work.get("cited_by_count"),
                "url": doi_url or work.get("id", ""),
                "abstract": abstract[:900],
            }
        )
    return results


def verify_identifier(identifier: str) -> dict[str, Any]:
    ident = identifier.strip()
    lower = ident.lower()
    try:
        if lower.startswith("arxiv:"):
            aid = ident.split(":", 1)[1].strip()
            aid_clean = re.sub(r"v\d+$", "", aid)
            url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(aid_clean)}"
            root = ET.fromstring(http_get(url, accept="application/atom+xml"))
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entry = root.find("atom:entry", ns)
            title = clean_ws(entry.findtext("atom:title", default="", namespaces=ns)) if entry is not None else ""
            if entry is None or not title or title.lower() == "error":
                return {"id": ident, "verified": False, "reason": "arXiv ID not found"}
            return {"id": ident, "verified": True, "title": title, "url": f"https://arxiv.org/abs/{aid_clean}"}

        if lower.startswith("pmid:"):
            pmid = ident.split(":", 1)[1].strip()
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
                {"db": "pubmed", "id": pmid, "retmode": "json"}
            )
            data = json.loads(http_get(url).decode("utf-8"))
            rec = (data.get("result") or {}).get(pmid)
            if not rec or "error" in rec:
                return {"id": ident, "verified": False, "reason": "PMID not found"}
            return {
                "id": ident,
                "verified": True,
                "title": clean_ws(rec.get("title")),
                "year": (rec.get("pubdate") or "")[:4],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }

        if lower.startswith("doi:") or lower.startswith("10."):
            doi = ident.split(":", 1)[1].strip() if lower.startswith("doi:") else ident
            url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}"
            data = json.loads(http_get(url).decode("utf-8"))
            if not data.get("id"):
                return {"id": ident, "verified": False, "reason": "DOI not found in OpenAlex"}
            return {
                "id": f"doi:{doi}",
                "verified": True,
                "title": clean_ws(data.get("display_name")),
                "year": data.get("publication_year"),
                "url": f"https://doi.org/{doi}",
            }

        return {"id": ident, "verified": False, "reason": "Unsupported prefix (use arxiv:, pmid:, or doi:)"}
    except Exception as exc:
        return {"id": ident, "verified": False, "reason": f"Lookup error: {exc}"}


def cmd_search(args: argparse.Namespace) -> None:
    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    dispatch = {
        "arxiv": search_arxiv,
        "pubmed": search_pubmed,
        "s2": search_semantic_scholar,
        "openalex": search_openalex,
    }
    papers: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    seen_titles: set[str] = set()

    for src in sources:
        fn = dispatch.get(src)
        if not fn:
            errors[src] = f"Unknown source '{src}'"
            continue
        try:
            items = fn(args.query, max_results=args.max_results)
            for item in items:
                norm_title = re.sub(r"\W+", "", (item.get("title") or "").lower())
                if norm_title and norm_title in seen_titles:
                    continue
                if norm_title:
                    seen_titles.add(norm_title)
                papers.append(item)
        except urllib.error.HTTPError as exc:
            errors[src] = f"HTTP {exc.code}: {exc.reason}"
        except Exception as exc:
            errors[src] = str(exc)

    print(
        json.dumps(
            {
                "query": args.query,
                "sources_queried": sources,
                "count": len(papers),
                "errors": errors,
                "papers": papers,
            },
            indent=2,
        )
    )


def cmd_verify(args: argparse.Namespace) -> None:
    checks = [verify_identifier(i) for i in args.ids]
    print(json.dumps({"checks": checks}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Search scientific literature and verify citations")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_s = sub.add_parser("search", help="Search across arXiv, PubMed, OpenAlex, Semantic Scholar")
    p_s.add_argument("--query", required=True, help="Search keywords")
    p_s.add_argument(
        "--sources",
        default="arxiv,pubmed,openalex",
        help="Comma-separated sources: arxiv,pubmed,openalex,s2 (default: arxiv,pubmed,openalex)",
    )
    p_s.add_argument("--max-results", type=int, default=5, help="Max results per source")
    p_s.set_defaults(func=cmd_search)

    p_v = sub.add_parser("verify", help="Verify paper identifiers (arxiv:..., pmid:..., doi:...)")
    p_v.add_argument("ids", nargs="+", help="Identifiers to verify")
    p_v.set_defaults(func=cmd_verify)

    return p


if __name__ == "__main__":
    parser = build_parser()
    parsed = parser.parse_args()
    parsed.func(parsed)
