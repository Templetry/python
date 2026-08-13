# TemplateApp

FastAPI service generated with [Templetry](https://github.com/Templetry): src layout, pytest with TestClient, optional slim Dockerfile.

```sh
pip install -e .[dev]
uvicorn template_app.main:app --reload   # :8000
pytest
docker build -t template-app .           # docker feature
```

Routes: `GET /healthz` · `GET /api/hello/{name}` · interactive docs at `/docs`.
