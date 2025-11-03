# VeoStudio: Next.js Implementation Guide

## 📂 Estructura Completa de Carpetas y Archivos

### 1. API Routes Structure

```
src/app/api/
├── videos/
│   ├── generate.ts                 # POST - Generar video
│   ├── route.ts                    # GET - Listar videos del usuario
│   └── [id]/
│       ├── status.ts               # GET - Polling estado
│       ├── download.ts             # GET - Descargar video
│       └── feedback.ts             # POST - Feedback de usuario
│
├── projects/
│   ├── route.ts                    # GET/POST - CRUD proyectos
│   └── [id]/
│       ├── route.ts                # GET/PUT/DELETE proyecto
│       └── videos.ts               # GET - Videos del proyecto
│
├── auth/
│   ├── signin.ts                   # POST - Login
│   ├── signup.ts                   # POST - Registro
│   └── me.ts                       # GET - User info
│
└── mcp/
    └── tools.ts                    # GET - Listar tools disponibles
```

### 2. Lib/Services Structure

```
src/lib/
├── gemini.ts                       # Client de Gemini API
├── veo-prompt-builder.ts           # Constructor de prompts
├── token-optimizer.ts              # Optimizador de tokens
├── context-manager.ts              # Gestor de contexto
├── cost-calculator.ts              # Cálculo de costos
└── validators.ts                   # Zod schemas

src/services/
├── video-generator.ts              # Lógica de generación
├── project-manager.ts              # Gestión de proyectos
├── prompt-engineer.ts              # Ingeniería de prompts
├── budget-manager.ts               # Gestión de presupuesto
└── analytics.ts                    # Tracking de métricas
```

---

## 📝 Código Inicial: API Route Generate Video

### `/src/app/api/videos/generate.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { contextManager } from '@/lib/context-manager'
import { veoPromptBuilder } from '@/lib/veo-prompt-builder'
import { tokenOptimizer } from '@/lib/token-optimizer'
import { costCalculator } from '@/lib/cost-calculator'
import { videoGenerator } from '@/services/video-generator'
import { db } from '@/lib/db'
import { validateRequest } from '@/lib/validators'

// Zod schema para validación
const GenerateVideoSchema = z.object({
  prompt: z.string().min(50).max(2000),
  duration: z.enum(['4', '6', '8']).transform(Number),
  resolution: z.enum(['720p', '1080p']),
  aspectRatio: z.enum(['16:9', '9:16']).optional().default('16:9'),
  referenceImages: z.array(z.string().url()).optional(),
  projectId: z.string().optional(),
  userId: z.string(),
})

type GenerateVideoRequest = z.infer<typeof GenerateVideoSchema>

/**
 * POST /api/videos/generate
 * Generar video usando Veo 3.1
 * 
 * Context Engineering: Usar prompt structure y contexto del usuario
 */
export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID()
  
  try {
    // 1. Validar payload
    const body = await request.json()
    const validated = GenerateVideoSchema.parse(body)

    // 2. Cargar contexto relevante
    const context = await contextManager.getRelevantContext({
      userId: validated.userId,
      taskType: 'video_generation',
      projectId: validated.projectId
    })

    // 3. Verificar presupuesto
    const budget = await db.tokenBudget.findUnique({
      where: { userId: validated.userId }
    })

    const estimatedCost = costCalculator.estimate(
      validated.resolution,
      validated.duration
    )

    if ((budget?.remaining || 0) < estimatedCost) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'INSUFFICIENT_BUDGET',
          message: `Presupuesto insuficiente. Necesitas $${estimatedCost} pero tienes $${budget?.remaining || 0}`
        }
      }, { status: 402 })
    }

    // 4. Optimizar prompt usando context engineering
    const optimizedPrompt = await tokenOptimizer.optimize(
      validated.prompt,
      context
    )

    // 5. Crear registro en DB (antes de generar)
    const videoRecord = await db.videoGeneration.create({
      data: {
        projectId: validated.projectId,
        userId: validated.userId,
        prompt: optimizedPrompt,
        duration: validated.duration,
        resolution: validated.resolution,
        estimatedCost: new Decimal(estimatedCost),
        status: 'queued',
        requestId: requestId,
      }
    })

    // 6. Queue job para generar video
    await videoGenerator.queueGeneration({
      videoId: videoRecord.id,
      prompt: optimizedPrompt,
      duration: validated.duration,
      resolution: validated.resolution,
      referenceImages: validated.referenceImages,
      requestId: requestId,
      context: context // Pasar contexto para consistency
    })

    // 7. Registrar uso de tokens
    await db.tokenUsage.create({
      data: {
        userId: validated.userId,
        videoId: videoRecord.id,
        tokensEstimated: tokenOptimizer.estimateTokens(optimizedPrompt),
        costUsd: new Decimal(estimatedCost),
        type: 'video_generation'
      }
    })

    // 8. Guardar snapshot de contexto para debugging
    await contextManager.saveSnapshot(videoRecord.id, {
      context: context,
      timestamp: new Date(),
      prompt_optimized: optimizedPrompt
    })

    // Respuesta exitosa
    return NextResponse.json({
      success: true,
      data: {
        videoId: videoRecord.id,
        status: 'queued',
        estimatedCost: estimatedCost,
        estimatedDuration: '120s',
        createdAt: videoRecord.createdAt,
        requestId: requestId
      }
    }, { status: 201 })

  } catch (error) {
    logger.error('Video generation error', {
      requestId,
      error: error instanceof Error ? error.message : 'Unknown error',
      errorCode: error instanceof z.ZodError ? 'VALIDATION_ERROR' : 'INTERNAL_ERROR'
    })

    return NextResponse.json({
      success: false,
      error: {
        code: error instanceof z.ZodError ? 'INVALID_REQUEST' : 'INTERNAL_ERROR',
        message: error instanceof Error ? error.message : 'Internal server error',
        requestId: requestId
      }
    }, { status: error instanceof z.ZodError ? 400 : 500 })
  }
}
```

---

## 📚 Lib: Gemini Client

### `/src/lib/gemini.ts`

```typescript
import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from '@google/generative-ai'

const genai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!)

/**
 * Gemini Client centralizado con best practices
 * - Configuración de safety filters
 * - System prompts reutilizables
 * - Error handling
 */

export class GeminiClient {
  private model = genai.getGenerativeModel({
    model: 'gemini-2.5-pro',
    systemInstruction: this.getSystemPrompt()
  })

  private veoModel = genai.getGenerativeModel({
    model: 'veo-2',
    systemInstruction: 'You are an expert at video generation using Veo 3.1. Optimize prompts for cinematic quality.'
  })

  private safetySettings = [
    {
      category: HarmCategory.HARM_CATEGORY_UNSPECIFIED,
      threshold: HarmBlockThreshold.BLOCK_NONE
    }
  ]

  /**
   * System prompt reutilizable (Context Engineering)
   */
  private getSystemPrompt(): string {
    return `You are VeoStudio, an expert AI for generating production-ready product videos.

Your expertise:
- Video cinematography and framing
- Product showcase techniques
- Token optimization for Gemini API
- Prompt engineering for Veo 3.1

Guidelines:
1. Always use 5-part formula: [Cinematography] + [Subject] + [Action] + [Context] + [Style]
2. Include negative prompts in every generation
3. Optimize tokens to reduce costs
4. Prioritize product quality and brand consistency
5. Suggest improvements based on previous results

Never:
- Generate unsafe or offensive content
- Ignore budget constraints
- Skip context understanding
- Compromise on video quality
`
  }

  /**
   * Generar video usando Veo 3.1
   */
  async generateVideo(params: {
    prompt: string
    negativePrompt?: string
    duration: number
    resolution: '720p' | '1080p'
    referenceImages?: string[]
  }): Promise<{
    videoId: string
    status: 'processing' | 'completed' | 'failed'
    metadata: Record<string, any>
  }> {
    try {
      const response = await this.veoModel.generateContent([
        {
          text: `Generate a professional product video with these specifications:
          
Prompt: ${params.prompt}

${params.negativePrompt ? `Negative: ${params.negativePrompt}` : ''}

Duration: ${params.duration} seconds
Resolution: ${params.resolution}
Aspect Ratio: 16:9

Requirements:
- High production quality
- Smooth camera movement
- Professional lighting
- Clear product visibility
- Audio synchronized with video`
        },
        ...(params.referenceImages?.map(url => ({
          inlineData: { mimeType: 'image/jpeg', data: url }
        })) || [])
      ], {
        safetySettings: this.safetySettings,
        generationConfig: {
          temperature: 0.7,
          topK: 40,
          topP: 0.95,
        }
      })

      const result = response.response.text()

      return {
        videoId: `veo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        status: 'processing',
        metadata: {
          promptTokens: result.length,
          resolution: params.resolution,
          duration: params.duration
        }
      }
    } catch (error) {
      logger.error('Veo generation error:', error)
      throw new Error(`Video generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Optimizar prompt usando Gemini análisis
   */
  async optimizePrompt(prompt: string): Promise<string> {
    const response = await this.model.generateContent(`
Optimize this Veo 3.1 prompt for maximum quality while minimizing tokens:

Original: "${prompt}"

Return ONLY the optimized prompt using 5-part formula:
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
    `)

    return response.response.text().trim()
  }

  /**
   * Analizar feedback y mejorar futuros prompts
   */
  async analyzeFeedback(originalPrompt: string, feedback: string): Promise<{
    issues: string[]
    improvements: string[]
    nextPrompt: string
  }> {
    const response = await this.model.generateContent(`
Video prompt analysis and improvement:

Original Prompt: "${originalPrompt}"
User Feedback: "${feedback}"

Analyze the issues and suggest improvements.
Return JSON: { "issues": [...], "improvements": [...], "nextPrompt": "..." }
    `)

    const text = response.response.text()
    const json = JSON.parse(text.match(/\{[\s\S]*\}/)?.[0] || '{}')
    return json
  }
}

// Export singleton instance
export const geminiClient = new GeminiClient()
```

---

## 🛠️ Services: Video Generator

### `/src/services/video-generator.ts`

```typescript
import Bull from 'bull'
import { geminiClient } from '@/lib/gemini'
import { db } from '@/lib/db'
import { supabaseClient } from '@/lib/supabase'
import { logger } from '@/lib/logger'

const videoQueue = new Bull('video-generation', {
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379')
  }
})

export class VideoGeneratorService {
  /**
   * Queue video generation job
   */
  async queueGeneration(params: {
    videoId: string
    prompt: string
    duration: number
    resolution: string
    referenceImages?: string[]
    requestId: string
    context: string
  }): Promise<void> {
    await videoQueue.add(
      {
        ...params,
        timestamp: Date.now()
      },
      {
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 2000
        },
        removeOnComplete: true,
        removeOnFail: false
      }
    )

    logger.info('Video queued for generation', { videoId: params.videoId })
  }

  /**
   * Process video generation
   */
  async processVideoGeneration(job: Bull.Job): Promise<{
    videoId: string
    url: string
    duration: number
    fileSize: number
  }> {
    const { videoId, prompt, duration, resolution, requestId, context } = job.data

    try {
      // Actualizar status a processing
      await db.videoGeneration.update({
        where: { id: videoId },
        data: { status: 'processing' }
      })

      // Generar video con Veo
      const veoResult = await geminiClient.generateVideo({
        prompt,
        duration,
        resolution
      })

      // Simulación de descarga y almacenamiento
      // En producción, llamar API de Veo para obtener video
      const videoBuffer = Buffer.from('mock-video-data')

      // Guardar en Supabase
      const fileName = `${videoId}-${Date.now()}.mp4`
      const { data, error } = await supabaseClient
        .storage
        .from('veo-videos')
        .upload(fileName, videoBuffer, {
          contentType: 'video/mp4'
        })

      if (error) throw error

      // Obtener URL pública
      const { data: urlData } = supabaseClient
        .storage
        .from('veo-videos')
        .getPublicUrl(fileName)

      // Actualizar DB con URL
      await db.videoGeneration.update({
        where: { id: videoId },
        data: {
          status: 'completed',
          videoUrl: urlData.publicUrl,
          completedAt: new Date(),
          actualCost: new Decimal(0.50) // Actualizar con costo real
        }
      })

      logger.info('Video generation completed', {
        videoId,
        url: urlData.publicUrl,
        requestId
      })

      return {
        videoId,
        url: urlData.publicUrl,
        duration,
        fileSize: videoBuffer.length
      }

    } catch (error) {
      logger.error('Video generation failed', {
        videoId,
        error: error instanceof Error ? error.message : 'Unknown error',
        requestId
      })

      await db.videoGeneration.update({
        where: { id: videoId },
        data: {
          status: 'failed',
          errorMsg: error instanceof Error ? error.message : 'Unknown error'
        }
      })

      throw error
    }
  }
}

// Procesador de queue
videoQueue.process(async (job) => {
  const videoGenerator = new VideoGeneratorService()
  return await videoGenerator.processVideoGeneration(job)
})

videoQueue.on('completed', (job) => {
  logger.info('Video generation job completed', { jobId: job.id })
})

videoQueue.on('failed', (job, err) => {
  logger.error('Video generation job failed', { jobId: job.id, error: err.message })
})

export const videoGenerator = new VideoGeneratorService()
```

---

## 📊 Prisma Schema

### `/prisma/schema.prisma`

```prisma
// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  name          String?
  
  tokenBudget   TokenBudget?
  projects      Project[]
  generations   VideoGeneration[]
  usage         TokenUsage[]
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}

model Project {
  id            String    @id @default(cuid())
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  name          String
  productName   String
  productDesc   String
  productType   String    // "electronics", "fashion", etc
  
  videos        VideoGeneration[]
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}

model VideoGeneration {
  id            String    @id @default(cuid())
  projectId     String?
  project       Project?  @relation(fields: [projectId], references: [id], onDelete: SetNull)
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  prompt        String
  veoVideoId    String?
  status        String    // "queued" | "processing" | "completed" | "failed"
  
  duration      Int       // 4, 6, 8
  resolution    String    // "720p" | "1080p"
  aspectRatio   String    @default("16:9")
  
  estimatedCost Decimal   @db.Decimal(10, 2)
  actualCost    Decimal?  @db.Decimal(10, 2)
  
  videoUrl      String?
  errorMsg      String?
  requestId     String?   @unique
  
  usage         TokenUsage?
  
  createdAt     DateTime  @default(now())
  completedAt   DateTime?
  updatedAt     DateTime  @updatedAt
  
  @@index([userId])
  @@index([projectId])
  @@index([status])
}

model TokenBudget {
  id            String    @id @default(cuid())
  userId        String    @unique
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  monthlyLimit  Decimal   @db.Decimal(10, 2)
  used          Decimal   @default(0) @db.Decimal(10, 2)
  
  tier          String    // "free" | "pro" | "enterprise"
  resetAt       DateTime
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}

model TokenUsage {
  id            String    @id @default(cuid())
  userId        String
  user          User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  videoId       String    @unique
  video         VideoGeneration @relation(fields: [videoId], references: [id], onDelete: Cascade)
  
  tokensEstimated Int
  costUsd       Decimal   @db.Decimal(10, 2)
  type          String    // "video_generation" | "prompt_optimization"
  
  createdAt     DateTime  @default(now())
}

model PromptTemplate {
  id            String    @id @default(cuid())
  
  name          String
  prompt        String
  productType   String
  tags          String[]
  
  usageCount    Int       @default(0)
  
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}
```

---

## 🚀 Next Steps

1. ✅ Crear proyecto Next.js: `npx create-next-app@latest veo-studio`
2. ✅ Instalar dependencias
3. ✅ Copiar archivos de este proyecto
4. ✅ Configurar .env.local
5. ✅ Setup database (Prisma migrate)
6. ✅ Crear MCP Server
7. ✅ Configurar Cursor MCP integration
8. ✅ Test endpoints
9. ✅ Build UI components
10. ✅ Deploy a Vercel + Railway

---

**Toda la estructura está lista para empezar a desarrollar! 🚀**
