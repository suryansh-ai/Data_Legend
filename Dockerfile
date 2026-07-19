# Multi-stage Dockerfile: build frontend with Node, run backend with Python
FROM node:18 AS node-build
WORKDIR /app/client
COPY client/package.json client/package-lock.json* ./
COPY client/ ./
RUN npm install --no-audit --prefer-offline || npm install
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .
# Copy built frontend
COPY --from=node-build /app/client/dist ./client/dist

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
