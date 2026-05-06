#!/usr/bin/env python3
"""Generate naturalistic Vienna real estate images via OpenRouter / Gemini."""
import base64
import json
import os
import sys
import urllib.request

API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "google/gemini-3-pro-image-preview"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

PROMPTS = {
    "hero-zinshaus.jpg": (
        "Photorealistic photograph of a classic Viennese Gründerzeit Zinshaus apartment "
        "building (Altbau) facade in the early morning, around 7am, soft warm sunlight "
        "from the side. Five storeys, ornate stucco facade in pale ochre and cream tones, "
        "wrought-iron balcony railings, large rectangular windows with white frames, "
        "ground floor with one small shop and a heavy wooden Hauseingang door. The street "
        "is calm and empty, slightly wet cobblestones reflecting light, a single planted "
        "tree on the sidewalk. Vienna 4th or 7th district atmosphere, Hietzing or Wieden. "
        "Documentary architectural photography, natural colours, no text, no logos, no "
        "people, sharp detail, slightly desaturated palette. 16:9 aspect ratio, "
        "high resolution."
    ),
    "construction-wien.jpg": (
        "Photorealistic photograph of an active mid-sized residential construction site "
        "in Vienna, Austria. Mid-rise apartment building under construction, around 4-5 "
        "storeys, scaffolding wrapping the structural concrete shell, blue safety fence "
        "with construction company signs, a single yellow tower crane against an overcast "
        "afternoon sky, stacks of bricks and rebar in the foreground, two construction "
        "workers in orange high-vis jackets and white helmets in the middle distance "
        "(small, not prominent). Setting is a typical Vienna outer district like "
        "Donaustadt or Favoriten — wide street, tram lines visible in the background. "
        "Documentary photography style, slightly muted colours, natural light, no text, "
        "no logos, sharp realistic detail. 16:9 aspect ratio."
    ),
    "rooftops-wien.jpg": (
        "Photorealistic aerial photograph of Vienna's mixed inner-district rooftops at "
        "golden hour, late afternoon. Foreground shows traditional Gründerzeit Zinshaus "
        "buildings with red clay tile roofs, dormer windows, copper-green chimneys and "
        "antenna masts. Middle distance shows several modern flat-roofed glass-and-zinc "
        "extensions and one new contemporary residential development with green rooftop "
        "terraces. Far background hints at Stephansdom spire silhouette. Warm orange and "
        "pink sky, soft shadows, late October atmosphere, leaves slightly turned. "
        "Architectural documentary photography, natural colours, no text, no logos, "
        "no people, high clarity. 16:9 aspect ratio."
    ),
}


def gen(prompt: str, out_path: str) -> bool:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nichtagentur.github.io/predevelopment-check/",
            "X-Title": "PREDEV Image Generation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:400]}")
        return False

    msg = data["choices"][0]["message"]
    images = msg.get("images") or []
    if not images:
        print(f"  no images in response: {json.dumps(data)[:400]}")
        return False
    url = images[0].get("image_url", {}).get("url", "")
    if url.startswith("data:image"):
        b64 = url.split(",", 1)[1]
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"  saved → {out_path} ({os.path.getsize(out_path)} bytes)")
        return True
    print(f"  unexpected url format: {url[:120]}")
    return False


def main():
    for name, prompt in PROMPTS.items():
        out = os.path.join(OUT_DIR, name)
        print(f"\n→ generating {name}")
        ok = gen(prompt, out)
        if not ok:
            print(f"  FAILED for {name}")
            sys.exit(1)


if __name__ == "__main__":
    main()
