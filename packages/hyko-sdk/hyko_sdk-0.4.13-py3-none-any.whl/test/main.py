from hyko_sdk import SDKFunction, CoreModel

func = SDKFunction(
    description="a test function",
    requires_gpu=False,
)

class Inputs(CoreModel):
    pass

class Params(CoreModel):
    pass

class Outputs(CoreModel):
    pass

@func.on_startup
async def start():
    import time
    print("started blocking sleep 1")
    time.sleep(5)
    print("blocking sleep finished 1")

@func.on_startup
async def start2():
    import time
    print("started blocking sleep 2")
    time.sleep(7)
    print("blocking sleep finished 2")

@func.on_execute
async def exec(inputs: Inputs, params: Params) -> Outputs:
    return Outputs()

