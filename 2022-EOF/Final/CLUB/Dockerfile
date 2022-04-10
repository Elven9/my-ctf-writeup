FROM node:lts-alpine

COPY src /app
WORKDIR /app

RUN npm install

ENV NODE_ENV=production
ENV SESSION_SECRET=example 
EXPOSE 3000/tcp
CMD ["node", "index.js"]
