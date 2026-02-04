# Venezuela Super Lawyer - Docker Container
# ==========================================
#
# Build:  docker build -t venezuela-super-lawyer .
# Run:    docker run -it --rm -e VSL_ACCESS_KEY=your-key venezuela-super-lawyer
#
# For development with volume mount:
#   docker run -it --rm \
#     -e VSL_ACCESS_KEY=your-key \
#     -v $(pwd)/cases:/app/cases \
#     -v $(pwd)/reportes_legales:/app/reportes_legales \
#     venezuela-super-lawyer

FROM python:3.11-slim

# Metadata
LABEL maintainer="Venezuela Super Lawyer"
LABEL description="Elite AI Legal Operating System for Venezuelan Law"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VSL_MODE=production
ENV VSL_DEBUG=false

# Install system dependencies for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For weasyprint PDF generation
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    # For general utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY references/ ./references/
COPY assets/ ./assets/
COPY tests/ ./tests/
COPY SKILL.md README.md LICENSE INDEX.md ./
COPY .env.example .env.example

# Create necessary directories
RUN mkdir -p cases reportes_legales logs cache/tsj cache/gaceta

# Set permissions
RUN chmod +x scripts/*.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash vsl && \
    chown -R vsl:vsl /app
USER vsl

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.path.insert(0, 'scripts'); from gaceta_verify import get_statistics; print(get_statistics())" || exit 1

# Default command - interactive Python shell with VSL modules
CMD ["python3", "-i", "-c", "import sys; sys.path.insert(0, 'scripts'); \
from gaceta_verify import *; \
from tsj_search import *; \
from voting_map import *; \
from constitution_diff import *; \
from constitutional_test import *; \
print('\\n╔══════════════════════════════════════════════════════════════╗'); \
print('║     VENEZUELA SUPER LAWYER - Interactive Legal Console        ║'); \
print('║                                                               ║'); \
print('║  Available modules:                                           ║'); \
print('║    - gaceta_verify: search_norms(), get_statistics()         ║'); \
print('║    - tsj_search: buscar_por_texto(), buscar_vinculantes()    ║'); \
print('║    - voting_map: analyze_proposal(), generate_voting_map()   ║'); \
print('║    - constitution_diff: get_article(), search_articles()     ║'); \
print('║    - constitutional_test: run_all_tests()                    ║'); \
print('╚══════════════════════════════════════════════════════════════╝\\n')"]

# Alternative entrypoints:
# Run specific script:
#   docker run venezuela-super-lawyer python3 scripts/gaceta_verify.py search hidrocarburos
# Run tests:
#   docker run venezuela-super-lawyer pytest tests/ -v
# Interactive bash:
#   docker run -it venezuela-super-lawyer /bin/bash
