import sqlite3
import os
from typing import List, Union
from contextlib import contextmanager

_DB_FILE = "{}/cim-11.sqlite3".format(os.path.dirname(__file__))


@contextmanager
def _db_cursor():
    db = sqlite3.connect(f"file:{_DB_FILE}?mode=ro", uri=True)
    cursor = db.cursor()
    yield cursor
    db.close()


class Concept:
    def __init__(
        self,
        idc_id: str,
        icode: str = None,
        label: str = None,
        parent_idc_id: str = None,
    ):
        self.idc_id = idc_id
        self.icode = icode
        self.label = label
        self.parent_idc_id = parent_idc_id

    @property
    def children(self) -> List["Concept"]:
        items = []
        with _db_cursor() as cursor:
            for row in cursor.execute(
                "SELECT idc_id, icode, label, parent_idc_id from cim11 where parent_idc_id = ?",
                (self.idc_id,),
            ):
                items.append(Concept(row[0], row[1], row[2], row[3]))
        return items

    @property
    def parent(self) -> Union["Concept", None]:
        with _db_cursor() as cursor:
            for row in cursor.execute(
                "SELECT idc_id, icode, label, parent_idc_id from cim11 where idc_id = ?",
                (self.parent_idc_id,),
            ):
                return Concept(row[0], row[1], row[2], row[3])

    def __str__(self):
        if self.icode:
            return f"{self.icode} {self.label}"


def root_concepts() -> List[Concept]:
    items = []
    with _db_cursor() as cursor:
        for row in cursor.execute(
            "SELECT idc_id, icode, label, parent_idc_id from cim11 where parent_idc_id is null"
        ):
            if row[1] not in ["X", "V"]:
                items.append(Concept(row[0], row[1], row[2], row[3]))
        return items


def autocomplete_label(terms: str) -> List[Concept]:
    items = []
    with _db_cursor() as cursor:
        for row in cursor.execute(
            "SELECT idc_id, icode, label, parent_idc_id from cim11 where label like ? order by label",
            (f"%{terms.strip()}%",),
        ):
            if row[1] not in ["X", "V"]:
                items.append(Concept(row[0], row[1], row[2], row[3]))
    return items


def label_search(terms: str) -> List[Concept]:
    def fts_escape(user_input: str) -> str:
        wrds = []
        for wrd in user_input.split(" "):
            wrds.append('"' + wrd.replace('"', '""') + '"')
        return " ".join(wrds)

    dedup = []
    terms = fts_escape(terms)
    items = []
    with _db_cursor() as cursor:
        for row in cursor.execute(
            "SELECT idc_id, icode, label, parent_idc_id from cim11 where label match ? and icode is not null order by icode",
            (terms,),
        ):
            if row[1] not in ["X", "V"] and row[1] not in dedup:
                items.append(Concept(row[0], row[1], row[2], row[3]))
                dedup.append(row[1])
    return items


def icode_search(partial_code: str) -> List[Concept]:
    items = []
    dedup = []
    with _db_cursor() as cursor:
        for row in cursor.execute(
            "SELECT idc_id, icode, label, parent_idc_id from cim11 where icode like ? order by icode",
            (f"{partial_code}%",),
        ):
            if row[1] not in ["X", "V"] and row[1] not in dedup:
                items.append(Concept(row[0], row[1], row[2], row[3]))
                dedup.append(row[1])
    return items


def icode_details(complete_code: str) -> Union[Concept, None]:
    with _db_cursor() as cursor:
        for row in cursor.execute(
            "SELECT idc_id, icode, label, parent_idc_id from cim11 where icode = ?",
            (complete_code,),
        ):
            return Concept(row[0], row[1], row[2], row[3])
