class Actions:
    """Class to define the actions that can be taken on a resource."""

    View = "view"
    Create = "create"
    Edit = "edit"
    Delete = "delete"

    @staticmethod
    def lookup(func_name: str) -> str:
        return {
            'get': Actions.View,
            'put': Actions.Create,
            'post': Actions.Edit,
            'delete': Actions.Delete,
        }[func_name]
