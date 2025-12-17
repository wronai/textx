FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static files
COPY index.html /usr/share/nginx/html/
COPY sdk-demo.html /usr/share/nginx/html/
COPY sdk-demo.css /usr/share/nginx/html/
COPY sdk-demo-app.js /usr/share/nginx/html/
COPY landing-example.html /usr/share/nginx/html/
COPY landing-example.css /usr/share/nginx/html/
COPY landing-example.js /usr/share/nginx/html/
COPY nlp2cmd-sdk.js /usr/share/nginx/html/

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
