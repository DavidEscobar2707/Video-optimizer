# VeoStudio: Production-Ready AI Video Generator for Products
## Context Engineering + Next.js + Gemini API + MCP

---

## 📋 Project Overview

**VeoStudio** es una plataforma enterprise-grade para generar videos de productos de calidad profesional usando:
- **Gemini API** (Veo 3.1) como motor de generación de videos
- **Next.js 15** como framework frontend/backend
- **Model Context Protocol (MCP)** para integración con Cursor
- **Context Engineering** para máxima eficiencia de tokens y reproducibilidad

### Objetivos Clave
1. Generar videos production-ready de productos con máxima calidad
2. Minimizar costos de tokens y créditos de Veo
3. Implementar prácticas de context engineering en Cursor
4. Automatizar flujos de trabajo de video generativo
5. Mantener consistencia de marca y estilos

---

## 🏗️ Stack Tecnológico

### Backend
- **Runtime**: Node.js 18+
- **Framework**: Next.js 15 (API Routes)
- **ORM/DB**: Prisma + PostgreSQL (para persistencia)
- **AI SDK**: @google/generative-ai (oficial de Google)
- **Task Queue**: Bull (Redis) para procesamiento asincrónico
- **Storage**: Supabase Storage (videos generados)

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI**: React 19 + Tailwind CSS 4
- **State Management**: TanStack Query v5
- **Video Player**: react-player
- **Forms**: React Hook Form + Zod

### DevOps & Tools
- **MCP Server**: FastMCP (Python)
- **Cursor Integration**: MCP Protocol
- **Deployment**: Vercel + Railway (backend)
- **Monitoring**: Sentry (errores)
- **Environment**: .env.local

---

## 📁 Estructura de Proyecto

```
veo-studio/
├── .cursor/
│   ├── mcp.json                    # Configuración MCP para Cursor
│   └── rules/
│       ├── .cursorrules            # Reglas principales
│       ├── api-standards.md        # Estándares API
│       ├── veo-prompts.md          # Mejores prácticas de prompts
│       └── context-engineering.md  # Principios de context engineering
│
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Layout principal
│   │   ├── page.tsx                # Landing page
│   │   ├── dashboard/
│   │   │   ├── page.tsx            # Dashboard
│   │   │   └── [id]/
│   │   │       ├── page.tsx        # Detalles de proyecto
│   │   │       └── edit.tsx        # Editar proyecto
│   │   ├── api/
│   │   │   ├── auth/               # Autenticación
│   │   │   ├── videos/
│   │   │   │   ├── generate.ts     # Generar video
│   │   │   │   ├── [id]/status.ts  # Estado de generación
│   │   │   │   └── [id]/download.ts # Descargar
│   │   │   ├── projects/           # CRUD de proyectos
│   │   │   └── mcp/
│   │   │       └── tools.ts        # Endpoints MCP
│   │   └── studio/
│   │       ├── page.tsx            # Studio principal
│   │       └── editor.tsx          # Editor de prompts
│   │
│   ├── lib/
│   │   ├── gemini.ts               # Cliente Gemini configurado
│   │   ├── veo-prompt-builder.ts   # Constructor de prompts Veo
│   │   ├── token-optimizer.ts      # Optimizador de tokens
│   │   ├── context-manager.ts      # Gestor de contexto
│   │   ├── db.ts                   # Prisma client
│   │   └── redis.ts                # Redis client
│   │
│   ├── services/
│   │   ├── video-generator.ts      # Servicio de generación
│   │   ├── prompt-engineer.ts      # Ingeniería de prompts
│   │   ├── project-manager.ts      # Gestión de proyectos
│   │   └── metrics.ts              # Analytics y costos
│   │
│   ├── types/
│   │   ├── index.ts                # Tipos globales
│   │   ├── veo.ts                  # Tipos Veo
│   │   └── database.ts             # Tipos Prisma
│   │
│   ├── components/
│   │   ├── ui/                     # Componentes reutilizables
│   │   ├── video-generator.tsx     # Formulario generador
│   │   ├── prompt-editor.tsx       # Editor de prompts
│   │   └── video-preview.tsx       # Preview de videos
│   │
│   └── utils/
│       ├── constants.ts            # Constantes
│       ├── validators.ts           # Validadores
│       └── helpers.ts              # Funciones auxiliares
│
├── mcp-server/
│   ├── server.py                   # MCP Server FastMCP
│   ├── tools/
│   │   ├── veo_generator.py        # Tool generador Veo
│   │   ├── prompt_optimizer.py     # Tool optimizador
│   │   └── context_analyzer.py     # Tool analizador
│   ├── requirements.txt            # Dependencias Python
│   └── config.py                   # Configuración
│
├── docs/
│   ├── ARCHITECTURE.md             # Documentación arquitectura
│   ├── VEO_PROMPTING.md            # Guía de prompts Veo
│   ├── CONTEXT_ENGINEERING.md      # Guía context engineering
│   ├── API.md                      # Documentación API
│   ├── COST_OPTIMIZATION.md        # Optimización costos
│   └── DEPLOYMENT.md               # Guía deployment
│
├── prisma/
│   └── schema.prisma               # Esquema base de datos
│
├── .env.example                    # Variables de ejemplo
├── .env.local                      # Variables locales (git ignored)
├── tsconfig.json                   # Configuración TypeScript
├── next.config.ts                  # Configuración Next.js
├── tailwind.config.ts              # Configuración Tailwind
└── package.json                    # Dependencias Node

```

---

## 🛠️ Guía de Instalación

### 1. Requisitos Previos
```bash
# Node.js 18+
node --version

# Python 3.10+
python --version

# Git
git --version
```

### 2. Clonar y Setup del Proyecto
```bash
# Clonar repositorio
git clone <repo-url>
cd veo-studio

# Instalar dependencias Node.js
npm install
# o pnpm install

# Instalar FastMCP
pip install fastmcp>=2.12.3
```

### 3. Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env.local

# Editar .env.local con tus credenciales
cat > .env.local << EOF
# Gemini API
GEMINI_API_KEY=your-api-key-here
NEXT_PUBLIC_GEMINI_API_KEY=your-public-key-here

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/veo_studio

# Redis (para queue)
REDIS_URL=redis://localhost:6379

# Supabase Storage
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_BUCKET=veo-videos

# App Settings
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development

# Sentry (opcional)
SENTRY_DSN=your-sentry-dsn
EOF
```

### 4. Base de Datos
```bash
# Instalar PostgreSQL localmente o usar servicio cloud
# Luego ejecutar migraciones
npx prisma migrate dev --name init

# Generar Prisma Client
npx prisma generate
```

### 5. Cursor MCP Configuration
```bash
# Crear archivo de configuración MCP
mkdir -p ~/.cursor

# Agregar contenido a ~/.cursor/mcp.json
cat > ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "veo-studio": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/veo-studio/mcp-server/server.py"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here",
        "DATABASE_URL": "your-db-url"
      }
    }
  }
}
EOF

# Reiniciar Cursor para aplicar cambios
```

---

## 🚀 Primer Inicio

### Start Local Server
```bash
# Terminal 1: Inicia Redis
redis-server

# Terminal 2: Inicia dev server
npm run dev

# La app estará en http://localhost:3000
```

### MCP Server (Cursor Integration)
```bash
# Terminal 3: Inicia MCP Server
cd mcp-server
python server.py
```

---

## 📝 Context Engineering: Cursor Rules

### .cursorrules Principal
```yaml
---
description: VeoStudio Project Standards
globs: **/*
alwaysApply: true
---

# Core Architecture
- Use Next.js 15 App Router (no pages directory)
- API routes via /src/app/api/* structure
- TypeScript strict mode (no any types)
- Environment: PostgreSQL + Redis + Supabase

# TypeScript Standards
- All functions must have explicit return types
- Use interfaces for complex objects
- No implicit any
- Export types as named exports
- Validate inputs with Zod

# Naming Conventions
- Components: PascalCase (VideoGenerator.tsx)
- Utilities: camelCase (videoOptimizer.ts)
- Types: PascalCase with T prefix (TVideoConfig)
- Constants: UPPER_SNAKE_CASE
- API routes: lowercase-dash-separated

# API Standards
- Use typed requests/responses
- Implement error handling with specific codes
- Return consistent JSON structure:
  ```json
  {
    "success": boolean,
    "data": object | null,
    "error": { code: string, message: string } | null
  }
  ```
- Log all operations with context

# Token Optimization
- Always batch API calls when possible
- Cache responses using React Query
- Reuse system prompts in context manager
- Monitor token usage with metrics service

# Veo Prompt Standards
- Use structured 5-part formula:
  [Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
- Always include negative prompts
- Reference product images for consistency
- Validate prompt before sending to API
```

### api-standards.md
```markdown
# API Standards

## Video Generation Endpoint

### POST /api/videos/generate

**Body:**
```json
{
  "prompt": "string (5-part Veo formula)",
  "duration": 4 | 6 | 8,
  "resolution": "720p" | "1080p",
  "aspectRatio": "16:9" | "9:16",
  "referenceImages": ["url1", "url2"],
  "negativePrompt": "string (optional)",
  "projectId": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "videoId": "uuid",
    "status": "queued",
    "createdAt": "ISO 8601",
    "estimatedCost": 0.50,
    "estimatedDuration": "120s"
  }
}
```

## Token Optimization Principles

1. **Batch Requests**: Agrupar múltiples prompts en una sola llamada
2. **Cache Strategy**: Reutilizar respuestas en 1 hora
3. **Prompt Reuse**: Guardar prompts exitosos para templating
4. **Context Persistence**: Mantener memoria de contexto entre requests
```

### veo-prompts.md
```markdown
# Veo 3.1 Prompting Guide for Product Videos

## 5-Part Formula

**[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]**

### Template para Videos de Producto

```
[CAMERA: Close-up with shallow depth of field / Smooth tracking shot / 
 Drone view establishing shot]
[PRODUCT: Sleek smartphone with premium materials]
[ACTION: Rotating slowly to show design details / Being held by elegant hands]
[CONTEXT: Minimalist white studio / Modern living room setting]
[STYLE: Photorealistic, cinematic, professional product photography, 
 warm gold lighting, sharp focus on product]
```

### Best Practices

1. **Especificidad**: Usar adjetivos descriptivos (sleek, premium, elegant)
2. **Movimiento de cámara**: Dolly shot, tracking shot, crane shot
3. **Profundidad**: Shallow depth of field para productos
4. **Iluminación**: Especificar temperatura de color (warm, cool, neutral)
5. **Audio**: Incluir efectos de sonido sutiles para ambiente

### Negative Prompts

Describe lo que NO quieres ver:

```
Negative: low quality, blurry, harsh shadows, unnatural lighting, 
distorted product, watermarks, text overlays, unprofessional,
oversaturated colors
```

### Reference Images Strategy

- Usar imagen de producto para consistency
- Proporcionar referencia de estilo visual
- Incluir paleta de colores deseada

```
Ingredients to Video:
- Reference: product_image.jpg
- Style: professional_lighting_setup.jpg
- Environment: studio_setting.jpg
```
```

### context-engineering.md
```markdown
# Context Engineering para VeoStudio

## Principios

1. **Modular Context**: Dividir contexto en capas (proyecto, usuario, sistema)
2. **Persistent Memory**: Guardar contexto entre conversaciones
3. **Lazy Loading**: Cargar solo contexto relevante
4. **Versioning**: Mantener versiones de contexto para reproducibilidad

## Implementación en Cursor

### 1. System Context
```
Eres un experto en generación de videos de productos usando Veo 3.1.
Especializaciones:
- Prompt engineering para videos cinematográficos
- Optimización de tokens Gemini API
- Arquitectura fullstack Next.js
```

### 2. Project Context
```
Proyecto: VeoStudio
Stack: Next.js 15, Gemini API, PostgreSQL, Redis
Objetivo: Generar videos de productos en 30 segundos máximo
Restricciones: Máximo 5 generaciones por usuario/día (free tier)
```

### 3. User Context (por sesión)
```
Usuario: [name]
Proyectos activos: [list]
Historial de prompts: [cached]
Presupuesto tokens: [remaining]
```

### 4. Task Context
```
Tarea: Generar video de producto
Producto: [name]
Duración: 6 segundos
Resolución: 1080p
Estilo: Moderno, profesional
Rango presupuesto: $0.50-$1.00
```

## Memory Management

```typescript
// context-manager.ts
class ContextManager {
  private systemContext: string
  private projectContext: Map<string, string>
  private userContext: Map<string, UserContext>
  
  // Lazy load only relevant context
  async getRelevantContext(task: Task): Promise<string>
  
  // Cache prompt history for reuse
  cachePromptResult(prompt: string, result: any): void
  
  // Version control for reproducibility
  saveContextSnapshot(version: string): void
}
```

## Token Budget

- Sistema de presupuesto por usuario
- Monitoreo de tokens en tiempo real
- Alertas cuando se acerca al límite
- Reporting de consumo por proyecto

```typescript
interface TokenBudget {
  userId: string
  dailyLimit: number
  used: number
  remaining: number
  resetAt: Date
  details: {
    prompts: number
    imageAnalysis: number
    videoGeneration: number
  }
}
```
```

---

## 🔌 MCP Server (FastMCP)

### server.py
```python
from fastmcp import FastMCP
from typing import Optional, List
import os
import google.generativeai as genai

# Inicializar MCP Server
mcp = FastMCP(name="VeoStudio")

# Configurar Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ==================== TOOLS ====================

@mcp.tool
def optimize_veo_prompt(
    product_name: str,
    product_description: str,
    desired_style: str,
    duration_seconds: int = 6,
    resolution: str = "1080p"
) -> dict:
    """
    Optimiza un prompt para Veo usando context engineering.
    Retorna un prompt estructura según la fórmula 5-parte.
    """
    # Implementación...
    pass

@mcp.tool
def estimate_veo_cost(
    prompt: str,
    duration_seconds: int,
    resolution: str,
    quantity: int = 1
) -> dict:
    """
    Estima el costo en créditos de Veo para una generación.
    """
    # Implementación...
    pass

@mcp.tool
def generate_veo_video(
    prompt: str,
    duration: int = 6,
    resolution: str = "1080p",
    aspect_ratio: str = "16:9",
    reference_images: Optional[List[str]] = None
) -> dict:
    """
    Genera un video usando Veo 3.1 a través de Gemini API.
    Retorna video_id para polling del estado.
    """
    # Implementación...
    pass

@mcp.tool
def analyze_video_quality(video_id: str) -> dict:
    """
    Analiza la calidad del video generado.
    Retorna métricas: brightness, contrast, motion smoothness, etc.
    """
    # Implementación...
    pass

@mcp.tool
def save_prompt_template(
    name: str,
    prompt: str,
    product_type: str,
    tags: List[str]
) -> dict:
    """
    Guarda un prompt exitoso como template reutilizable.
    """
    # Implementación...
    pass

# Ejecutar servidor
if __name__ == "__main__":
    mcp.run()
```

---

## 💰 Optimización de Costos

### Estrategia de 3 Niveles

**Tier 1: Fast Generation (Testing)**
- Duración: 4 segundos
- Resolución: 720p
- Costo: ~$0.20
- Uso: Iteración de prompts, validación

**Tier 2: Standard Production**
- Duración: 6 segundos
- Resolución: 1080p
- Costo: ~$0.50
- Uso: Videos finales de productos

**Tier 3: Premium Cinema**
- Duración: 8 segundos
- Resolución: 1080p
- Costo: ~$0.75
- Uso: Campañas principales, presupuesto alto

### Batching Strategy
```typescript
// Procesar múltiples videos simultáneamente
// Máximo 5 requests paralelos para evitar throttling
// Cache de prompts exitosos por 24 horas
// Reuso de reference images
```

### Cost Tracking
```typescript
interface VideoCost {
  videoId: string
  duration: number
  resolution: "720p" | "1080p"
  estimatedCost: number
  actualCost: number
  savedByOptimization: number
  optimizationPercentage: number
}
```

---

## 📊 Monitoring & Observability

### Métricas Clave
- **Token Usage**: Total diario/mensual
- **Video Generation Time**: Promedio, P95, P99
- **Success Rate**: % videos completados exitosamente
- **Cost per Video**: Costo promedio
- **User Satisfaction**: Rating de calidad

### Logging
```typescript
logger.info('Video generation started', {
  videoId: string,
  userId: string,
  prompt: string,
  estimatedCost: number,
  timestamp: Date
})

logger.error('Video generation failed', {
  videoId: string,
  error: string,
  retryCount: number
})
```

---

## 🚀 Deployment

### Vercel (Frontend)
```bash
# Conectar repositorio a Vercel
# Variables de entorno en dashboard Vercel
vercel env add GEMINI_API_KEY
vercel env add DATABASE_URL
vercel env add REDIS_URL

# Deploy automático en push a main
git push origin main
```

### Railway (Backend + Redis)
```bash
# Deploying service
railway link
railway up
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm run test
      - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: vercel deploy --prod
```

---

## ✅ Checklist de Implementación

- [ ] Configurar variables de entorno
- [ ] Crear base de datos PostgreSQL
- [ ] Configurar Redis
- [ ] Instalar dependencias Node.js y Python
- [ ] Configurar MCP en Cursor
- [ ] Crear API client Gemini
- [ ] Implementar video generator service
- [ ] Build UI dashboard
- [ ] Implementar system de prompts
- [ ] Configurar monitoring
- [ ] Setup deployment en Vercel + Railway
- [ ] Documentación de API completa
- [ ] Testing automatizado
- [ ] Performance optimization
- [ ] Security review

---

## 📚 Recursos Adicionales

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Veo 3.1 Prompting Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [FastMCP Documentation](https://gofastmcp.com)
- [Next.js 15 Docs](https://nextjs.org/docs)
- [Context Engineering](https://contextengineering.ai)

---

## 💬 Soporte & Contacto

Para soporte técnico, reportar bugs, o sugerencias:
- GitHub Issues: veo-studio/issues
- Discord: [Community Link]
- Email: support@veostudio.dev

---

**Last Updated**: November 2025
**Maintainer**: VeoStudio Team
**Version**: 1.0.0
