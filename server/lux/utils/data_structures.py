from lux.models.lux_base_model import LuxBaseModel


def sort_by_id(x: LuxBaseModel) -> int:
    """For situations where orderby is not how we sort."""
    return x.id
