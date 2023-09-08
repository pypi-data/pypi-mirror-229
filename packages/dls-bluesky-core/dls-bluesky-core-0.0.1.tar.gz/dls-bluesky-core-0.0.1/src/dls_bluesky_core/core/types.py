from typing import Any, Callable, Generator

from bluesky import Msg

#  'A true "plan", usually the output of a generator function'
MsgGenerator = Generator[Msg, Any, None]
#  'A function that generates a plan'
PlanGenerator = Callable[..., MsgGenerator]
