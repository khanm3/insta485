FROM python:3.10 AS python-deps
WORKDIR /workdir
COPY requirements.txt setup.py ./
COPY insta485/api ./insta485/api
COPY insta485/views ./insta485/views
COPY insta485/__init__.py insta485/config.py insta485/model.py ./insta485
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

FROM node:22 AS node-deps
WORKDIR /workdir
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps .

FROM node-deps AS build-js-prod
COPY webpack.config.js ./
COPY insta485/js ./insta485/js
RUN npx webpack

FROM python-deps AS prod
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y sqlite3
COPY sql ./sql
COPY bin ./bin
# exec into container to run "./bin/insta485db create" if no db created
COPY insta485/templates ./insta485/templates
COPY insta485/static/images ./insta485/static/images
COPY insta485/static/css ./insta485/static/css
COPY --from=build-js-prod /workdir/insta485/static/js /workdir/insta485/static/js
ENV FLASK_APP=insta485
CMD ["flask", "run", "--host", "0.0.0.0"]
