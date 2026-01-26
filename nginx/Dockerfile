# Etapa 1: Construir la aplicación de React
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
COPY frontend/.npmrc ./
# Install dependencies with legacy peer deps and ignore scripts to avoid husky issues
RUN npm install --legacy-peer-deps --ignore-scripts
COPY frontend/ ./
RUN npm run build

# Etapa 2: Servir la aplicación con Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
