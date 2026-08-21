"""IP & Network intelligence tools: Geolocation, ISP, ASN, Ping, Headers, Port checks."""

import asyncio
import socket
import time
from typing import Dict, Any, Optional, Tuple
import httpx
from bot.utils.country_data import get_flag_emoji


async def lookup_ip(target: str) -> Dict[str, Any]:
    """Retrieve IP address geolocation, ISP, ASN, and proxy/VPN flags."""
    clean_target = target.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]

    url = f"http://ip-api.com/json/{clean_target}?fields=status,message,continent,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            data = resp.json()

        if data.get("status") != "success":
            return {"success": False, "error": data.get("message", "Could not resolve IP address.")}

        flag = get_flag_emoji(data.get("countryCode"))
        is_proxy = data.get("proxy", False)
        is_hosting = data.get("hosting", False)

        risk_tag = "🔴 Proxy / VPN / Tor" if is_proxy else ("🟡 Datacenter / Cloud Server" if is_hosting else "🟢 Residential / ISP")

        return {
            "success": True,
            "ip": data.get("query"),
            "flag": flag,
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "region": data.get("regionName"),
            "city": data.get("city"),
            "zip": data.get("zip") or "N/A",
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "timezone": data.get("timezone"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "asn": data.get("as"),
            "reverse_dns": data.get("reverse") or "None",
            "is_mobile": data.get("mobile", False),
            "is_proxy": is_proxy,
            "is_hosting": is_hosting,
            "risk_tag": risk_tag,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def check_ping(host: str) -> Dict[str, Any]:
    """Measure TCP latency to a host in milliseconds."""
    clean_host = host.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]

    start_time = time.time()
    try:
        # Resolve hostname
        loop = asyncio.get_running_loop()
        ip_addr = await loop.run_in_executor(None, socket.gethostbyname, clean_host)
        dns_time = (time.time() - start_time) * 1000

        # TCP Connect test on port 443 or 80
        t0 = time.time()
        conn_coro = asyncio.open_connection(ip_addr, 443)
        try:
            reader, writer = await asyncio.wait_for(conn_coro, timeout=5.0)
            writer.close()
            await writer.wait_closed()
            tcp_time = (time.time() - t0) * 1000
            port_used = 443
        except Exception:
            # Fallback to port 80
            t0 = time.time()
            reader, writer = await asyncio.wait_for(asyncio.open_connection(ip_addr, 80), timeout=5.0)
            writer.close()
            await writer.wait_closed()
            tcp_time = (time.time() - t0) * 1000
            port_used = 80

        total_time = (time.time() - start_time) * 1000

        return {
            "success": True,
            "host": clean_host,
            "ip": ip_addr,
            "port": port_used,
            "dns_ms": round(dns_time, 2),
            "tcp_ms": round(tcp_time, 2),
            "total_ms": round(total_time, 2),
        }
    except Exception as e:
        return {"success": False, "host": clean_host, "error": str(e)}


async def check_headers(target_url: str) -> Dict[str, Any]:
    """Fetch HTTP response headers and security headers analysis."""
    url = target_url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)

        headers = dict(resp.headers)
        status_code = resp.status_code
        server = headers.get("server", "Hidden / Not Disclosed")
        content_type = headers.get("content-type", "N/A")

        # Security Headers
        sec_hsts = "strict-transport-security" in headers
        sec_csp = "content-security-policy" in headers
        sec_xframe = "x-frame-options" in headers
        sec_xss = "x-content-type-options" in headers

        return {
            "success": True,
            "url": str(resp.url),
            "status_code": status_code,
            "server": server,
            "content_type": content_type,
            "headers": headers,
            "hsts": sec_hsts,
            "csp": sec_csp,
            "xframe": sec_xframe,
            "xss": sec_xss,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def check_port(host: str, port: int) -> Dict[str, Any]:
    """Test if a TCP port on a target host is open."""
    clean_host = host.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]

    try:
        coro = asyncio.open_connection(clean_host, port)
        reader, writer = await asyncio.wait_for(coro, timeout=3.0)
        writer.close()
        await writer.wait_closed()
        return {"success": True, "host": clean_host, "port": port, "is_open": True}
    except Exception:
        return {"success": True, "host": clean_host, "port": port, "is_open": False}
