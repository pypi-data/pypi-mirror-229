from ...delivery._data._validators import (
    ContentValidator,
    ValidatorContainer,
)


class NewsUDFContentValidator(ContentValidator):
    def __init__(self) -> None:
        super().__init__()
        self.validators.append(self.content_data_has_no_error)


validator = ValidatorContainer(content_validator=NewsUDFContentValidator())
