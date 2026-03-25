###1.生成 Dockerfile###

```
    cat > Dockerfile << 'EOF'
    FROM node:22-alpine
    WORKDIR /app
    COPY .output /app
    EXPOSE 3000
    CMD ["node", "server/index.mjs"]
    EOF
```

###2. 重新构建 & 启动

`docker build -t nuxt-app .`

###3. 重新构建 & 启动

`docker run -d --restart always -p 3000:3000 --name nuxt-app nuxt-app`

`docker logs -f nuxt-app`

###4.更新容器

```aiignore
docker stop nuxt-app
docker rm nuxt-app
docker rmi nuxt-app
```