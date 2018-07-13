import logging
import psutil
import socket
import time

FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='reducer_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/reducerlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('reducer')

# periodic sytem info message
psi_msg = "cpu%:{} cpuCnt:{} mem%:{}"

while True:
    time.sleep(5)
    cp = psutil.cpu_percent()
    cc = psutil.cpu_count()
    vm = psutil.virtual_memory().percent
    logger.info(psi_msg.format(cp, cc, vm))
