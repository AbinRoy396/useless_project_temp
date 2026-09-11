FROM caddy:2.8-alpine
WORKDIR /srv
COPY index.html app.js pages.css pages.js ./
COPY submit.html pulse.html ai-engine.html roast.html admin.html email.html exhibition.html ./
COPY Caddyfile /etc/caddy/Caddyfile
