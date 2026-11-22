c.ServerProxy.servers = {
    "monitor": {
        "command": [
            "streamlit",
            "run",
            "dashboard/app.py",
            "--server.port",
            "{port}",
            "--server.headless",
            "true",
            "--server.enableCORS",
            "false",
            "--server.enableXsrfProtection",
            "false",
        ],
        "timeout": 180,
        "environment": {"AURICHELIX_CLOUD": "1"},
        "launcher_entry": {"title": "AuricHelix Monitor"},
    }
}
