# When loading data from a table we
# - determine the Pydantic instance to use
# - determine the model to use
# - do an "update_or_create" on the model

import importlib
from pathlib import Path
from types import ModuleType
from typing import Type, Union

from django.db import models
from pydantic import BaseModel
from rich.console import Console
from rich.progress import Progress

from mdb_codegen.djaccess import AccessTableNames, PNDSAccessTableNames
from mdb_codegen.jsontools import FieldRenamer, NamerProto
from mdb_codegen.mdbtools import AccessDatabase, AccessTable

console = Console()


def _get_pk(model: Type[models.Model]) -> models.Field:
    for field in model._meta.fields:
        if getattr(field, "primary_key", False) is True:
            return field
    raise KeyError("No primary key?")


class ModelUpdater:
    def __init__(
        self,
        app_label: str,
        table_renamer: Type[AccessTableNames] = AccessTableNames,
        field_namer: Type[NamerProto] = FieldRenamer,
    ):
        self.table_renamer: AccessTableNames = table_renamer()
        self.field_namer: FieldRenamer = field_namer()
        self.models_: ModuleType = importlib.import_module(f"{app_label}.models")
        self.base_models_: ModuleType = importlib.import_module(f"{app_label}.base_models")

    def update_from_table(self, table: AccessTable, sample_only: bool = False):
        try:
            model_name = self.table_renamer.model(table)
            django_model: models.Model = getattr(self.models_, model_name)
        except AttributeError as E:
            raise AttributeError(f"Expected a model named {model_name} repreenting Access table {table}") from E
        pydantic_base_model: BaseModel = getattr(self.base_models_, self.table_renamer.base_model(table))
        qs: models.QuerySet = django_model.objects

        django_pk = _get_pk(django_model).name
        instances = {}
        fieldmap = {k: getattr(v, "alias", k) for k, v in pydantic_base_model.__fields__.items()}
        # Map the Django primary key to Pydantic instances extracted from the model
        for i in qs.all():
            pydantic_instance = pydantic_base_model.parse_obj(
                {alias: getattr(i, fieldname) for fieldname, alias in fieldmap.items()}
            )
            instances[getattr(pydantic_instance, django_pk)] = pydantic_instance

        lines = [json.replace(b"1900-01-00", b"1900-01-01") for json in table.json()]

        with Progress() as progress:
            counts = dict(changed=0, created=0, skipped=0, exceptions=0)
            task = progress.add_task(f"Import {table.table}", total=len(lines))
            for line in lines:
                try:
                    pydantic_instance = pydantic_base_model.parse_raw(line)
                    pydantic_pk = getattr(pydantic_instance, django_pk)
                    if pydantic_pk not in instances:
                        qs.create(**{i: j for i, j in pydantic_instance})
                        counts["created"] += 1
                    elif instances[pydantic_pk] != pydantic_instance:
                        changed = {i: j for i, j in pydantic_instance if getattr(instances[pydantic_pk], i) != j}
                        qs.filter(pk=pydantic_pk).update(**changed)
                        counts["changed"] += 1
                    else:
                        counts["skipped"] += 1
                except Exception as E:
                    progress.console.print(f"[red]Exception importing {table.table} pk {pydantic_pk}")
                    progress.console.print(f"[red]{E}")
                    counts["exceptions"] += 1
                    continue
                finally:
                    progress.advance(task)
        console.print(counts)

    def __call__(self, target: Union[AccessDatabase, AccessTable], include: list[str] | None = None):
        if isinstance(target, AccessTable):
            try:
                return self.update_from_table(target)
            except AttributeError as E:
                console.log(f"[red]{E}")
                return
        elif isinstance(target, AccessDatabase):
            for table in target.tables.values():
                if include and table.table not in include:
                    continue
                self.__call__(table)
            return
        elif isinstance(target, Path):
            return self.__call__(AccessDatabase(target))

        raise TypeError("Expected either a Table or a Database instance")


class PndsModelUpdater(ModelUpdater):
    def __init__(self):
        super().__init__(app_label="pnds_data", table_renamer=PNDSAccessTableNames)

    def __call__(self, target=AccessDatabase(Path.home() / "PNDS_Interim_MIS-Data.accdb")):
        super().__call__(target=target)
