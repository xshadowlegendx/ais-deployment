# change this to apache/superset:5.0.0 or whatever version you want to build from;
# otherwise the default is the latest commit on GitHub master branch
FROM apache/superset:6.0.0

USER root

RUN apt-get update && apt-get install -y build-essential

RUN . /app/.venv/bin/activate &&\
  uv pip install Authlib psycopg2

USER superset

CMD ["/app/docker/entrypoints/run-server.sh"]
