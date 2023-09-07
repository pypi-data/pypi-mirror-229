#!/usr/bin/env python
import binascii
import dataclasses
import datetime
import glob
import hashlib
import json
import logging
import os
import pathlib
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import zipfile
from dataclasses import dataclass, field
from logging.handlers import TimedRotatingFileHandler

import pkg_resources
from dacite import Config, from_dict

from kontor.defines import *


@dataclass
class ApplicantDossier:
    username: str = ""
    password_hash: str = ""
    allowed_procedures: list = field(default_factory=list)


@dataclass
class BureauConfiguration:
    ip_address: str = "localhost"
    port: int = 5690
    chunk_size_kilobytes: int = 256
    client_idle_timeout_seconds: int = 30
    max_storage_period_hours: int = 0
    max_parallel_connections: int = 100
    max_consequent_client_procedures: int = 1
    max_grace_shutdown_timeout_seconds: int = 30
    procedures: dict = field(default_factory=dict)


class Bureau:
    def __init__(self, working_folder_path: str):
        self.__server: socket.socket
        self.__configuration: BureauConfiguration = BureauConfiguration()
        self.__is_server_started = False
        self.__is_server_shutting_down = False
        self.__server_threads = list()
        self.__client_threads = list()

        self.__working_directory = working_folder_path
        pathlib.Path(self.__working_directory).mkdir(parents=True, exist_ok=True)

        self.__temp_directory = os.path.join(self.__working_directory, "temp")
        pathlib.Path(self.__temp_directory).mkdir(parents=True, exist_ok=True)

        """
        Enable logging both to file and stdout.
        """
        log_directory = os.path.join(self.__working_directory, "logs")
        pathlib.Path(log_directory).mkdir(parents=True, exist_ok=True)

        filename = "bureau.log"
        filepath = os.path.join(log_directory, filename)

        handler = TimedRotatingFileHandler(filepath, when="midnight", backupCount=60)
        handler.suffix = "%Y%m%d"

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s:%(levelname)s %(message)s",
            handlers=[handler, logging.StreamHandler()],
        )

        kontor_version = pkg_resources.get_distribution("kontor").version
        logging.info(f"Initializing the bureau of version {kontor_version}.")

        self.__parse_configuration_json_file()

    def __parse_configuration_json_file(self, configuration_filepath=None):
        """
        Try to locate configuration file in the working directory.
        """
        if configuration_filepath is None:
            configuration_filepath = os.path.join(
                self.__working_directory, "server_configuration.json"
            )

        """
        Use default settings if no file was found. Create file with default settings.
        """
        if not os.path.exists(configuration_filepath):
            self.__save_configuration_to_json_file()
            return

        """
        Read configuration JSON.
        """
        with open(configuration_filepath, "r") as json_file:
            configuration_json = json.load(json_file)

        """
        Parse configuration JSON.
        """
        if "ip_address" not in configuration_json:
            raise ValueError("No IP address was provided in configuration JSON!")

        self.__configuration = BureauConfiguration()
        self.__configuration.ip_address = configuration_json["ip_address"]

        if "port" not in configuration_json:
            raise ValueError("No port was provided in configuration JSON!")

        self.__configuration.port = configuration_json["port"]

        if "chunk_size_kilobytes" not in configuration_json:
            raise ValueError(
                "No transfer chunk size was provided in configuration JSON!"
            )

        self.__configuration.chunk_size_kilobytes = configuration_json[
            "chunk_size_kilobytes"
        ]

        if "client_idle_timeout_seconds" not in configuration_json:
            raise ValueError(
                "No client idle timeout was provided in configuration JSON!"
            )

        self.__configuration.client_idle_timeout_seconds = configuration_json[
            "client_idle_timeout_seconds"
        ]

        if "max_storage_period_hours" not in configuration_json:
            raise ValueError(
                "No max limit for storing temporary files was provided in configuration JSON!"
            )

        self.__configuration.max_storage_period_hours = configuration_json[
            "max_storage_period_hours"
        ]

        if "max_parallel_connections" not in configuration_json:
            raise ValueError(
                "No max limit for parallel connections was provided in configuration JSON!"
            )

        self.__configuration.max_parallel_connections = configuration_json[
            "max_parallel_connections"
        ]

        if "max_consequent_client_procedures" not in configuration_json:
            raise ValueError(
                "No max limit for consequent client procedures was provided in configuration JSON!"
            )

        self.__configuration.max_consequent_client_procedures = configuration_json[
            "max_consequent_client_procedures"
        ]

        if "max_grace_shutdown_timeout_seconds" not in configuration_json:
            raise ValueError(
                "No max grace shutdown timeout was provided in configuration JSON!"
            )

        self.__configuration.max_grace_shutdown_timeout_seconds = configuration_json[
            "max_grace_shutdown_timeout_seconds"
        ]

        self.__configuration.procedures = configuration_json["procedures"]

    def __save_configuration_to_json_file(self, configuration_filepath=None):
        if configuration_filepath is None:
            configuration_filepath = os.path.join(
                self.__working_directory, "server_configuration.json"
            )

        with open(configuration_filepath, "w", encoding="utf-8") as file:
            json.dump(
                dataclasses.asdict(self.__configuration),
                file,
                ensure_ascii=False,
                indent=4,
            )

    def __is_user_auth_correct(self, username: str, password_hash: str) -> bool:
        """
        Reading and parsing file every time function is called for loading file changes.
        Should be fine with small user databases.
        """
        user_db_filepath = os.path.join(self.__working_directory, "server_users.json")
        with open(user_db_filepath) as json_file:
            user_db_json = json.load(json_file)

        for user in user_db_json:
            if username == user["username"]:
                if password_hash == user["password_hash"]:
                    return True

        return False

    def __is_procedure_allowed_for_user(self, username: str, procedure: str) -> bool:
        """
        Reading and parsing file every time function is called for loading file changes.
        Should be fine with small user databases.
        """
        user_db_filepath = os.path.join(self.__working_directory, "server_users.json")
        with open(user_db_filepath) as json_file:
            user_db_json = json.load(json_file)

        for user in user_db_json:
            if username == user["username"]:
                if procedure in user["allowed_procedures"]:
                    return True

        return False

    def __serve_client(self, client: socket.socket, address):
        logging.info(f"{address}: Starting new thread for connection.")

        try:
            username = ""
            procedure = ""
            user_temp_folder_path = ""
            is_authenticated = False

            client.settimeout(self.__configuration.client_idle_timeout_seconds)

            current_retry = 0
            max_connection_retries = 5
            try:
                for current_retry in range(max_connection_retries):
                    clerk_ready = ClerkReadyMessage(
                        applicant_ip=address[0], applicant_port=address[1]
                    )
                    send_message(client, address, dataclasses.asdict(clerk_ready))

                    message_json = wait_and_receive_response(client, address)
                    applicant_ready = from_dict(
                        data_class=ApplicantReadyMessage,
                        data=message_json,
                        config=Config(cast=[Enum]),
                    )
                    break

            except socket.timeout:
                if current_retry == max_connection_retries - 1:
                    raise

                time.sleep(5)

            is_connection_alive = True
            while not self.__is_server_shutting_down and is_connection_alive:
                message_json = wait_and_receive_response(client, address)

                if "type" not in message_json:
                    logging.error(
                        f"{address}: No 'type' stated in the incoming message, terminating connection."
                    )
                    raise InvalidMessageFormatException(
                        f"{address}: No 'type' stated in the incoming message, terminating connection."
                    )

                if message_json["type"] == TransmissionType.AUTH_REQUEST:
                    if is_authenticated:
                        auth_response = AuthResponseMessage(
                            is_authenticated=False, message="Unexpected message type."
                        )
                        send_message(client, address, dataclasses.asdict(auth_response))
                        logging.error(
                            f"{address}: User is trying to re-authenticate while already being authenticated, terminating connection."
                        )
                        raise UnexpectedMessageException(
                            f"{address}: User is trying to re-authenticate while already being authenticated, terminating connection."
                        )

                    auth_request = AuthRequestMessage()
                    try:
                        auth_request = from_dict(
                            data_class=AuthRequestMessage,
                            data=message_json,
                            config=Config(cast=[Enum]),
                        )
                    except:
                        auth_response = AuthResponseMessage(
                            is_authenticated=False, message="Incorrect message format."
                        )
                        send_message(client, address, dataclasses.asdict(auth_response))
                        logging.error(
                            f"{address}: No username or password stated in the incoming authentication request, terminating connection."
                        )
                        raise InvalidMessageFormatException(
                            f"{address}: No username or password stated in the incoming authentication request, terminating connection."
                        )

                    if not self.__is_user_auth_correct(
                        auth_request.username, auth_request.password_hash
                    ):
                        auth_response = AuthResponseMessage(
                            is_authenticated=False,
                            message="Incorrect username or password.",
                        )
                        send_message(client, address, dataclasses.asdict(auth_response))
                        logging.error(
                            f"{address}: Username or password is incorrect, terminating connection."
                        )
                        raise AuthenticationFailureException(
                            f"{address}: Username or password is incorrect, terminating connection."
                        )

                    is_authenticated = True

                    auth_response = AuthResponseMessage(
                        is_authenticated=True, message="Authentication successful."
                    )
                    send_message(client, address, dataclasses.asdict(auth_response))

                    timestamp = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
                    username = auth_request.username
                    user_temp_folder_path = os.path.join(
                        self.__temp_directory,
                        timestamp + "_" + username + f"_{address[1]}",
                    )
                    pathlib.Path(user_temp_folder_path).mkdir(
                        parents=True, exist_ok=True
                    )
                    logging.debug(
                        f"{address}: Created temporary folder {user_temp_folder_path}."
                    )

                if message_json["type"] == TransmissionType.PROCEDURE_REQUEST:
                    if not is_authenticated:
                        procedure_response = ProcedureResponseMessage(
                            is_ready_for_procedure=False,
                            message="User is not authenticated.",
                        )
                        send_message(
                            client, address, dataclasses.asdict(procedure_response)
                        )
                        logging.error(
                            f"{address}: User is not authenticated, terminating connection."
                        )
                        raise UnexpectedMessageException(
                            f"{address}: User is not authenticated, terminating connection."
                        )

                    procedure_request = ProcedureRequestMessage()
                    try:
                        procedure_request = from_dict(
                            data_class=ProcedureRequestMessage,
                            data=message_json,
                            config=Config(cast=[Enum]),
                        )
                    except:
                        procedure_response = ProcedureResponseMessage(
                            is_ready_for_procedure=False,
                            message="Incorrect message format.",
                        )
                        send_message(
                            client, address, dataclasses.asdict(procedure_response)
                        )
                        logging.error(
                            f"{address}: No file size, CRC32, name or procedure stated in the incoming authentication request, terminating connection."
                        )
                        raise InvalidMessageFormatException(
                            f"{address}: No file size, CRC32, name or procedure stated in the incoming authentication request, terminating connection."
                        )

                    if not self.__is_procedure_allowed_for_user(
                        username, procedure_request.procedure
                    ):
                        procedure_response = ProcedureResponseMessage(
                            is_ready_for_procedure=False,
                            message="User is not allowed to use selected procedure.",
                        )
                        send_message(
                            client, address, dataclasses.asdict(procedure_response)
                        )
                        logging.error(
                            f"{address}: User is not allowed to use selected procedure, terminating connection."
                        )
                        raise ProcedureApprovalException(
                            f"{address}: User is not allowed to use selected procedure, terminating connection."
                        )

                    procedure_response = ProcedureResponseMessage(
                        is_ready_for_procedure=True,
                        message="Procedure approved, ready to receive files.",
                    )
                    send_message(
                        client, address, dataclasses.asdict(procedure_response)
                    )

                    procedure = procedure_request.procedure

                    file_size_bytes = procedure_request.file_size_bytes
                    received_file_path = os.path.join(
                        user_temp_folder_path, procedure_request.file_name
                    )

                    wait_and_receive_file(
                        client,
                        address,
                        received_file_path,
                        procedure_request.file_size_bytes,
                    )

                    data_crc32: int = 0
                    with open(received_file_path, "rb") as processed_file:
                        data = processed_file.read()
                        data_crc32 = binascii.crc32(data) & 0xFFFFFFFF
                        data_crc32_str = "%08X" % data_crc32
                        logging.info(
                            f"{address}: Received file CRC32: {data_crc32_str}."
                        )

                    if data_crc32_str != procedure_request.file_crc32:
                        procedure_receipt = FileReceivingReceiptMessage(
                            is_received_correctly=False,
                            message=f"File is received incorrectly, received CRC32 {data_crc32} differs to provided CRC32 {procedure_request.file_crc32}.",
                        )
                        send_message(
                            client, address, dataclasses.asdict(procedure_receipt)
                        )
                        logging.error(
                            f"{address}: File is received incorrectly, received CRC32 {data_crc32} differs to provided CRC32 {procedure_request.file_crc32}."
                        )
                        raise ProcedureApprovalException(
                            f"{address}: File is received incorrectly, received CRC32 {data_crc32} differs to provided CRC32 {procedure_request.file_crc32}."
                        )

                    file_size_bytes = os.path.getsize(received_file_path)
                    if file_size_bytes != procedure_request.file_size_bytes:
                        procedure_receipt = FileReceivingReceiptMessage(
                            is_received_correctly=False,
                            message=f"File is received incorrectly, received size {file_size_bytes} differs to provided size {procedure_request.file_size_bytes}.",
                        )
                        send_message(
                            client, address, dataclasses.asdict(procedure_receipt)
                        )
                        logging.error(
                            f"{address}: File is received incorrectly, received size {file_size_bytes} differs to provided size {procedure_request.file_size_bytes}."
                        )
                        raise ProcedureApprovalException(
                            f"{address}: File is received incorrectly, received size {file_size_bytes} differs to provided size {procedure_request.file_size_bytes}."
                        )

                    procedure_receipt = FileReceivingReceiptMessage(
                        is_received_correctly=True,
                        message="File is received correctly and being processed.",
                    )
                    send_message(client, address, dataclasses.asdict(procedure_receipt))

                    file_paths = []
                    if procedure_request.file_type == FileType.SINGLE:
                        file_paths.append(received_file_path)
                    elif procedure_request.file_type == FileType.ARCHIVE:
                        with zipfile.ZipFile(received_file_path, "r") as zip_file:
                            zip_file.extractall(user_temp_folder_path)
                        os.remove(received_file_path)
                        file_paths = glob.glob(f"{user_temp_folder_path}/*")

                    for file_path in file_paths:
                        command = self.__configuration.procedures[procedure]

                        if "<FILE_NAME>" in command:
                            command = command.replace("<FILE_NAME>", file_path)

                        if "<FILE_COPY>" in command:
                            file_copy_path = file_path
                            extension = pathlib.Path(file_copy_path).suffix
                            file_copy_path = file_copy_path.replace(
                                extension, "_copy" + extension
                            )
                            command = command.replace("<FILE_COPY>", file_copy_path)
                            shutil.copy(file_path, file_copy_path)

                        logging.info(
                            f"{address}: Executing procedure command: '{command}'."
                        )

                        result = subprocess.run(
                            command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell=True,
                            text=True,
                            universal_newlines=True,
                        )
                        if result.returncode != 0:
                            procedure_receipt = ProcedureReceiptMessage(
                                is_processed_correctly=False,
                                message=f"Procedure failed with return code {result.returncode} and error message {result.stdout}.",
                            )
                            send_message(
                                client, address, dataclasses.asdict(procedure_receipt)
                            )
                            logging.error(
                                f"{address}: Procedure failed with return code {result.returncode} and error message {result.stdout}."
                            )
                            raise ProcedureExecutionException(
                                f"{address}: Procedure failed with return code {result.returncode} and error message {result.stdout}."
                            )

                    if procedure_request.file_type == FileType.ARCHIVE:
                        with zipfile.ZipFile(received_file_path, "w") as zip_file:
                            for file in file_paths:
                                zip_file.write(
                                    file,
                                    os.path.basename(file),
                                    compress_type=zipfile.ZIP_DEFLATED,
                                )

                    processed_file_size_bytes = os.path.getsize(received_file_path)
                    processed_data_crc32: int = 0
                    with open(received_file_path, "rb") as processed_file:
                        processed_data = processed_file.read()
                        processed_data_crc32 = (
                            binascii.crc32(processed_data) & 0xFFFFFFFF
                        )
                        processed_data_crc32_str = "%08X" % processed_data_crc32
                        logging.info(
                            f"{address}: Processed file CRC32: {processed_data_crc32_str}."
                        )

                    procedure_receipt = ProcedureReceiptMessage(
                        is_processed_correctly=True,
                        message="File was successfully processed.",
                        file_crc32=processed_data_crc32_str,
                        file_size_bytes=processed_file_size_bytes,
                    )
                    send_message(client, address, dataclasses.asdict(procedure_receipt))

                    send_file(client, address, processed_data)

                    if self.__configuration.max_storage_period_hours == 0:
                        shutil.rmtree(user_temp_folder_path)
                        logging.debug(
                            f"{address}: Removed temporary folder {user_temp_folder_path}."
                        )

        except ConnectionBrokenException as e:
            logging.info(f"{address}: Client disconnected.")

        except Exception as e:
            logging.exception(f"{address}: " + str(e))

        finally:
            client.shutdown(socket.SHUT_RDWR)
            client.close()

            """
            Automatically remove itself from list of client threads.
            """
            self.__client_threads.remove(threading.current_thread())
            logging.info(f"{address}: Thread for connection from {address} was closed.")

    def add_user(self, username: str, password: str, allowed_procedures: list):
        if not os.path.exists(self.__working_directory):
            raise MissingWorkingDirectoryException(
                "Working directory is not set, aborting start."
            )

        if not os.path.exists(self.__temp_directory):
            raise MissingWorkingDirectoryException(
                "Temporary directory is not set, aborting start."
            )

        new_user = ApplicantDossier()
        new_user.username = username
        new_user.password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
        new_user.allowed_procedures = allowed_procedures

        user_db_json = []
        user_db_filepath = os.path.join(self.__working_directory, "server_users.json")
        if os.path.exists(user_db_filepath):
            with open(user_db_filepath, "r") as json_file:
                user_db_json = json.load(json_file)

        user_db_json.append(dataclasses.asdict(new_user))

        with open(user_db_filepath, "w", encoding="utf-8") as file:
            json.dump(
                user_db_json,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def add_procedure(self, name: str, command: str, overwrite: bool = False):
        if not os.path.exists(self.__working_directory):
            raise MissingWorkingDirectoryException(
                "Working directory is not set, aborting start."
            )

        if not os.path.exists(self.__temp_directory):
            raise MissingWorkingDirectoryException(
                "Temporary directory is not set, aborting start."
            )

        if not overwrite and name in self.__configuration.procedures:
            raise ProcedureAlreadyPresentException(
                f"Procedure {name} is already present in configuration."
            )

        self.__configuration.procedures[name] = command
        self.__save_configuration_to_json_file()

    def start_async(self):
        async_thread = threading.Thread(target=self.start, daemon=True)
        async_thread.start()
        self.__server_threads.append(async_thread)

        max_seconds_to_wait = 30
        timeout = time.time() + max_seconds_to_wait
        while not self.__is_server_started:
            time.sleep(1)

            if time.time() >= timeout:
                raise ServerStartTimeoutException(
                    f"Failed to start server in {max_seconds_to_wait} seconds!"
                )

    def start(self):
        if not os.path.exists(self.__working_directory):
            raise MissingWorkingDirectoryException(
                "Working directory is not set, aborting start."
            )

        if not os.path.exists(self.__temp_directory):
            raise MissingWorkingDirectoryException(
                "Temporary directory is not set, aborting start."
            )

        logging.info(
            f"Opening server connection at {self.__configuration.ip_address}:{self.__configuration.port}."
        )

        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((self.__configuration.ip_address, self.__configuration.port))
        self.__server.listen(self.__configuration.max_parallel_connections)
        self.__server.settimeout(0.5)

        logging.info("Starting to listen for incoming connections.")

        self.__is_server_started = True
        while not self.__is_server_shutting_down:
            try:
                client, address = self.__server.accept()

                logging.info(f"New incoming connection from {address}.")

                thread = threading.Thread(
                    target=self.__serve_client,
                    args=(
                        client,
                        address,
                    ),
                )
                thread.start()
                self.__client_threads.append(thread)
            except Exception as e:
                logging.info(f"Waiting for new connections. Exception {str(e)}.")
                time.sleep(1)

    def shutdown(self):
        logging.info("Shutting down the kontorist server.")

        self.__is_server_shutting_down = True

        grace_shutdown_start_time = time.process_time()
        while (
            len(self.__client_threads) > 0
            and (time.process_time() - grace_shutdown_start_time)
            >= self.__configuration.max_grace_shutdown_timeout_seconds
        ):
            logging.info(
                f"Waiting for {len(self.__client_threads)} thread to complete their jobs (max wait {self.__configuration.max_grace_shutdown_timeout_seconds} seconds)."
            )
            time.sleep(5)

        """
        Somewhat weird way of stopping endlessly waiting socket.accept.
        """
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
            (self.__configuration.ip_address, self.__configuration.port)
        )
        self.__server.close()

        if len(self.__server_threads) > 0:
            logging.info(
                "Server is running in async mode, waiting for thread to finish."
            )
            for async_thread in self.__server_threads:
                async_thread.join()

        logging.info("Shutdown complete.")


def shutdown_signal_handler(sig, frame):
    logging.critical("Caught SIGINT signal, properly shutting down the server.")
    sys.exit(0)


if __name__ == "__main__":
    """
    Catch Ctrl+C signal for proper shutdown of the server.
    """
    signal.signal(signal.SIGINT, shutdown_signal_handler)

    bureau = Bureau(os.path.dirname(os.path.realpath(__file__)))
    bureau.start()
