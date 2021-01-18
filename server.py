import json
import optparse

import gevent
import zmq

from core.errors import ApplicationError
from core.factory_command import Command


def tcp_server(ip, tcp_port):
    """Listen on a tcp ip:port to receive and process the data

    Args:
        ip  (str): ip
        tcp_port (int): port
    """
    ctx = zmq.Context()
    s = ctx.socket(zmq.REP)

    s.connect(f"tcp://{ip}:{tcp_port}")

    while True:
        try:
            print("Server is ready to receive data...")
            msg = s.recv_json()
            print("Message Received...")
            commands = [Command.factory(cmd) for cmd in msg] if type(msg) == list else [Command.factory(msg)]
            processes = [gevent.spawn(cmd.execute) for cmd in commands]
            gevent.joinall(processes)
            out = []
            for index, cmd in enumerate(commands):
                out.append(cmd.format_output(processes[index].value))
            s.send_json(json.dumps(out, indent=4))
            print("Result is sent to client...\n")
        except ApplicationError as err:
            s.send_json(f"Error '{err}' has occurred!!")
            print(f"Error '{err}' has occurred!!")
            print("Send another data...")

        except Exception as err:
            s.send_json(err)
            raise err


if __name__ == "__main__":

    parser = optparse.OptionParser()

    parser.add_option("--port", type="int", dest="port", default='9090', help="port number")
    parser.add_option("--ip", type="str", dest="ip", default='127.0.0.1', help="ip")
    # parser.add_option("--log-level", type="string", dest="log_level", default='info', help="logging level")
    (options, args) = parser.parse_args()
    port = 9090
    if options.port in range(1000, 9998):
        port = options.port

    tcp_server(options.ip, port)
