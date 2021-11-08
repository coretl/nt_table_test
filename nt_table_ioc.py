# Import the basic framework components.
import logging
from epicsdbbuilder import PP
from epicsdbbuilder.recordset import WriteRecords
from softioc import softioc, builder, asyncio_dispatcher
from softioc.builder import records
import asyncio
import numpy as np

# Create an asyncio dispatcher, the event loop is now running
dispatcher = asyncio_dispatcher.AsyncioDispatcher()

# Set the record prefix
builder.SetDeviceName("NT-TABLE-IOC:TABLE")

# Create some table records
columns = builder.WaveformOut("LABELS", initial_value=["enabled", "trigger", "repeats"])
columns.add_info("Q:group", {
    "NT-TABLE-IOC:TABLE":{
        "+id": "epics:nt/NTTable:1.0",
        "labels":{"+type": "plain", "+channel": "VAL"}
    }
})
enabled = builder.WaveformOut("ENABLED", initial_value=np.zeros(10, dtype=np.bool_), always_update=True)
enabled.add_info("Q:group", {
    "NT-TABLE-IOC:TABLE":{
        "value.c1":{"+type": "plain", "+channel": "VAL", "+putorder": 2}
    }
})
trigger = builder.WaveformOut("TRIGGER", initial_value=np.arange(10, dtype=np.int8) % 3, always_update=True)
trigger.add_info("Q:group", {
    "NT-TABLE-IOC:TABLE":{
        "value.c2":{"+type": "plain", "+channel": "VAL", "+putorder": 2}
    }
})
repeats = builder.WaveformOut("REPEATS", initial_value=np.arange(10, dtype=np.int16), always_update=True)
repeats.add_info("Q:group", {
    "NT-TABLE-IOC:TABLE":{
        "value.c3":{"+type": "plain", "+channel": "VAL", "+putorder": 2}
    }
})

should_update = True

def switch_editable(e):
    if not e:
        # Push values to PandA
        print({r: globals()[r].get() for r in columns.get()})
    global should_update
    should_update = not e


editable = builder.mbbOut("EDITABLE", "No", "Yes", initial_value=0, on_update=switch_editable)
editable_start = records.ao("EDITABLE:START", VAL=1, OUT=PP(editable))
editable_start.add_info("Q:group", {
    "NT-TABLE-IOC:TABLE":{
        "_start":{"+type":"proc",
                "+channel":"PROC",
                "+putorder":1,
                "+trigger":"*"}
    }
})
editable_end = records.ao("EDITABLE:END", VAL=0, OUT=PP(editable))
editable_end.add_info("Q:group", {
    "NT-TABLE-IOC:TABLE":{
        "_end":{"+type":"proc",
                "+channel":"PROC",
                "+putorder":3,
                "+trigger":"*"}
    }
})

# Boilerplate get the IOC started
WriteRecords("/dev/stdout", header="######################\n")
print("######################")
builder.LoadDatabase()
softioc.iocInit(dispatcher)

# Start processes required to be run after iocInit
async def update():
    try:
        while True:
            if should_update:
                r = repeats.get()
                r[0] += 1
                repeats.set(r)
            await asyncio.sleep(1)
    except:
        logging.exception("bad")

asyncio.run_coroutine_threadsafe(update(), dispatcher.loop)

# Finally leave the IOC running with an interactive shell.
softioc.interactive_ioc(globals())
