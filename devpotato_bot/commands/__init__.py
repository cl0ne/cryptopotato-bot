from . import fortune
from . import help
from . import me
from . import ping
from . import produce_error, get_chat_id
from . import roll

handler_getters = [
    m.get_handler for m in
    (fortune, get_chat_id, help, me, ping, produce_error, roll)
]
