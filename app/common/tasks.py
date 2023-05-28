from rocketry import Rocketry
from rocketry.conds import minutely

rocketry = Rocketry(execution='thread')


# @rocketry.task(minutely)
async def task_test() -> None:
    print('test task')
