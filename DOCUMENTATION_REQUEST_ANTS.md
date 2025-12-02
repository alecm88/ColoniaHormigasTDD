# 📦 Documentación: Endpoint request-multiple

## 🎯 Propósito
El endpoint `/ants/request-multiple` permite solicitar múltiples hormigas de forma atómica para asignación a un subsistema específico.

## ⚡ Características Principales

### Operación Atómica
- ✅ **Todo o nada**: Se asignan TODAS las hormigas solicitadas o NINGUNA
- 🔄 **Rollback automático**: Si falla parcialmente, revierte cualquier asignación

### Estrategia de Asignación
1. **Prioridad a existentes**: Usa primero hormigas disponibles en la colonia
2. **Creación inteligente**: Crea nuevas hormigas solo si es necesario
3. **Validación de recursos**: Verifica capacidad y stock de comida antes de proceder

## ⚠️ IMPORTANTE: Cálculo de Duración

### 📐 Fórmula de Cálculo:
```
estimated_duration_seconds + 10s_tiempo_espera ≤ 90s_vida_útil_por_defecto
```

**Tiempo de espera fijo**: Cada hormiga requiere **10 segundos adicionales** de tiempo de espera automáticamente.

### ✅ Ejemplos válidos:
| estimated_duration_seconds | Tiempo espera | Total | ¿Válido? |
|---------------------------|---------------|-------|-----------|
| 40 | 10s | 50s | ✅ (50 ≤ 90) |
| 60 | 10s | 70s | ✅ (70 ≤ 90) |
| 70 | 10s | 80s | ✅ (80 ≤ 90) |
| 79 | 10s | 89s | ✅ (89 ≤ 90) |

### ❌ Ejemplos inválidos:
| estimated_duration_seconds | Tiempo espera | Total | ¿Por qué falla? |
|---------------------------|---------------|-------|-----------------|
| 80 | 10s | 90s | ❌ Margen muy estrecho (timing issues) |
| 85 | 10s | 95s | ❌ Excede vida útil (95 > 90) |
| 120 | 10s | 130s | ❌ Muy por encima del límite |

## 🛡️ Recomendaciones

### Para Solicitudes Seguras:
1. **Máximo recomendado**: `estimated_duration_seconds: 79`
2. **Valor por defecto seguro**: `estimated_duration_seconds: 60` (se usa si se omite)
3. **Para pruebas**: `estimated_duration_seconds: 40`

### Para Tareas Más Largas:
Primero configure la colonia:
```json
POST /colony/configure
{
  "ant_lifespan_minutes": 3.0
}
```
Luego solicite con duraciones mayores:
```json
POST /ants/request-multiple
{
  "estimated_duration_seconds": 150,
  "quantity": 5,
  "subsystem_name": "defense"
}
```

## 📊 Parámetros del Endpoint

### Parámetros de Entrada:
```json
{
  "subsystem_name": "defense|communication|collection",
  "quantity": 1-99,
  "priority": 1-3,
  "estimated_duration_seconds": 1-79
}
```

### Respuesta:
```json
{
  "success": true/false,
  "message": "Descripción del resultado",
  "ants": [...],
  "ants_used": 0,
  "ants_created": 5,
  "available": 0,
  "can_create": 95,
  "requested": 5
}
```

## 🚨 Casos de Fallo

La operación falla cuando:
1. **Duración excesiva**: `estimated_duration_seconds + 10 > vida_útil`
2. **Recursos insuficientes**: No hay suficientes hormigas disponibles + creables
3. **Subsistema inválido**: El subsistema no existe
4. **Cantidad inválida**: quantity ≤ 0
5. **Sin comida**: No hay suficiente comida para crear hormigas nuevas
6. **Capacidad llena**: Se ha alcanzado el límite máximo de hormigas

## 💡 Ejemplos de Uso

### Ejemplo 1: Solicitud Básica Segura
```bash
curl -X POST "http://localhost:8000/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "defense",
    "quantity": 5,
    "priority": 1,
    "estimated_duration_seconds": 40
  }'
```

### Ejemplo 2: Usando Valores por Defecto
```bash
curl -X POST "http://localhost:8000/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "communication",
    "quantity": 3
  }'
```

### Ejemplo 3: Para Tareas Largas (Configurando Colonia Primero)
```bash
# Paso 1: Configurar colonia
curl -X POST "http://localhost:8000/colony/configure" \
  -H "Content-Type: application/json" \
  -d '{"ant_lifespan_minutes": 5.0}'

# Paso 2: Solicitar con duración mayor
curl -X POST "http://localhost:8000/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "collection",
    "quantity": 2,
    "estimated_duration_seconds": 200
  }'
```

## 🔗 Endpoints Relacionados
- `POST /ants/request`: Solicitar una sola hormiga
- `POST /ants/emergency`: Solicitar hormigas de emergencia
- `GET /colony/status/comprehensive`: Ver estado de la colonia
- `POST /colony/configure`: Configurar parámetros de la colonia

## 📚 Recursos Adicionales
- Documentación interactiva: http://localhost:8000/docs
- Esquemas de API: http://localhost:8000/redoc
- Estado de la colonia: http://localhost:8000/colony/status/comprehensive