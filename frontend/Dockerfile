FROM nginx:alpine

LABEL maintainer="Hiqode DevOps Team"
LABEL project="Vote App - Frontend Pod"
LABEL version="1.0"

RUN rm -rf /usr/share/nginx/html/*

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/

RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]