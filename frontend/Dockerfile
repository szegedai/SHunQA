FROM node:18-alpine

WORKDIR /app

COPY . .

RUN rm -rf node_modules/

RUN npm install

RUN npm run build

ENV HOST 0.0.0.0
EXPOSE 3000

ENTRYPOINT [ "node", ".output/server/index.mjs" ]