FROM node:18-alpine

WORKDIR /app

COPY . .

RUN npm install

RUN npm run build

ENV HOST 0.0.0.0
EXPOSE 3000

ENTRYPOINT node .output/server/index.mjs
# ENTRYPOINT NUXT_APP_BASE_URL=/demo_qa node .output/server/index.mjs
# ENTRYPOINT NUXT_APP_CDN_URL=https://chatbot-rgai3.inf.u-szeged.hu/demo_qa node .output/server/index.mjs
# ENTRYPOINT NUXT_APP_CDN_URL=https://chatbot-rgai3.inf.u-szeged.hu/demo_qa/ NUXT_APP_BASE_URL=/demo_qa/ node .output/server/index.mjs