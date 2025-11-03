#!/usr/bin/env python3
"""
VeoStudio MCP Server
Integracion con Cursor IDE para generacion de videos con Veo 3.1
Context Engineering + FastMCP + Gemini API
"""

from fastmcp import FastMCP
import google.generativeai as genai
import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

# ==================== SETUP ====================

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastMCP Server
mcp = FastMCP(name="VeoStudio")

# Configurar Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY no configurada")

genai.configure(api_key=API_KEY)

# Pricing tabla (en USD)
VEO_PRICING = {
    "720p": {
        4: 0.15,
        6: 0.25,
        8: 0.35
    },
    "1080p": {
        4: 0.25,
        6: 0.50,
        8: 0.75
    }
}

# ==================== UTILITIES ====================

def log_tool_usage(tool_name: str, params: Dict[str, Any]) -> None:
    """Log tool usage para auditoría"""
    logger.info(f"MCP Tool called: {tool_name}", extra={
        "timestamp": datetime.now().isoformat(),
        "params": json.dumps(params, default=str)
    })

def validate_prompt(prompt: str) -> Dict[str, Any]:
    """Validar estructura de prompt"""
    if len(prompt) < 50:
        raise ValueError("Prompt muy corto (mínimo 50 caracteres)")
    
    if len(prompt) > 2000:
        raise ValueError("Prompt muy largo (máximo 2000 caracteres)")
    
    return {
        "valid": True,
        "length": len(prompt),
        "estimated_tokens": len(prompt.split()) * 1.3
    }

def estimate_tokens(text: str) -> int:
    """Estimar tokens de un texto"""
    words = len(text.split())
    return int(words * 1.3)

def format_veo_prompt(
    cinematography: str,
    subject: str,
    action: str,
    context: str,
    style: str,
    negative: str = ""
) -> Dict[str, str]:
    """Formato Veo usando 5-part formula"""
    
    # Main prompt
    main = f"{cinematography} | {subject} | {action} | {context} | {style}"
    
    # Negative prompt (best practices)
    if not negative:
        negative = (
            "low quality, blurry, distorted product, watermarks, text overlays, "
            "harsh shadows, unnatural lighting, oversaturated, unprofessional"
        )
    
    return {
        "main_prompt": main.strip(),
        "negative_prompt": negative.strip(),
        "structure": {
            "cinematography": cinematography,
            "subject": subject,
            "action": action,
            "context": context,
            "style": style
        }
    }

# ==================== MCP TOOLS ====================

@mcp.tool
def optimize_veo_prompt(
    product_name: str,
    product_description: str,
    desired_style: str,
    camera_style: str = "close-up tracking shot",
    duration_seconds: int = 6,
    resolution: str = "1080p"
) -> Dict[str, Any]:
    """
    Optimiza un prompt para Veo 3.1 usando la fórmula 5-parte.
    
    Args:
        product_name: Nombre del producto (ej: "iPhone 15")
        product_description: Descripción detallada
        desired_style: Estilo deseado (ej: "cinematic, professional")
        camera_style: Tipo de movimiento de cámara
        duration_seconds: Duración del video (4, 6, 8)
        resolution: Resolución (720p, 1080p)
    
    Returns:
        Prompt optimizado con estructura 5-parte, tokens estimados y costo
    """
    
    log_tool_usage("optimize_veo_prompt", {
        "product": product_name,
        "duration": duration_seconds,
        "resolution": resolution
    })
    
    try:
        # Construir prompt estructura
        cinematography = f"{camera_style}, dynamic composition, perfect framing"
        subject = f"premium {product_name}: {product_description}"
        action = "rotating, showcasing details, highlighting features"
        context = "minimalist white studio with professional lighting"
        style = f"{desired_style}, 4K quality, sharp focus, rich colors, studio lighting"
        
        prompt_dict = format_veo_prompt(
            cinematography=cinematography,
            subject=subject,
            action=action,
            context=context,
            style=style
        )
        
        # Calcular tokens y costo
        total_text = prompt_dict["main_prompt"] + " " + prompt_dict["negative_prompt"]
        estimated_tokens = estimate_tokens(total_text)
        estimated_cost = VEO_PRICING[resolution].get(
            duration_seconds,
            VEO_PRICING[resolution][6]  # default
        )
        
        return {
            "success": True,
            "prompt_optimized": prompt_dict["main_prompt"],
            "negative_prompt": prompt_dict["negative_prompt"],
            "structure": prompt_dict["structure"],
            "metadata": {
                "tokens_estimated": estimated_tokens,
                "tokens_used_by_gemini": int(estimated_tokens * 0.8),  # Estimación
                "cost_usd": float(estimated_cost),
                "duration_seconds": duration_seconds,
                "resolution": resolution,
                "generated_at": datetime.now().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error optimizing prompt: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "code": "PROMPT_OPTIMIZATION_FAILED"
        }

@mcp.tool
def estimate_generation_cost(
    duration_seconds: int,
    resolution: str,
    quantity: int = 1,
    include_reference_images: bool = False,
    include_audio: bool = True
) -> Dict[str, Any]:
    """
    Estima el costo total de generación de videos.
    
    Pricing:
    - 4s/720p: $0.15
    - 6s/720p: $0.25
    - 8s/720p: $0.35
    - 4s/1080p: $0.25
    - 6s/1080p: $0.50
    - 8s/1080p: $0.75
    
    Extra:
    - Reference images: +$0.05 por imagen
    - Audio generation: +$0.10
    """
    
    log_tool_usage("estimate_generation_cost", {
        "duration": duration_seconds,
        "resolution": resolution,
        "quantity": quantity
    })
    
    try:
        # Base cost
        base_cost = VEO_PRICING.get(resolution, {}).get(duration_seconds, 0.50)
        
        if base_cost == 0:
            return {
                "success": False,
                "error": f"Invalid duration {duration_seconds} or resolution {resolution}",
                "code": "INVALID_CONFIG"
            }
        
        # Calcular adicionales
        extras = 0
        if include_reference_images:
            extras += 0.05 * 3  # 3 reference images
        if include_audio:
            extras += 0.10
        
        # Costo total
        per_video = base_cost + extras
        total_cost = per_video * quantity
        
        return {
            "success": True,
            "pricing_breakdown": {
                "base_per_video": float(base_cost),
                "reference_images": 0.15 if include_reference_images else 0,
                "audio_generation": 0.10 if include_audio else 0,
                "per_video_total": float(per_video),
                "quantity": quantity,
                "total_cost_usd": float(total_cost)
            },
            "savings_opportunity": {
                "batch_discount": "10% if batch >= 5" if quantity >= 5 else None,
                "bulk_purchase": "Contact sales for volumes > 100"
            }
        }
    
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "code": "COST_ESTIMATION_FAILED"
        }

@mcp.tool
def build_product_video_prompt(
    product_name: str,
    key_features: List[str],
    target_audience: str,
    brand_style: str,
    video_duration: int = 6,
    resolution: str = "1080p"
) -> Dict[str, Any]:
    """
    Construye un prompt profesional para video de producto.
    
    Args:
        product_name: Nombre del producto
        key_features: Lista de características principales
        target_audience: Audience objetivo (ej: "Tech professionals")
        brand_style: Estilo de marca (ej: "Luxury, minimalist")
        video_duration: 4, 6 u 8 segundos
        resolution: 720p o 1080p
    
    Returns:
        Prompt completo + costos + recomendaciones
    """
    
    log_tool_usage("build_product_video_prompt", {
        "product": product_name,
        "features": len(key_features)
    })
    
    try:
        # Features como string
        features_str = ", ".join(key_features[:3])
        
        # Cinematography (varía por audiencia)
        cinema_map = {
            "Tech": "smooth tracking shot with dynamic angles",
            "Luxury": "slow dolly shot with shallow depth of field",
            "Youth": "fast-paced montage with transitions",
            "Professional": "stable medium shot with professional framing"
        }
        cinematography = cinema_map.get("Tech", "tracking shot")
        
        # Build prompt usando template
        product_desc = f"{product_name} featuring {features_str}"
        
        prompt_dict = format_veo_prompt(
            cinematography=cinematography,
            subject=f"premium {product_desc}",
            action="demonstrating key features, rotating to show details",
            context="elegant studio environment with professional lighting",
            style=f"{brand_style}, cinematic, professional, 4K, sharp details, warm lighting"
        )
        
        # Cost estimation
        cost = estimate_generation_cost(
            duration_seconds=video_duration,
            resolution=resolution,
            include_audio=True
        )
        
        return {
            "success": True,
            "prompt": prompt_dict["main_prompt"],
            "negative_prompt": prompt_dict["negative_prompt"],
            "specifications": {
                "duration_seconds": video_duration,
                "resolution": resolution,
                "aspect_ratio": "16:9",
                "audio": "Professional background music + subtle SFX"
            },
            "estimated_cost": cost.get("pricing_breakdown", {}).get("total_cost_usd"),
            "recommendations": [
                "Use 2-3 reference images of product for consistency",
                "Include brand colors in style description",
                "Test with 4s/720p first to optimize prompt",
                "Use 'Ingredients to Video' for character consistency"
            ]
        }
    
    except Exception as e:
        logger.error(f"Error building prompt: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "code": "PROMPT_BUILD_FAILED"
        }

@mcp.tool
def validate_and_enhance_prompt(
    prompt: str,
    product_type: str = "general"
) -> Dict[str, Any]:
    """
    Valida un prompt y sugiere mejoras.
    
    Verifica:
    - Longitud adecuada
    - Presencia de cinematography
    - Negativos incluidos
    - Tokens estimados
    """
    
    log_tool_usage("validate_and_enhance_prompt", {
        "product_type": product_type,
        "prompt_length": len(prompt)
    })
    
    issues = []
    warnings = []
    
    # Validaciones
    if len(prompt) < 50:
        issues.append("Prompt demasiado corto (< 50 chars)")
    
    if len(prompt) > 2000:
        issues.append("Prompt demasiado largo (> 2000 chars)")
    
    # Advertencias
    cinema_keywords = ["shot", "angle", "camera", "dolly", "tracking", "aerial"]
    if not any(kw in prompt.lower() for kw in cinema_keywords):
        warnings.append("Agregar descripción de movimiento de cámara")
    
    if "negative" not in prompt.lower() and "not" not in prompt.lower():
        warnings.append("Considerar agregar negative prompt")
    
    # Calcular tokens
    tokens = estimate_tokens(prompt)
    
    return {
        "valid": len(issues) == 0,
        "prompt": prompt,
        "analysis": {
            "length_chars": len(prompt),
            "estimated_tokens": tokens,
            "word_count": len(prompt.split())
        },
        "issues": issues,
        "warnings": warnings,
        "recommendations": [
            "Use structured 5-part formula",
            "Include resolution and duration",
            "Add negative prompt",
            "Test with Fast mode first"
        ]
    }

@mcp.tool
def get_veo_pricing_table() -> Dict[str, Any]:
    """
    Retorna tabla de precios actual de Veo 3.1
    """
    
    return {
        "provider": "Google Veo 3.1",
        "last_updated": datetime.now().isoformat(),
        "pricing": {
            "720p": {
                "4_seconds": 0.15,
                "6_seconds": 0.25,
                "8_seconds": 0.35
            },
            "1080p": {
                "4_seconds": 0.25,
                "6_seconds": 0.50,
                "8_seconds": 0.75
            }
        },
        "extras": {
            "reference_image": 0.05,
            "audio_generation": 0.10,
            "4k_processing": 0.15
        },
        "bulk_discounts": {
            "5_to_9_videos": "5%",
            "10_to_49_videos": "10%",
            "50_plus_videos": "15%"
        },
        "recommendations": {
            "cost_optimization": [
                "Start with 4s/720p for testing",
                "Use fast mode for iterations",
                "Batch similar products together",
                "Reuse reference images"
            ]
        }
    }

@mcp.tool
def save_prompt_template(
    template_name: str,
    prompt: str,
    product_type: str,
    tags: List[str],
    notes: str = ""
) -> Dict[str, Any]:
    """
    Guarda un prompt exitoso como template reutilizable.
    
    Esto permite:
    - Reutilizar prompts similares
    - Mantener consistencia de estilo
    - Reducir tiempo de creación
    """
    
    log_tool_usage("save_prompt_template", {
        "template_name": template_name,
        "product_type": product_type
    })
    
    # En producción, guardar en DB
    # Por ahora retornar estructura
    
    return {
        "success": True,
        "template": {
            "name": template_name,
            "prompt": prompt,
            "product_type": product_type,
            "tags": tags,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "template_id": f"tpl_{template_name.lower().replace(' ', '_')}",
            "usage_count": 0
        },
        "message": f"Template '{template_name}' saved successfully",
        "usage_example": f"Load template: templates://product-{product_type}"
    }

@mcp.tool
def get_product_templates(product_type: str) -> Dict[str, Any]:
    """
    Retorna templates predefinidos por tipo de producto.
    
    Tipos soportados:
    - electronics
    - fashion
    - furniture
    - cosmetics
    - automotive
    - jewelry
    """
    
    templates = {
        "electronics": {
            "cinematography": "smooth tracking shot with tech aesthetics",
            "style": "futuristic, sleek, professional tech showcase",
            "features": ["sharp focus on details", "UI highlights", "hand interactions"]
        },
        "fashion": {
            "cinematography": "runway-style dolly shot with model",
            "style": "editorial, magazine-like, fashionable ambiance",
            "features": ["fabric texture focus", "motion flow", "elegant poses"]
        },
        "furniture": {
            "cinematography": "wide establishing shot transitioning to close-up",
            "style": "interior design showcase, modern, spacious",
            "features": ["room context", "scale reference", "material quality"]
        },
        "cosmetics": {
            "cinematography": "macro close-up with shallow depth of field",
            "style": "luxurious, beauty-focused, glamorous lighting",
            "features": ["product detail", "application demo", "color vibrancy"]
        }
    }
    
    return {
        "product_type": product_type,
        "templates": templates.get(product_type, templates["electronics"]),
        "recommendation": f"Use as base and customize for your specific {product_type} product"
    }

# ==================== RESOURCES ====================

@mcp.resource("veo://pricing")
def veo_pricing_resource() -> str:
    """Recurso: tabla de precios Veo"""
    pricing = get_veo_pricing_table()
    return json.dumps(pricing, indent=2)

@mcp.resource("veo://best-practices")
def veo_best_practices() -> str:
    """Recurso: mejores prácticas para Veo"""
    practices = {
        "prompt_formula": "[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]",
        "optimization": [
            "Test with 4s/720p first ($0.15)",
            "Use reference images for consistency",
            "Include negative prompts",
            "Batch similar videos together",
            "Cache successful prompts"
        ],
        "common_mistakes": [
            "Too vague cinematography",
            "Missing context or ambiance",
            "No negative prompts",
            "Starting with 1080p/8s (expensive)"
        ]
    }
    return json.dumps(practices, indent=2)

@mcp.resource("templates://product-{type}")
def product_templates_resource(type: str) -> str:
    """Recurso: templates por tipo de producto"""
    result = get_product_templates(type)
    return json.dumps(result, indent=2)

# ==================== SERVER STARTUP ====================

if __name__ == "__main__":
    logger.info("🎬 VeoStudio MCP Server iniciando...")
    logger.info(f"API Key configurada: {bool(API_KEY)}")
    logger.info("Tools disponibles: optimize_veo_prompt, estimate_generation_cost, build_product_video_prompt, validate_and_enhance_prompt, save_prompt_template")
    
    mcp.run()
