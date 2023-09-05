import logging
import sys
import os
from datetime import datetime

import asyncio
import qkd_simulator.backend as backend
import qkd_simulator.key_synchronization as key_synchronization
import qkd_simulator.configuration as configuration
import qkd_simulator.database as database
import qkd_simulator.key_management as key_management
import aioconsole

import time
from logging.handlers import QueueListener
from logging import FileHandler, StreamHandler
import queue
from logging.handlers import QueueHandler

CONFIG_FILE = os.path.join(os.getcwd(), "config.json")


def init():
    # https://stackoverflow.com/questions/45842926/python-asynchronous-logging

    global logger

    log_queue = queue.Queue()
    queue_handler = QueueHandler(log_queue)

    logger = logging.getLogger("qkd_simulator")

    logger.setLevel(logging.DEBUG)
    log_file_name = "quantum_twink_" + str(int(time.time())) + ".log"
    #file_handler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs", log_file_name)
    #file_handler = FileHandler(file_handler_path)
    stream_handler = StreamHandler()
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    #file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    queue_listener = QueueListener(log_queue, stream_handler)
    queue_listener.start()
    root = logging.getLogger()
    root.addHandler(queue_handler)

class MainLoop:

    def __init__(self):
        self.key_manager = None
        self.key_synchronizator = None
        self.backend = None
        self.database = None

    async def start(self, config):
        init()

        backend.init()
        database.init()
        key_management.init()
        key_synchronization.init()

        logger.info("Initializing database")
        self.database = database.Database(config)

        logger.info("Starting the backend")
        self.backend = backend.QBackend(config)
        self.backend.start()

        logger.info("Starting the key synchronizator")
        self.key_synchronizator = key_synchronization.KeySynchronizationSubsystem(
            config, self.database, self.backend)

        neighbour_node_names = [name for (name, _, _) in config.neighbours]
        waiter_for_nodes = list(filter(lambda x: x < config.node_name, neighbour_node_names))
        self.key_synchronizator.start(waiter_for_nodes)

        logger.info("Starting the application interface")
        self.key_manager = key_management.KeyManagementSubsystem(config, self.database, self.key_synchronizator)
        await self.key_manager.start()

    async def stop(self):
        logger.info("Stopping key manager")
        await self.key_manager.stop()

        logger.info("Stopping key synchronizator")
        self.key_synchronizator.stop()

        logger.info("Stopping quantum backend")
        self.backend.stop()

    def start_as_daemon(self, pidfile, config):
        print("Still not implemented")

    def stop_as_daemon(self, pidfile):
        print("Still not implemented")

    def restart_as_daemon(self, pidfile):
        print("Still not implemented")


def start(pidfile, config_file):
    # We load the configuration from this script rather than from the daemon.
    config = configuration.Config(config_file)
    main_loop = MainLoop()
    main_loop.start_as_daemon(pidfile, config)


def restart(pidfile):
    main_daemon = MainLoop()
    main_daemon.restart_as_daemon(pidfile)


def stop(pidfile):
    main_daemon = MainLoop()
    main_daemon.stop_as_daemon(pidfile)


async def non_daemon_start(config_file):
    print("Once the program has started, it will be stopped when enter is press")
    print("Press enter to start the program...")
    await aioconsole.ainput()
    config = configuration.Config(config_file)
    main_daemon = MainLoop()
    await main_daemon.start(config)
    await aioconsole.ainput(' ')
    await main_daemon.stop()


def print_cli_usage():
    print("Usage")
    exit(-1)


def cli():
    argc = len(sys.argv)
    if argc < 2:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(non_daemon_start(CONFIG_FILE))
        exit(0)
    pid_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qkd-twin.pid")
    action = sys.argv[1]
    if action == "start":
        if argc != 3:
            print_cli_usage()
        config_file = sys.argv[2]
        start(pid_file_path, config_file)
    elif action == "stop":
        stop(pid_file_path)
    elif action == "restart":
        restart(pid_file_path)
    else:
        print_cli_usage()


if __name__ == "__main__":
    cli()
