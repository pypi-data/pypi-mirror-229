from fastapi import Query

from .utils import Operations, Pagination, Sort, SortConfig


def filters(field: str, type: str, operations: list[Operations], **kwargs):
    arguments = []
    handlers = []
    for operation in operations:
        op = operation.name.lower()
        if operation == Operations.EQ:
            param = field
        else:
            param = f"{field}:{op}"

        kwargs["alias"] = f'"{param}"'
        kwargs["default"] = None
        keywords = ", ".join([f"{k}={v}" for k, v in kwargs.items()])

        name = f"{field}_{op}"
        argument = f"{name}: {type} | None = Query({keywords})"
        arguments.append(argument)

        formatted_operation = operation.value.replace("replacement", name)
        operation = '{"' + field + '": ' + formatted_operation + "}"
        handler = f"if {name} is not None:\n        return {operation}"
        handlers.append(handler)

    params = ",\n    ".join(arguments)
    body = "\n\n    ".join(handlers) + "\n\n    return " + "{}"
    func = f"def header_func(\n    {params}\n) -> dict:\n    {body}"

    scope = {"Query": Query}
    exec(func, scope)
    return scope["header_func"]  # type: ignore


def pagination(
    offset: dict | None = None,
    limit: dict | None = None,
    sort: SortConfig | None = None,
):
    arguments = []
    handlers = []
    if offset is not None:
        offset["default"] = None
        keywords = ", ".join([f"{k}={v}" for k, v in offset.items()])
        arguments.append(f"offset: int | None = Query({keywords})")
        offset_name = "offset"
    else:
        offset_name = "None"

    if limit is not None:
        limit["default"] = None
        keywords = ", ".join([f"{k}={v}" for k, v in limit.items()])
        arguments.append(f"limit: int | None = Query({keywords})")
        limit_name = "limit"
    else:
        limit_name = "None"

    if sort is not None:
        sort.config["default"] = None
        keywords = ", ".join([f"{k}={v}" for k, v in sort.config.items()])
        arguments.append(f"sort: str | None = Query({keywords})")
        handlers.append(
            "    if sort is not None:\n"
            '        fields = sort.split(",")\n'
            "        for field in fields:\n"
            '            if field.startswith("-"):\n'
            "                order = -1\n"
            "            else:\n"
            "                order = 1\n\n"
            "            formatted_sort.append(Sort(field=field, order=order))\n"
        )

    if arguments:
        params = "\n    " + ",\n    ".join(arguments) + ",\n"
    else:
        params = ""

    body = (
        "    formatted_sort = []\n"
        + "\n".join(handlers)
        + f"\n    return Pagination(offset={offset_name}, limit={limit_name}, sort=formatted_sort)"
    )
    func = f"def pagination_func({params}) -> Pagination:\n{body}"
    scope = {"Query": Query, "Pagination": Pagination, "Sort": Sort}
    exec(func, scope)
    return scope["pagination_func"]
