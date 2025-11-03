# VeoStudio: Code Snippets Ready to Copy-Paste

## 🔧 Utilidades Esenciales

### 1. Veo Prompt Builder

```typescript
// src/lib/veo-prompt-builder.ts
export class VeoPromptBuilder {
  /**
   * Constructor usando 5-part Veo formula
   * [Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
   */
  
  private cinematography: string
  private subject: string
  private action: string
  private context: string
  private style: string
  private negativePrompt: string = ''

  constructor(private productName: string, private productType: string) {}

  setCinematography(cam: string): this {
    this.cinematography = cam
    return this
  }

  setSubject(subj: string): this {
    this.subject = subj
    return this
  }

  setAction(act: string): this {
    this.action = act
    return this
  }

  setContext(ctx: string): this {
    this.context = ctx
    return this
  }

  setStyle(sty: string): this {
    this.style = sty
    return this
  }

  setNegative(neg: string): this {
    this.negativePrompt = neg
    return this
  }

  /**
   * Build prompt string
   */
  build(): string {
    const parts = [
      this.cinematography,
      this.subject,
      this.action,
      this.context,
      this.style
    ]
    
    return parts.filter(p => p).join(' | ')
  }

  /**
   * Build with negative prompt
   */
  buildFull(): { main: string; negative: string } {
    const mainPrompt = this.build()
    
    const negative = this.negativePrompt || [
      'low quality',
      'blurry',
      'distorted product',
      'watermarks',
      'text overlays',
      'harsh shadows',
      'unnatural lighting',
      'oversaturated',
      'unprofessional'
    ].join(', ')

    return {
      main: mainPrompt,
      negative
    }
  }

  /**
   * Preset para tipos de producto
   */
  static forProductType(
    productName: string,
    productType: 'electronics' | 'fashion' | 'furniture' | 'cosmetics',
    features: string[]
  ): VeoPromptBuilder {
    const builder = new VeoPromptBuilder(productName, productType)

    const presets = {
      electronics: {
        cinematography: 'smooth tracking shot with tech aesthetics',
        context: 'minimalist white studio with professional lighting',
        style: 'futuristic, sleek, professional tech showcase, 4K, sharp details'
      },
      fashion: {
        cinematography: 'elegant dolly shot with model movement',
        context: 'high-end boutique or runway setting',
        style: 'editorial, magazine-like, fashionable, luxurious ambiance'
      },
      furniture: {
        cinematography: 'wide establishing shot to detailed close-up',
        context: 'beautifully designed interior space',
        style: 'interior design showcase, modern, spacious, warm lighting'
      },
      cosmetics: {
        cinematography: 'macro close-up with shallow depth of field',
        context: 'luxurious vanity setup with professional lighting',
        style: 'glamorous, beauty-focused, luxurious, vibrant colors'
      }
    }

    const preset = presets[productType]
    const featuresStr = features.slice(0, 3).join(', ')

    return builder
      .setCinematography(preset.cinematography)
      .setSubject(`premium ${productName} featuring ${featuresStr}`)
      .setAction('rotating, showcasing key features, highlighting design details')
      .setContext(preset.context)
      .setStyle(preset.style)
      .setNegative([
        'low quality', 'blurry', 'distorted', 'watermarks',
        'harsh shadows', 'unnatural colors'
      ].join(', '))
  }
}

// Uso:
const prompt = VeoPromptBuilder
  .forProductType('iPhone 15 Pro', 'electronics', [
    'Titanium design',
    'A17 Pro chip',
    '48MP camera'
  ])
  .build()
```

### 2. Token Optimizer

```typescript
// src/lib/token-optimizer.ts
export class TokenOptimizer {
  /**
   * Estimar tokens de un texto
   * Aproximación: 1 palabra ≈ 1.3 tokens
   */
  estimateTokens(text: string): number {
    const words = text.trim().split(/\s+/).length
    return Math.ceil(words * 1.3)
  }

  /**
   * Optimizar prompt para reducir tokens
   */
  optimize(prompt: string, context?: string): string {
    // Remover palabras redundantes comunes
    const redundantWords = [
      'the', 'a', 'an', 'and', 'or', 'but',
      'very', 'really', 'quite', 'extremely',
      'with', 'have', 'has'
    ]

    let optimized = prompt

    redundantWords.forEach(word => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi')
      optimized = optimized.replace(regex, '')
    })

    // Comprimir espacios
    optimized = optimized.replace(/\s+/g, ' ').trim()

    // Usar abbreviaturas
    optimized = optimized
      .replace(/\bcinematography\b/gi, 'cine')
      .replace(/\bphotorealistic\b/gi, '4K photorealistic')

    return optimized
  }

  /**
   * Calcular ahorro de tokens
   */
  calculateSavings(original: string, optimized: string): {
    originalTokens: number
    optimizedTokens: number
    savedTokens: number
    percentSaved: number
  } {
    const originalTokens = this.estimateTokens(original)
    const optimizedTokens = this.estimateTokens(optimized)
    const savedTokens = originalTokens - optimizedTokens

    return {
      originalTokens,
      optimizedTokens,
      savedTokens,
      percentSaved: Math.round((savedTokens / originalTokens) * 100)
    }
  }
}

export const tokenOptimizer = new TokenOptimizer()
```

### 3. Cost Calculator

```typescript
// src/lib/cost-calculator.ts
const VEO_PRICING: Record<string, Record<number, number>> = {
  '720p': {
    4: 0.15,
    6: 0.25,
    8: 0.35
  },
  '1080p': {
    4: 0.25,
    6: 0.50,
    8: 0.75
  }
}

export class CostCalculator {
  /**
   * Calcular costo base de video
   */
  calculateBaseCost(
    resolution: '720p' | '1080p',
    durationSeconds: 4 | 6 | 8
  ): number {
    return VEO_PRICING[resolution]?.[durationSeconds] ?? 0.50
  }

  /**
   * Calcular costo total con extras
   */
  calculateTotal(params: {
    resolution: '720p' | '1080p'
    duration: 4 | 6 | 8
    referenceImages?: number
    includeAudio?: boolean
    quantity?: number
  }): number {
    const baseCost = this.calculateBaseCost(params.resolution, params.duration)
    
    let totalPerVideo = baseCost

    // Extras
    if (params.referenceImages) {
      totalPerVideo += params.referenceImages * 0.05
    }
    if (params.includeAudio) {
      totalPerVideo += 0.10
    }

    // Quantity
    const quantity = params.quantity ?? 1
    let totalCost = totalPerVideo * quantity

    // Batch discount
    if (quantity >= 5) totalCost *= 0.95  // 5% off
    if (quantity >= 10) totalCost *= 0.90 // 10% off
    if (quantity >= 50) totalCost *= 0.85 // 15% off

    return Number(totalCost.toFixed(2))
  }

  /**
   * Comparar costos de diferentes configuraciones
   */
  compare(scenarios: Array<{
    name: string
    resolution: '720p' | '1080p'
    duration: 4 | 6 | 8
    quantity: number
  }>): Array<{
    name: string
    costPerUnit: number
    totalCost: number
    recommendation: boolean
  }> {
    return scenarios.map(scenario => {
      const costPerUnit = this.calculateBaseCost(
        scenario.resolution,
        scenario.duration
      )
      const totalCost = this.calculateTotal({
        ...scenario,
        referenceImages: 0,
        includeAudio: true,
        quantity: scenario.quantity
      })

      return {
        name: scenario.name,
        costPerUnit,
        totalCost,
        recommendation: costPerUnit < 0.50 // Recomendación si < $0.50
      }
    })
  }
}

export const costCalculator = new CostCalculator()
```

### 4. Context Manager

```typescript
// src/lib/context-manager.ts
export interface ContextSnapshot {
  userId: string
  taskType: string
  projectId?: string
  timestamp: Date
  data: Record<string, any>
  version: string
}

export class ContextManager {
  private cache = new Map<string, ContextSnapshot>()
  private contextHistory: ContextSnapshot[] = []

  /**
   * Cargar contexto relevante para una tarea
   */
  async getRelevantContext(params: {
    userId: string
    taskType: 'video_generation' | 'prompt_optimization'
    projectId?: string
  }): Promise<string> {
    const cacheKey = `${params.userId}-${params.taskType}-${params.projectId}`
    
    // Check cache primero
    const cached = this.cache.get(cacheKey)
    if (cached && this.isRecent(cached.timestamp)) {
      return this.serializeContext(cached.data)
    }

    // Load context from DB (en producción)
    const context = {
      userId: params.userId,
      taskType: params.taskType,
      projectId: params.projectId,
      userPreferences: { /* ... */ },
      systemPrompt: this.getSystemPrompt(params.taskType),
      recentPrompts: [], // De historial
      successfulTemplates: [] // De BD
    }

    // Cache por 24 horas
    this.cache.set(cacheKey, {
      ...context,
      timestamp: new Date(),
      version: '1.0'
    })

    return this.serializeContext(context)
  }

  /**
   * System prompt por tipo de tarea
   */
  private getSystemPrompt(taskType: string): string {
    const prompts = {
      video_generation: `You are expert at generating product videos using Veo 3.1.
- Use 5-part formula: [Cinematography] + [Subject] + [Action] + [Context] + [Style]
- Include negative prompts
- Optimize for token efficiency
- Prioritize product quality and brand consistency`,
      
      prompt_optimization: `You are expert at optimizing Veo prompts.
- Improve clarity and specificity
- Reduce tokens while maintaining quality
- Suggest cinematic techniques
- Provide specific camera movements and angles`
    }

    return prompts[taskType] || prompts.video_generation
  }

  /**
   * Serializar contexto a string
   */
  private serializeContext(data: Record<string, any>): string {
    return JSON.stringify(data, null, 2)
  }

  /**
   * Check si cache está reciente (< 24 horas)
   */
  private isRecent(timestamp: Date): boolean {
    const oneDayMs = 24 * 60 * 60 * 1000
    return Date.now() - timestamp.getTime() < oneDayMs
  }

  /**
   * Guardar snapshot para debugging
   */
  async saveSnapshot(
    resourceId: string,
    data: Record<string, any>
  ): Promise<void> {
    const snapshot: ContextSnapshot = {
      userId: data.userId || 'unknown',
      taskType: data.taskType || 'general',
      projectId: data.projectId,
      timestamp: new Date(),
      data: data,
      version: '1.0'
    }

    this.contextHistory.push(snapshot)
    
    // En producción, guardar en BD
    logger.debug(`Context snapshot saved: ${resourceId}`, snapshot)
  }

  /**
   * Retrieve snapshot para debugging
   */
  async getSnapshot(resourceId: string): Promise<ContextSnapshot | null> {
    return this.contextHistory.find(
      s => s.data.resourceId === resourceId
    ) || null
  }

  /**
   * Clear old cache
   */
  clearOldCache(maxAgeHours: number = 24): void {
    const now = Date.now()
    const maxAgeMs = maxAgeHours * 60 * 60 * 1000

    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp.getTime() > maxAgeMs) {
        this.cache.delete(key)
      }
    }

    this.contextHistory = this.contextHistory.filter(
      s => now - s.timestamp.getTime() < maxAgeMs
    )
  }
}

export const contextManager = new ContextManager()
```

### 5. Validadores Zod

```typescript
// src/lib/validators.ts
import { z } from 'zod'

export const VideoGenerationSchema = z.object({
  prompt: z.string()
    .min(50, 'Prompt must be at least 50 characters')
    .max(2000, 'Prompt must be less than 2000 characters'),
  
  duration: z.enum(['4', '6', '8'])
    .transform(Number)
    .refine(v => [4, 6, 8].includes(v), 'Duration must be 4, 6, or 8 seconds'),
  
  resolution: z.enum(['720p', '1080p']),
  
  aspectRatio: z.enum(['16:9', '9:16']).optional().default('16:9'),
  
  referenceImages: z.array(
    z.string().url('Must be valid URL')
  ).optional(),
  
  projectId: z.string().optional(),
  
  userId: z.string().min(1, 'User ID required')
})

export const ProjectSchema = z.object({
  name: z.string().min(3).max(100),
  productName: z.string().min(2).max(100),
  productDesc: z.string().min(10).max(500),
  productType: z.enum(['electronics', 'fashion', 'furniture', 'cosmetics', 'other'])
})

export type VideoGenerationRequest = z.infer<typeof VideoGenerationSchema>
export type ProjectRequest = z.infer<typeof ProjectSchema>

/**
 * Validar request con manejo de errores
 */
export function validateRequest<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: boolean; data?: T; errors?: Record<string, string> } {
  try {
    const parsed = schema.parse(data)
    return { success: true, data: parsed }
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: Record<string, string> = {}
      error.errors.forEach(err => {
        const path = err.path.join('.')
        errors[path] = err.message
      })
      return { success: false, errors }
    }
    return { success: false, errors: { general: 'Validation failed' } }
  }
}
```

---

## 🎯 Uso Completo de Example

```typescript
// Ejemplo: Generar video de iPhone
const productName = 'iPhone 15 Pro'
const features = ['Titanium Design', 'A17 Pro Chip', '48MP Camera']

// 1. Build prompt
const prompt = VeoPromptBuilder
  .forProductType(productName, 'electronics', features)
  .build()

// 2. Estimate tokens
const tokens = tokenOptimizer.estimateTokens(prompt)
console.log(`Tokens: ${tokens}`)

// 3. Optimize prompt
const optimized = tokenOptimizer.optimize(prompt)
const savings = tokenOptimizer.calculateSavings(prompt, optimized)
console.log(`Saved: ${savings.percentSaved}%`)

// 4. Calculate cost
const cost = costCalculator.calculateTotal({
  resolution: '1080p',
  duration: 6,
  quantity: 1,
  includeAudio: true
})
console.log(`Cost: $${cost}`)

// 5. Compare scenarios
const scenarios = [
  { name: 'Fast Test', resolution: '720p' as const, duration: 4 as const, quantity: 1 },
  { name: 'Standard', resolution: '1080p' as const, duration: 6 as const, quantity: 1 },
  { name: 'Premium', resolution: '1080p' as const, duration: 8 as const, quantity: 1 }
]
const comparison = costCalculator.compare(scenarios)
console.table(comparison)

// 6. Load context
const context = await contextManager.getRelevantContext({
  userId: 'user123',
  taskType: 'video_generation',
  projectId: 'proj456'
})
console.log('Context:', context)

// 7. Validate request
const request = {
  prompt: optimized,
  duration: '6',
  resolution: '1080p',
  userId: 'user123'
}
const validation = validateRequest(VideoGenerationSchema, request)
if (validation.success) {
  console.log('Valid request:', validation.data)
} else {
  console.log('Errors:', validation.errors)
}
```

---

**Todos los snippets están listos para copiar-pegar directamente en tu proyecto! 🚀**
