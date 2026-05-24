"""
app/utils/display_meta.py
AR Chemistry Lab — display enrichment helpers

Converts raw GNN predictions into frontend-ready display data:
  - color_block()      → hex + Flutter + Unity colors from a color name
  - build_danger()     → danger level + Unity effect instructions
  - enrich_payload()   → call this in the router, pass the raw AI response
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# 1. COLOR — PRECIPITATE_COLOR name → hex + engine formats
# ─────────────────────────────────────────────────────────────────────────────

# All color names your GNN may return for PRECIPITATE_COLOR
COLOR_HEX: dict[str, str] = {
    "white":        "#F5F5F5",
    "black":        "#1A1A1A",
    "yellow":       "#F5C518",
    "pale yellow":  "#F9E57A",
    "orange":       "#E8820C",
    "red":          "#C0392B",
    "brick red":    "#CB4154",
    "blue":         "#2E86AB",
    "pale blue":    "#AED6F1",
    "green":        "#27AE60",
    "pale green":   "#A8D8A8",
    "brown":        "#7B5E3A",
    "dark brown":   "#3E2000",
    "gray":         "#888888",
    "grey":         "#888888",
    "purple":       "#8E44AD",
    "pink":         "#E91E8C",
    "colorless":    "#E8F4FD",
    "cream":        "#FFFDD0",
    "silver":       "#C0C0C0",
    "gold":         "#FFD700",
    "none":         "#E8F4FD",   # no precipitate → transparent-ish
}


def _hex_to_flutter(hex_color: str) -> str:
    """#RRGGBB → Flutter Color(0xFFRRGGBB)"""
    h = hex_color.lstrip("#")
    return f"Color(0xFF{h.upper()})"


def _hex_to_unity(hex_color: str) -> dict:
    """#RRGGBB → Unity Color struct with 0–1 floats"""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return {"r": round(r, 4), "g": round(g, 4), "b": round(b, 4), "a": 1.0}


def color_block(color_name: str) -> dict:
    """
    Build the full color dict from a plain color name like 'black'.

    Returns:
        name          — original name from GNN
        hex           — #RRGGBB
        flutter_color — Color(0xFFRRGGBB)
        unity_color   — {r, g, b, a} floats 0-1
    """
    name = (color_name or "none").strip().lower()
    hex_color = COLOR_HEX.get(name, "#AAAAAA")   # gray fallback for unknown
    return {
        "name":          name,
        "hex":           hex_color,
        "flutter_color": _hex_to_flutter(hex_color),
        "unity_color":   _hex_to_unity(hex_color),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. DANGER — REACTION_TYPE + HAZARD_LEVEL + GAS_PRODUCED → danger signal
# ─────────────────────────────────────────────────────────────────────────────

# Keyword sets matched against the GNN label strings (lowercase)
_EXPLOSION_KEYWORDS  = {"explosive", "thermite", "detonation", "violent"}
_FIRE_KEYWORDS       = {"combustion", "oxidation", "exothermic", "burning", "ignition"}
_TOXIC_GAS_KEYWORDS  = {
    "chlorine", "hydrogen sulfide", "ammonia", "carbon monoxide",
    "sulfur dioxide", "nitrogen dioxide", "phosgene", "hydrogen cyanide",
    "fluorine", "bromine",
}
_FLAMMABLE_GAS_KEYWORDS = {"hydrogen", "methane", "acetylene", "propane", "ethylene"}

# Hazard level → numeric rank so we can take the max
_HAZARD_RANK: dict[str, int] = {
    "none":    0,
    "low":     1,
    "medium":  2,
    "high":    3,
    "extreme": 4,
}

# Rank → unified level label
_RANK_LABEL = {0: "none", 1: "caution", 2: "warning", 3: "danger", 4: "extreme"}

# Level → traffic-light hex for overlay tinting
_LEVEL_COLOR = {
    "none":    "#4CAF50",   # green
    "caution": "#FFC107",   # amber
    "warning": "#FF9800",   # orange
    "danger":  "#F44336",   # red
    "extreme": "#9C27B0",   # purple
}

# Unity effect presets — names must match your Unity Addressable/Resources asset names
_UNITY_PRESETS: dict[str, dict] = {
    "explosion": {
        "particle_system":  "ExplosionVFX",
        "sound_cue":        "SFX_Explosion",
        "camera_shake":     True,
        "shake_intensity":  0.8,
        "post_process":     "FlashWhite",
        "warning_overlay":  "OverlayExplosion",
        "haptic":           "HeavyImpact",
    },
    "fire": {
        "particle_system":  "FireVFX",
        "sound_cue":        "SFX_Fire",
        "camera_shake":     False,
        "shake_intensity":  0.0,
        "post_process":     "ColorGradeRed",
        "warning_overlay":  "OverlayFire",
        "haptic":           "MediumImpact",
    },
    "toxic_gas": {
        "particle_system":  "ToxicSmokeVFX",
        "sound_cue":        "SFX_GasLeak",
        "camera_shake":     False,
        "shake_intensity":  0.0,
        "post_process":     "ColorGradeGreen",
        "warning_overlay":  "OverlayToxic",
        "haptic":           "LightImpact",
    },
    "flammable_gas": {
        "particle_system":  "GasSmokeVFX",
        "sound_cue":        "SFX_Hiss",
        "camera_shake":     False,
        "shake_intensity":  0.0,
        "post_process":     "ColorGradeAmber",
        "warning_overlay":  "OverlayFlammable",
        "haptic":           "LightImpact",
    },
    "caution": {
        "particle_system":  "SteamVFX",
        "sound_cue":        "SFX_Caution",
        "camera_shake":     False,
        "shake_intensity":  0.0,
        "post_process":     "None",
        "warning_overlay":  "OverlayCaution",
        "haptic":           "None",
    },
    "none": {
        "particle_system":  "None",
        "sound_cue":        "None",
        "camera_shake":     False,
        "shake_intensity":  0.0,
        "post_process":     "None",
        "warning_overlay":  "None",
        "haptic":           "None",
    },
}


def _match_any(text: str, keywords: set[str]) -> bool:
    return any(kw in text for kw in keywords)


def _build_message(
    level: str,
    explosion: bool,
    fire: bool,
    toxic_gas: bool,
    flammable_gas: bool,
    gas: str,
) -> str:
    if explosion:
        return "Explosive reaction — do not perform without full protection"
    if fire and toxic_gas:
        return f"Fire risk + toxic gas ({gas}) — use fume hood"
    if fire:
        return "Fire hazard — keep away from ignition sources"
    if toxic_gas:
        return f"Toxic gas produced ({gas}) — use fume hood"
    if flammable_gas:
        return f"Flammable gas produced ({gas}) — no open flames"
    if level == "caution":
        return "Mild hazard — standard lab precautions apply"
    return "No significant hazard detected"


def _unity_effects(
    explosion: bool,
    fire: bool,
    toxic_gas: bool,
    flammable_gas: bool,
    level: str,
) -> dict:
    """
    Pick the dominant Unity effect preset and collect secondary additive layers.
    Unity spawns dominant_particle first, then secondary_particles on top.
    """
    if explosion:
        dominant_key = "explosion"
    elif fire:
        dominant_key = "fire"
    elif toxic_gas:
        dominant_key = "toxic_gas"
    elif flammable_gas:
        dominant_key = "flammable_gas"
    elif level == "caution":
        dominant_key = "caution"
    else:
        dominant_key = "none"

    effects = dict(_UNITY_PRESETS[dominant_key])
    effects["dominant_effect"] = dominant_key

    # Collect secondary particle systems Unity layers additively
    secondary: list[str] = []
    if fire and dominant_key != "fire":
        secondary.append(_UNITY_PRESETS["fire"]["particle_system"])
    if toxic_gas and dominant_key != "toxic_gas":
        secondary.append(_UNITY_PRESETS["toxic_gas"]["particle_system"])
    if flammable_gas and dominant_key not in ("flammable_gas", "explosion"):
        secondary.append(_UNITY_PRESETS["flammable_gas"]["particle_system"])

    effects["secondary_particles"] = secondary
    return effects


def build_danger(
    reaction_type: str,
    hazard_level: str,
    gas_produced: str,
) -> dict:
    """
    Build the full danger signal from 3 GNN output labels.

    Args:
        reaction_type — GNN label e.g. "Combustion"
        hazard_level  — GNN label e.g. "High"
        gas_produced  — GNN label e.g. "Hydrogen"

    Returns:
        level           — "none" | "caution" | "warning" | "danger" | "extreme"
        explosion       — bool
        fire            — bool
        toxic_gas       — bool
        flammable_gas   — bool
        message         — human-readable string for AR overlay
        color_hex       — traffic-light color for overlay tinting
        flutter_color   — Color(0xFF...)
        unity_color     — {r, g, b, a}
        unity_effects   — full Unity instruction block
    """
    rt  = (reaction_type or "").strip().lower()
    hl  = (hazard_level  or "none").strip().lower()
    gas = (gas_produced  or "none").strip().lower()

    explosion     = _match_any(rt,  _EXPLOSION_KEYWORDS)
    fire          = _match_any(rt,  _FIRE_KEYWORDS)
    toxic_gas     = _match_any(gas, _TOXIC_GAS_KEYWORDS)
    flammable_gas = _match_any(gas, _FLAMMABLE_GAS_KEYWORDS)

    # Compute unified rank from hazard label + flags
    rank = _HAZARD_RANK.get(hl, 0)
    if explosion:
        rank = max(rank, 4)
    elif fire or toxic_gas:
        rank = max(rank, 3)
    elif flammable_gas:
        rank = max(rank, 2)

    level     = _RANK_LABEL[rank]
    hex_color = _LEVEL_COLOR[level]

    return {
        "level":          level,
        "explosion":      explosion,
        "fire":           fire,
        "toxic_gas":      toxic_gas,
        "flammable_gas":  flammable_gas,
        "message":        _build_message(level, explosion, fire, toxic_gas, flammable_gas, gas),
        "color_hex":      hex_color,
        "flutter_color":  _hex_to_flutter(hex_color),
        "unity_color":    _hex_to_unity(hex_color),
        "unity_effects":  _unity_effects(explosion, fire, toxic_gas, flammable_gas, level),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. ENRICH — single entry point called from the router
# ─────────────────────────────────────────────────────────────────────────────

def enrich_payload(payload: dict) -> dict:
    """
    Takes the raw JSON from forward_predict() and adds display enrichment.

    The GNN returns each label nested like:
        payload["PRECIPITATE_COLOR"]["label"]  = "black"
        payload["REACTION_TYPE"]["label"]      = "Combustion"
        payload["HAZARD_LEVEL"]["label"]       = "High"
        payload["GAS_PRODUCED"]["label"]       = "Hydrogen"

    Adds two top-level keys:
        payload["color"]   — color block
        payload["danger"]  — danger signal + Unity effects
    """
    def _label(key: str) -> str:
        entry = payload.get(key, {})
        # Support both {"label": "..."} and plain string responses
        if isinstance(entry, dict):
            return entry.get("label", "")
        return str(entry)

    payload["color"] = color_block(_label("PRECIPITATE_COLOR"))

    payload["danger"] = build_danger(
        reaction_type = _label("REACTION_TYPE"),
        hazard_level  = _label("HAZARD_LEVEL"),
        gas_produced  = _label("GAS_PRODUCED"),
    )

    return payload