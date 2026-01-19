FROM python:3.11-slim

# UPDATE APT SOURCES FIRST
RUN apt-get update && apt-get install -y \
    curl \
    gnupg

# ADD DEBIAN BACKPORTS REPO FOR NEWER PACKAGES
RUN echo "deb http://deb.debian.org/debian bookworm-backports main" >> /etc/apt/sources.list

# INSTALL SYSTEM DEPENDENCIES FOR WEASYPRINT 61+
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libharfbuzz0b \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu \
    fonts-freefont-ttf \
    # Additional fonts
    fontconfig \
    && fc-cache -f -v

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# TEST PDF GENERATION ON STARTUP
RUN python -c "
try:
    from weasyprint import HTML
    html = HTML(string='<h1>Test</h1>')
    pdf = html.write_pdf()
    print('✅ WeasyPrint installation successful')
except Exception as e:
    print(f'❌ WeasyPrint error: {e}')
    raise
"

CMD ["python", "app.py"]