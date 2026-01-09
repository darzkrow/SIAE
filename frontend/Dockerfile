# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Construir para producción
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine

WORKDIR /app

# Instalar servidor HTTP simple para servir archivos estáticos
RUN npm install -g serve

# Copiar archivos construidos del stage anterior
COPY --from=builder /app/dist ./dist

# Copiar package.json para referencia
COPY package*.json ./

EXPOSE 5173

# Servir archivos estáticos en producción
CMD ["serve", "-s", "dist", "-l", "5173"]
