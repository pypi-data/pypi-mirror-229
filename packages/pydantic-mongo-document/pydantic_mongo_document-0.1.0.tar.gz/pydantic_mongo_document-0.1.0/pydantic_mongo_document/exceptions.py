class DocumentNotFound(Exception):
    def __init__(self) -> None:
        super().__init__("Specified document doesn't exist.")
