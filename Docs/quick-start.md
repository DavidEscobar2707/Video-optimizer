# VeoStudio: Quick Start & Setup Guide

## 🚀 5 Minutos para Empezar

### Paso 1: Clonar & Setup Inicial
```bash
# Clonar proyecto
git clone https://github.com/yourusername/veo-studio.git
cd veo-studio

# Instalar dependencias
npm install

# Instalar FastMCP para MCP Server
pip install fastmcp>=2.12.3 google-generativeai
```

### Paso 2: Configurar Variables de Entorno
```bash
# Crear archivo .env.local
cat > .env.local << 'EOF'
# Gemini API Key (obtener de ai.google.dev)
GEMINI_API_KEY=your-api-key-here
NEXT_PUBLIC_GEMINI_API_KEY=your-public-key-here

# Base de datos (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/veo_studio

# Redis (para queue de videos)
REDIS_URL=redis://localhost:6379

# Supabase Storage (para guardar videos)
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_BUCKET=veo-videos

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development
EOF
```

### Paso 3: Configurar MCP en Cursor
```bash
# Crear estructura .cursor
mkdir -p ~/.cursor

# Actualizar ~/.cursor/mcp.json
cat > ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "veo-studio": {
      "type": "stdio",
      "command": "python3",
      "args": ["$(pwd)/mcp-server/server.py"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
EOF

# Reiniciar Cursor
```

### Paso 4: Start Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Next.js Dev Server
npm run dev
# http://localhost:3000 está listo

# Terminal 3: MCP Server (en Cursor o standalone)
cd mcp-server
python3 server.py
```

---

## 📋 Project Structure Explained

```
veo-studio/
├── src/app/
│   ├── api/videos/generate.ts      ← API endpoint para generar videos
│   ├── api/videos/[id]/status.ts   ← Polling status de generación
│   └── studio/page.tsx              ← UI principal para crear videos
│
├── src/lib/
│   ├── gemini.ts                   ← Cliente Gemini configurado
│   ├── veo-prompt-builder.ts       ← Constructor de prompts
│   └── token-optimizer.ts          ← Optimizador de costos
│
├── mcp-server/
│   └── server.py                   ← FastMCP Server tools
│
├── .cursor/rules/
│   ├── .cursorrules                ← Reglas principales
│   ├── veo-prompts.md              ← Guía de prompts
│   └── context-engineering.md      ← Principios de context
│
└── docs/
    ├── ARCHITECTURE.md
    ├── VEO_PROMPTING.md
    └── COST_OPTIMIZATION.md
```

---

## 🎯 Flujo Típico de Uso

### Escenario: Generar video de un iPhone

#### 1. Desde UI Dashboard
```
1. Click en "New Video"
2. Seleccionar "Electronics" como tipo de producto
3. Ingresar:
   - Product Name: "iPhone 15 Pro"
   - Key Features: ["Titanium design", "A17 Pro chip", "48MP camera"]
   - Target Style: "Professional, cinematic"
   - Duration: "6 segundos"
   - Resolution: "1080p"
4. Click "Generate"
5. Sistema calcula costo: $0.50
6. Video inicia generación
7. Polling status cada 2 segundos
8. En ~2-3 minutos: video completado
```

#### 2. Desde Cursor (MCP Integration)
```
En Cursor, usar comando MCP:

@veo-studio optimize_veo_prompt
  product_name: "iPhone 15 Pro"
  key_features: ["Titanium", "A17 Pro", "Camera"]
  desired_style: "cinematic, professional"

→ Retorna:
  - Prompt optimizado (5-parte formula)
  - Estimated tokens: 120
  - Estimated cost: $0.50
  - Recomendaciones
```

#### 3. Programáticamente (API)
```bash
curl -X POST http://localhost:3000/api/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Close-up tracking shot | premium iPhone 15 Pro with titanium design | 
              rotating 360 degrees | minimalist white studio | 
              photorealistic, cinematic, warm gold lighting, sharp focus",
    "duration": 6,
    "resolution": "1080p",
    "aspectRatio": "16:9"
  }'

→ Response:
{
  "success": true,
  "data": {
    "videoId": "vid_abc123",
    "status": "queued",
    "estimatedCost": 0.50,
    "createdAt": "2025-11-02T..."
  }
}
```

---

## 💰 Cost Optimization Tips

### ❌ Approach Ineficiente (Caro)
```
- Generar directamente en 1080p/8s ($0.75)
- No usar reference images (genera variaciones)
- No cachear prompts exitosos
- Generar múltiples variantes en paralelo
→ Costo por producto: $3-5
```

### ✅ Approach Optimizado (Barato)
```
Paso 1: Test & Iterate ($0.15)
- Generar en 4s/720p ($0.15)
- Perfeccionar prompt
- Guardar como template

Paso 2: Production ($0.50)
- Usar template exitoso
- Generar en 6s/1080p ($0.50)
- Usar reference images (guardar por 24h)

Paso 3: Batch ($0.40 c/u)
- Procesar 5 videos similares en lote
- 10% descuento por batch
→ Costo por producto: $0.40-0.50 (80% ahorrado)
```

### Estrategia de 3 Tiers

**Tier 1: Fast Testing ($0.15)**
```
- Duración: 4s
- Resolución: 720p
- Uso: Iteración y prueba de prompts
- Batching: No necesario
- Time: ~30 segundos
```

**Tier 2: Standard Production ($0.50)**
```
- Duración: 6s
- Resolución: 1080p
- Uso: Mayoría de videos de producto
- Batching: 5-10 videos
- Time: ~2-3 minutos
```

**Tier 3: Premium Cinema ($0.75)**
```
- Duración: 8s
- Resolución: 1080p
- Uso: Campañas principales
- Batching: Solo para proyectos grandes
- Time: ~3-4 minutos
```

---

## 🔧 Troubleshooting

### Error: "GEMINI_API_KEY not configured"
```bash
# Verificar variable
echo $GEMINI_API_KEY

# Si no existe, agregar a .env.local
echo "GEMINI_API_KEY=your-key" >> .env.local

# Reiniciar servidor
npm run dev
```

### Error: "Video generation timeout"
```bash
# Aumentar timeout en next.config.ts
timeout: 600 // 10 minutos

# O usar polling más frecuente
// Poll cada 5 segundos en lugar de 2
setInterval(() => checkStatus(), 5000)
```

### Error: "Redis connection failed"
```bash
# Verificar Redis running
redis-cli ping
# Debe retornar: PONG

# Si no:
redis-server --daemonize yes
```

### Error: "MCP Server not recognized in Cursor"
```bash
# 1. Verificar archivo mcp.json existe
cat ~/.cursor/mcp.json

# 2. Verificar path es correcto
which python3

# 3. Actualizar path en mcp.json:
"args": ["/usr/bin/python3", "$(pwd)/mcp-server/server.py"]

# 4. Reiniciar Cursor completamente
```

---

## 📚 Recomendaciones Clave

### Context Engineering Best Practices
```
1. Documentar TODO en archivos versionados
   - Prompts exitosos → templates
   - Patrones encontrados → docs/
   - Decisiones arquitectónicas → .cursorrules

2. Usar lazy loading de contexto
   - No cargar todo en memoria
   - Cargar solo lo relevante por tarea
   - Cache de 24 horas

3. Versionar cambios
   - Cada cambio de prompt = nueva versión
   - Tracking de resultados
   - A/B testing automático
```

### Token Optimization
```
1. Batch requests
   - 5 videos similares = 1 prompt optimizado
   - Guardar reference images
   - Reutilizar en 24 horas

2. Cache agresivo
   - Prompts exitosos: cache infinito
   - Imágenes de referencia: cache 24h
   - Resultados de generación: cache 7 días

3. Monitoreo
   - Log de tokens por usuario
   - Alertas si se acerca al límite
   - Reporting diario de consumo
```

### API Best Practices
```
1. Validación siempre
   - Zod schemas en TODOS los endpoints
   - No confiar en entrada del usuario
   - Error messages específicos

2. Error handling
   - Códigos de error personalizados
   - Retry logic automático
   - Logging detallado

3. Seguridad
   - NEVER log full API keys
   - Validar user_id en cada request
   - Rate limiting por user + IP
```

---

## 🔍 Debugging en Cursor con MCP

### Ver logs del MCP Server
```bash
# Terminal donde corre MCP Server
# Debería ver logs como:
# [INFO] MCP Tool called: optimize_veo_prompt
# [INFO] timestamp: 2025-11-02T10:00:00...
```

### Usar Context Manager para debugging
```typescript
// En Cursor, puedes hacer:
@veo-studio build_product_video_prompt
  product_name: "Test Product"
  key_features: ["Feature 1"]
  target_audience: "Tech professionals"
  brand_style: "Modern"

// Cursor mostrará el resultado completo del MCP Tool
// Incluyendo prompt optimizado, costos, etc.
```

### Performance profiling
```bash
# Agregar timing logs
const start = performance.now()
// ... código ...
const duration = performance.now() - start
console.log(`Task took ${duration}ms`)

# Analizar en logs
# Buscar endpoints lentos
# Optimizar DB queries (add indexes)
```

---

## 📖 Documentación Completa

- **Architecture**: `docs/ARCHITECTURE.md` (system design)
- **Prompting**: `docs/VEO_PROMPTING.md` (5-part formula)
- **Context Engineering**: `docs/CONTEXT_ENGINEERING.md` (best practices)
- **API Docs**: `docs/API.md` (endpoints reference)
- **Cost Optimization**: `docs/COST_OPTIMIZATION.md` (strategies)
- **Deployment**: `docs/DEPLOYMENT.md` (production setup)

---

## 🎓 Learning Resources

### Gemini API
- [Official Docs](https://ai.google.dev/gemini-api/docs)
- [Veo 3.1 Prompting Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)

### FastMCP
- [FastMCP Docs](https://gofastmcp.com)
- [MCP Protocol Spec](https://modelcontextprotocol.io)

### Context Engineering
- [Context Engineering Website](https://contextengineering.ai)
- [Cursor IDE Docs](https://cursor.sh/docs)

---

## ✅ Next Steps

1. ✅ Setup proyecto (este archivo)
2. ✅ Configurar variables de entorno
3. ✅ Start services (Next.js, Redis, MCP)
4. ✅ Crear primer video en UI
5. → Optimizar prompts basado en resultados
6. → Implementar templates reutilizables
7. → Setup CI/CD para deployments
8. → Scale a producción

---

## 💬 Support

- GitHub Issues: [repository/issues](https://github.com/yourusername/veo-studio)
- Discord Community: [invite link]
- Email: support@veostudio.dev

**Happy video generating! 🎬✨**
