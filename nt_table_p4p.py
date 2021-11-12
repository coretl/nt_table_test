import asyncio
import time

from p4p.nt import NTEnum, NTTable
from p4p.nt.scalar import NTScalar
from p4p.server import Server
from p4p.server.asyncio import SharedPV
from p4p.wrapper import Value

# Some display types
common_display_fields = [("description", "s")]
enum_display_fields = common_display_fields + [("enumLabels", "as")]
form = ("S", "enum_t", [("index", "i"), ("choices", "as")])
float_display_fields = common_display_fields + [
    ("limitLow", "d"),
    ("limitHigh", "d"),
    ("units", "s"),
    ("precision", "i"),
    ("form", form),
]

# An original enum
enum_labels = ["ZERO", "ONE", "MANY"]
old_enum = SharedPV(nt=NTEnum(), initial=dict(index=1, choices=enum_labels))

# A new enum
enum_display = ("display", ("S", "display_t", enum_display_fields))
new_enum = SharedPV(
    nt=NTScalar("I", extra=[enum_display]),
    initial=dict(
        value=1,
        display=dict(
            description="A single enum",
            enumLabels=enum_labels,
        ),
    ),
)

# An original table
columns = [("enum", "aI"), ("checkBox", "a?"), ("string", "as"), ("float64", "ad")]
table_value = dict(
    labels=["Enum", "Check Box", "String", "Float 64"],
    value=dict(
        enum=[0, 1, 2],
        checkBox=[0, 1, 0],
        string=["a", "b", "c"],
        float64=[3.5, 2.5, 1.5],
    ),
)
old_table = SharedPV(initial=Value(NTTable.buildType(columns), table_value))

# A new table
column_display_fields = [
    ("enum", ("S", "display_t", enum_display_fields)),
    ("checkBox", ("S", "display_t", common_display_fields)),
    ("string", ("S", "display_t", common_display_fields)),
    ("float64", ("S", "display_t", float_display_fields)),
]
column_display = ("display", ("S", None, column_display_fields))
display_value = dict(
    enum=dict(description="An enum column", enumLabels=enum_labels),
    checkBox=dict(description="A checkBox column"),
    string=dict(description="A string column"),
    float64=dict(
        description="A float64 column",
        limitLow=0,
        limitHigh=10000.5,
        precision=1,
        units="m",
        form=dict(
            index=0,
            choices=[
                "Default",
                "String",
                "Binary",
                "Decimal",
                "Hex",
                "Exponential",
                "Engineering",
            ],
        ),
    ),
)
new_table = SharedPV(
    initial=Value(
        NTTable.buildType(columns, extra=[column_display]),
        dict(table_value, display=display_value),
    )
)


# Run up the server
async def run():
    with Server(
        providers=[
            {
                "P4P:OLD:ENUM": old_enum,
                "P4P:NEW:ENUM": new_enum,
                "P4P:OLD:TABLE": old_table,
                "P4P:NEW:TABLE": new_table,
            }
        ]
    ):
        while True:
            await asyncio.sleep(1)
            for e in old_enum, new_enum:
                e.post((e.current() + 1) % 3)
            for t in old_table, new_table:
                v = t.current()
                v.value.float64 = v.value.float64 + 1
                v.value.checkBox = v.value.checkBox == False
                v.timeStamp.secondsPastEpoch, ns = divmod(time.time(), 1.0)
                v.timeStamp.nanoseconds = ns * 1e9
                t.post(v)


asyncio.run(run())
