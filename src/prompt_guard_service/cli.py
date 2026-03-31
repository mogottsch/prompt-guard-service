from prompt_guard_service.config import Settings


def main() -> None:
    settings = Settings()
    print(
        "prompt-guard-service config: "
        f"host={settings.host} port={settings.port} model_path={settings.model_path}"
    )


if __name__ == "__main__":
    main()
