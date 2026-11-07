FROM docker.io/library/node:22-bookworm-slim@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_ROOT=http://127.0.0.1:8000/api/v1
ENV VITE_API_ROOT=$VITE_API_ROOT
RUN npm run build

FROM docker.io/library/node:22-alpine@sha256:0e1754758c2df4cfa3e68d59e2e1b7374bb7fd9ea6328eaaacf15cc934af8202
WORKDIR /app
# Alpine 3.24 musl 1.2.6-r3 is branch-fixed (the scanner incorrectly uses edge r6).
# Pin the compatible zlib security patch from the supported Alpine repository.
RUN apk add --no-cache --upgrade zlib=1.4-r0
# Built assets use only Node built-ins; keep package managers in the build stage.
RUN rm -rf /usr/local/lib/node_modules /opt/yarn-v1.22.22 && \
    rm -f /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/yarn /usr/local/bin/yarnpkg /usr/local/bin/corepack /usr/local/bin/pnpm /usr/local/bin/pnpx
COPY --from=build --chown=node:node /app/dist ./dist
COPY --chown=node:node server.mjs ./server.mjs
USER node
EXPOSE 5173
HEALTHCHECK --interval=5s --timeout=3s --retries=12 CMD ["node","-e","fetch('http://127.0.0.1:5173/_health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
CMD ["node","server.mjs"]
