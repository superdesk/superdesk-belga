def init_app(app):
    for resource in ("ingest", "archive", "published"):
        for field in ("body_html",):
            mapping = app.config["DOMAIN"][resource]["schema"][field]["mapping"]
            mapping[
                "search_analyzer"
            ] = "default"  # use custom analyzer from settings.py
