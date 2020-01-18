from . import fortune
from . import help
from . import me
from . import ping
from . import produce_error
from . import roll

handler_getters = [
    m.get_handler for m in
    (fortune, help, me, ping, produce_error, roll)
]
