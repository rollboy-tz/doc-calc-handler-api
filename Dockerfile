FROM python:3.11-slim

# INSTALL SYSTEM DEPENDENCIES FOR WEASYPRINT
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu \
    fonts-freefont-ttf \
    fontconfig \
    && fc-cache -f -v

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Create simple test script to verify PDF works
RUN echo '#!/usr/bin/env python3
import sys
try:
    from weasyprint import HTML
    html = HTML(string=\"<h1>Test PDF</h1><p>If you see this, PDF generation works!</p>\")
    pdf = html.write_pdf()
    print(f\"✅ PDF generation successful: {len(pdf)} bytes\")
    with open(\"/tmp/test_weasyprint.pdf\", \"wb\") as f:
        f.write(pdf)
    print(\"✅ Test PDF saved to /tmp/test_weasyprint.pdf\")
except Exception as e:
    print(f\"❌ Error: {e}\")
    sys.exit(1)
' > /test_pdf.py && python /test_pdf.py

CMD ["python", "app.py"]