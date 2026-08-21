"""Domain & DNS Intelligence tools: DNS records, URL unshortener, subdomains, and security scans."""

import asyncio
from typing import Dict, Any, List, Set
import dns.resolver
import httpx


async def lookup_dns(domain: str) -> Dict[str, Any]:
    """Query DNS records (A, AAAA, MX, TXT, NS, CNAME) for a given domain."""
    clean_domain = domain.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]

    records: Dict[str, List[str]] = {
        "A": [],
        "AAAA": [],
        "MX": [],
        "TXT": [],
        "NS": [],
        "CNAME": [],
    }

    loop = asyncio.get_running_loop()

    def _query():
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3.0
        resolver.lifetime = 3.0

        for r_type in records.keys():
            try:
                answers = resolver.resolve(clean_domain, r_type)
                for rdata in answers:
                    records[r_type].append(str(rdata))
            except Exception:
                pass
        return records

    try:
        resolved_records = await loop.run_in_executor(None, _query)
        total_found = sum(len(v) for v in resolved_records.values())
        return {
            "success": True,
            "domain": clean_domain,
            "records": resolved_records,
            "total_records": total_found,
        }
    except Exception as e:
        return {"success": False, "domain": clean_domain, "error": str(e)}


async def unshorten_url(short_url: str) -> Dict[str, Any]:
    """Trace HTTP redirect chains to find the true destination URL (Anti-Phishing)."""
    url = short_url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    hops: List[Dict[str, Any]] = []

    try:
        current_url = url
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            for _ in range(10):  # Maximum 10 redirects
                resp = await client.get(current_url)
                status = resp.status_code
                location = resp.headers.get("location")

                hops.append({
                    "url": current_url,
                    "status_code": status,
                    "location": location,
                })

                if status in (301, 302, 303, 307, 308) and location:
                    if location.startswith("/"):
                        # Relative redirect
                        from urllib.parse import urljoin
                        current_url = urljoin(current_url, location)
                    else:
                        current_url = location
                else:
                    break

        final_url = hops[-1]["url"] if hops else url
        is_redirected = len(hops) > 1

        return {
            "success": True,
            "initial_url": url,
            "final_url": final_url,
            "hops_count": len(hops),
            "hops": hops,
            "is_redirected": is_redirected,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def find_subdomains(domain: str) -> Dict[str, Any]:
    """Discover subdomains from public Certificate Transparency (crt.sh) logs."""
    clean_domain = domain.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]

    url = f"https://crt.sh/?q=%.{clean_domain}&output=json"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)

        if resp.status_code != 200:
            return {"success": False, "domain": clean_domain, "error": "Certificate Transparency service unavailable."}

        data = resp.json()
        subdomains: Set[str] = set()

        for entry in data:
            name_value = entry.get("name_value", "")
            for sub in name_value.split("\n"):
                sub = sub.strip().lower()
                if sub and not sub.startswith("*.") and clean_domain in sub:
                    subdomains.add(sub)

        sorted_subdomains = sorted(list(subdomains))[:50]  # Limit to 50 items

        return {
            "success": True,
            "domain": clean_domain,
            "subdomains": sorted_subdomains,
            "count": len(sorted_subdomains),
        }
    except Exception as e:
        return {"success": False, "domain": clean_domain, "error": str(e)}


async def security_scan(domain: str) -> Dict[str, Any]:
    """Analyze HTTP security headers and assign a security grade."""
    clean_domain = domain.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    target_url = f"https://{clean_domain}"

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(target_url)

        headers = {k.lower(): v for k, v in resp.headers.items()}

        checks = {
            "Strict-Transport-Security (HSTS)": "strict-transport-security" in headers,
            "Content-Security-Policy (CSP)": "content-security-policy" in headers,
            "X-Frame-Options (Clickjacking Protection)": "x-frame-options" in headers,
            "X-Content-Type-Options (MIME Sniffing)": "x-content-type-options" in headers,
            "Referrer-Policy": "referrer-policy" in headers,
            "Permissions-Policy": "permissions-policy" in headers,
        }

        score = sum(checks.values())
        if score >= 5:
            grade = "🟢 A+ (Excellent Security Headers)"
        elif score >= 4:
            grade = "🟢 A (Strong Security Headers)"
        elif score >= 3:
            grade = "🟡 B (Moderate Security - Some headers missing)"
        elif score >= 2:
            grade = "🟡 C (Weak Security - Key headers missing)"
        else:
            grade = "🔴 F (High Risk - Missing critical protection headers)"

        return {
            "success": True,
            "domain": clean_domain,
            "grade": grade,
            "score": f"{score}/6",
            "checks": checks,
            "server": headers.get("server", "Hidden"),
            "status_code": resp.status_code,
        }
    except Exception as e:
        return {"success": False, "domain": clean_domain, "error": str(e)}
