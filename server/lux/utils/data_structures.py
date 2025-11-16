from lux.models.lux_base_model import LuxBaseModel


def sort_by_id(x: LuxBaseModel | dict) -> int:
    """For situations where orderby is not how we sort."""
    return x.id if isinstance(x, LuxBaseModel) else x['id']
