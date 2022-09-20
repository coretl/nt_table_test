import asyncio
import logging

from epicsdbbuilder.recordbase import PP
from epicsdbbuilder.recordset import WriteRecords
from softioc import asyncio_dispatcher, builder, softioc
from softioc.builder import records

# Create an asyncio dispatcher, the event loop is now running
dispatcher = asyncio_dispatcher.AsyncioDispatcher()

# An original enum
builder.SetDeviceName("QSRV:OLD")
old_enum = builder.mbbOut(
    "ENUM", "ZERO", "ONE", "MANY", DESC="Old Enum", initial_value=1
)

# A new enum
builder.SetDeviceName("QSRV:NEW")
new_enum = builder.longOut("ENUM:INDEX", DESC="New Enum", initial_value=1)
new_enum.add_info(
    "Q:group",
    {
        "QSRV:NEW:ENUM": {
            "+id": "epics:nt/NTScalar:1.0",
            "value": {"+type": "plain", "+channel": "VAL"},
            "display.description": {"+type": "plain", "+channel": "DESC"},
            "": {"+type": "meta", "+channel": "VAL"},
        }
    },
)
new_labels = builder.WaveformOut(
    "ENUM:LABELS", initial_value=[b"ZERO", b"ONE", b"MANY"]
)
new_labels.add_info(
    "Q:group",
    {
        "QSRV:NEW:ENUM": {
            "display.enumLabels": {"+type": "plain", "+channel": "VAL"},
        }
    },
)

# An original table
builder.SetDeviceName("QSRV:TABLE")
columns = builder.WaveformOut(
    "LABELS", initial_value=[b"Enum", b"Check Box", b"String", b"Float 64"]
)
columns.add_info(
    "Q:group",
    {
        "QSRV:TABLE": {
            "+id": "epics:nt/NTTable:1.0",
            "labels": {"+type": "plain", "+channel": "VAL"},
        }
    },
)
enum_col = builder.WaveformOut("ENUM", initial_value=[b"ZERO", b"ONE", b"MANY"], always_update=True)
enum_col.add_info(
    "Q:group",
    {"QSRV:TABLE": {"value.c1": {"+type": "plain", "+channel": "VAL", "+putorder": 2}}},
)
check_box = builder.WaveformOut("CHECKBOX", initial_value=[0, 1, 0], always_update=True)
check_box.add_info(
    "Q:group",
    {"QSRV:TABLE": {"value.c2": {"+type": "plain", "+channel": "VAL", "+putorder": 2}}},
)
string = builder.WaveformOut(
    "STRING", initial_value=[b"a", b"b", b"c"], always_update=True
)
string.add_info(
    "Q:group",
    {"QSRV:TABLE": {"value.c3": {"+type": "plain", "+channel": "VAL", "+putorder": 2}}},
)
float_64 = builder.WaveformOut(
    "FLOAT64", initial_value=[3.5, 2.5, 1.5], always_update=True
)
# Last column update triggers monitor
float_64.add_info(
    "Q:group",
    {
        "QSRV:TABLE": {
            "value.c4": {
                "+type": "plain",
                "+channel": "VAL",
                "+putorder": 2,
                "+trigger": "*",
            },
            "": {"+type": "meta", "+channel": "VAL"},
        }
    },
)

should_update = True


def switch_editable(e):
    global should_update
    should_update = e == 0
    if not e:
        # Push values to hardware
        print("Set", enum_col.get(), check_box.get(), string.get(), float_64.get())


editable = builder.mbbOut(
    "EDITABLE", "No", "Yes", initial_value=0, on_update=switch_editable
)
editable_start = records.ao("EDITABLE:START", VAL=1, MDEL=-1, OUT=PP(editable))
editable_start.add_info(
    "Q:group",
    {
        "QSRV:TABLE": {
            "_start": {
                "+type": "proc",
                "+channel": "PROC",
                "+putorder": 1,
                "+trigger": "",
            }
        }
    },
)
editable_end = records.ao("EDITABLE:END", VAL=0, MDEL=-1, OUT=PP(editable))
editable_end.add_info(
    "Q:group",
    {
        "QSRV:TABLE": {
            "_end": {
                "+type": "proc",
                "+channel": "PROC",
                "+putorder": 3,
                "+trigger": "*",
            }
        }
    },
)

# Boilerplate get the IOC started
WriteRecords("/dev/stdout", header="######################\n")
print("######################")
builder.LoadDatabase()
softioc.iocInit(dispatcher)


# Start processes required to be run after iocInit
async def update():
    try:
        while True:
            await asyncio.sleep(1)
            old_enum.set((old_enum.get() + 1) % 3)
            if should_update:
                check_box.set((check_box.get() + 1) % 2)
                float_64.set(float_64.get() + 1)
                enum_col.set([(b"ZERO", b"ONE", b"MANY")[(old_enum.get() + i) % 3] for i in range(3)])
    except Exception:
        logging.exception("bad")


dispatcher(update)

# Finally leave the IOC running with an interactive shell.
softioc.interactive_ioc(globals())
