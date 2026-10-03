# SHIFT Labour Demand Index — deployable container.
# Default service = REST/OpenAPI API (works for ChatGPT Actions + any HTTP agent + browser).
# To run the MCP (streamable-HTTP) service instead, override the start command to:
#     python shift_mcp_server.py http
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shift_data.py shift_mcp_server.py shift_api.py ./

# Hosts set $PORT; default 8000. SHIFT_PUBLIC_URL makes the OpenAPI servers block correct.
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn shift_api:app --host 0.0.0.0 --port ${PORT}"]
