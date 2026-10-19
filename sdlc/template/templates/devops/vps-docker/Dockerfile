# Dockerfile for {{BE_REPO}} — multi-stage Node build (adapt stages for non-Node stacks)
FROM node:{{NODE_VERSION}}-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN {{INSTALL_CMD}}

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN {{SETUP_CMD}}
RUN {{BUILD_CMD}}

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 appuser

# Next.js standalone output shown below — adjust COPY lines for other stacks.
COPY --from=builder /app/public ./public
COPY --from=builder --chown=appuser:nodejs /app/.next/standalone ./
COPY --from=builder --chown=appuser:nodejs /app/.next/static ./.next/static
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma

USER appuser
EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
