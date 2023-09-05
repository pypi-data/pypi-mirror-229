from multiprocessing import Queue
from utils.errno import Error, OK


def init_base(conf_path: str, log: Queue = None, qs=None) -> Error:
    from utils.log import logger
    from utils.config import init_conf
    err = init_conf(conf_path)
    if not err.ok:
        logger.error(f"{conf_path} init {err}")
        return err

    from utils.log.q import QLogM
    if log:
        QLogM.init_q(log)
    from utils.log.log import init
    from utils.config import log_conf
    init(log_conf())

    from .q import QM
    if qs:
        QM.init(qs)
    return OK
