#!/bin/bash

# Ejemplos de uso del endpoint request-multiple usando curl

# URL base del servidor
BASE_URL="http://localhost:8000"

echo "🐜 Ejemplos de uso con curl"
echo "=================================="

# 1. Solicitud básica exitosa
echo -e "\n1️⃣ Solicitud básica de 5 hormigas para Defense:"
curl -X POST "$BASE_URL/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "Defense",
    "quantity": 5,
    "priority": 1,
    "estimated_duration_seconds": 120
  }' | python -m json.tool

# 2. Solicitud con parámetros mínimos
echo -e "\n2️⃣ Solicitud mínima (usa valores por defecto):"
curl -X POST "$BASE_URL/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "Communication",
    "quantity": 3
  }' | python -m json.tool

# 3. Solicitud que probablemente falle (muchas hormigas)
echo -e "\n3️⃣ Solicitud de muchas hormigas (probablemente falle):"
curl -X POST "$BASE_URL/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "Collection",
    "quantity": 100
  }' | python -m json.tool

# 4. Verificar estado de la colonia
echo -e "\n4️⃣ Estado actual de la colonia:"
curl -X GET "$BASE_URL/colony/status/comprehensive" | python -m json.tool

# 5. Solicitud con todos los parámetros
echo -e "\n5️⃣ Solicitud completa con todos los parámetros:"
curl -X POST "$BASE_URL/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "Defense",
    "quantity": 2,
    "priority": 1,
    "estimated_duration_seconds": 45
  }' | python -m json.tool

# 6. Ejemplo con jq para procesar la respuesta (si está instalado)
if command -v jq &> /dev/null; then
    echo -e "\n6️⃣ Procesando respuesta con jq:"
    RESPONSE=$(curl -s -X POST "$BASE_URL/ants/request-multiple" \
      -H "Content-Type: application/json" \
      -d '{
        "subsystem_name": "Communication",
        "quantity": 2
      }')

    echo "Resultado: $(echo $RESPONSE | jq -r '.message')"
    echo "Hormigas asignadas: $(echo $RESPONSE | jq -r '.ants | length')"
    echo "Usadas: $(echo $RESPONSE | jq -r '.ants_used')"
    echo "Creadas: $(echo $RESPONSE | jq -r '.ants_created')"
else
    echo -e "\n⚠️ jq no está instalado. Instalar con: brew install jq (Mac) o apt-get install jq (Linux)"
fi

# 7. Guardar respuesta en archivo
echo -e "\n7️⃣ Guardando respuesta en archivo:"
curl -X POST "$BASE_URL/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "Collection",
    "quantity": 3,
    "priority": 2
  }' -o response.json

echo "Respuesta guardada en response.json"
cat response.json | python -m json.tool

# 8. Ejemplo con verbose para debugging
echo -e "\n8️⃣ Solicitud con modo verbose (para debugging):"
curl -v -X POST "$BASE_URL/ants/request-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "subsystem_name": "Defense",
    "quantity": 1
  }' 2>&1 | grep -E "< HTTP|< content-type|{.*}"