FROM python:3.11.3-alpine3.18

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

COPY socialnetwork /socialnetwork
COPY scripts /scripts

WORKDIR /socialnetwork

EXPOSE 8000

RUN python -m venv /venv && \
	/venv/bin/pip install --upgrade pip && \
	/venv/bin/pip install -r /socialnetwork/requirements.txt && \
	adduser --disabled-password --no-create-home duser && \
	mkdir -p /data/web/static && \
	mkdir -p /data/web/media && \
	chown -R duser:duser /venv && \
	chown -R duser:duser /data/web/static && \
	chown -R duser:duser /data/web/media && \
	chmod -R 755 /data/web/static && \
	chmod -R 755 /data/web/media && \
	chmod -R +x /scripts

ENV PATH="/scripts:/venv/bin:$PATH"

USER duser

CMD ["commands.sh"]