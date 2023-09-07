#!/usr/bin/env python
import binascii
import dataclasses
import datetime
import hashlib
import logging
import os
import pathlib
import socket
import time
import uuid
import zipfile

from dacite import Config, from_dict

from kontor.defines import *


class BureauApplicant:
    __connection: socket.socket
    __working_directory = os.path.dirname(os.path.realpath(__file__))
    __temp_directory = os.path.join(__working_directory, "temp", "applicant")
    __communication_timeout_seconds: int = 30
    __file_transfer_timeout_seconds: int = 300

    def __init__(self):
        """
        Enable logging both to file and stdout.
        """
        log_directory = os.path.dirname(os.path.realpath(__file__))
        timestamp = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
        filename = timestamp + "_kontorist_client.log"
        filepath = os.path.join(log_directory, filename)

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s:%(levelname)s %(message)s",
            handlers=[logging.FileHandler(filepath), logging.StreamHandler()],
        )

        logging.info("Initializing the kontorist client.")

        """
        Create temp folder if it is not exist, including intermediate folders.
        """
        pathlib.Path(self.__temp_directory).mkdir(parents=True, exist_ok=True)

        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connection.settimeout(self.__communication_timeout_seconds)
        self.__connection.setblocking(True)

    def __del__(self):
        self.__disconnect()

    def __connect(self, server_ip_address: str, server_port: int):
        logging.info(f"Connecting to {server_ip_address}:{server_port}.")
        self.__connection.connect((server_ip_address, server_port))

    def __disconnect(self):
        logging.info(f"Closing the connection.")
        self.__connection.close()

    def __authenticate(self, username: str, password: str):
        logging.info(f"Authenticating {username} user.")

        password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
        auth_request = AuthRequestMessage(
            username=username, password_hash=password_hash
        )

        send_message(self.__connection, dataclasses.asdict(auth_request))
        response_json_data = wait_and_receive_response(self.__connection)
        auth_response = from_dict(
            data_class=AuthResponseMessage,
            data=response_json_data,
            config=Config(cast=[Enum]),
        )

        if auth_response.is_authenticated:
            logging.info(f"Authentication succeed.")
        else:
            logging.error(f"Authentication failed with error {auth_response.message}.")
            raise AuthenticationFailureException(
                f"Authentication failed with error {auth_response.message}."
            )

    def __send_file_for_processing(
        self, procedure: str, file_path: str, file_type: FileType
    ):
        file_name = os.path.basename(file_path)
        file_size_bytes = os.path.getsize(file_path)

        with open(file_path, "rb") as file:
            file_data = file.read()

        file_data_crc32 = binascii.crc32(file_data) & 0xFFFFFFFF
        file_data_crc32_str = "%08X" % file_data_crc32

        procedure_request = ProcedureRequestMessage(
            procedure=procedure,
            file_type=file_type,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
            file_crc32=file_data_crc32_str,
        )

        send_message(self.__connection, dataclasses.asdict(procedure_request))
        response_json_data = wait_and_receive_response(self.__connection)
        procedure_response = from_dict(
            data_class=ProcedureResponseMessage,
            data=response_json_data,
            config=Config(cast=[Enum]),
        )

        if procedure_response.is_ready_for_procedure:
            logging.info(f"Procedure was approved.")
        else:
            logging.error(
                f"Procedure was declined with error {procedure_response.message}."
            )
            raise ProcedureApprovalException(
                f"Procedure was declined with error {procedure_response.message}."
            )

        send_file(self.__connection, file_data)
        response_json_data = wait_and_receive_response(self.__connection)
        file_receiving_receipt = from_dict(
            data_class=FileReceivingReceiptMessage,
            data=response_json_data,
            config=Config(cast=[Enum]),
        )

        if file_receiving_receipt.is_received_correctly:
            logging.info(f"File was received correctly.")
        else:
            logging.error(f"File was received with error {procedure_response.message}.")
            raise FileTransmissionException(
                f"File was received with error {procedure_response.message}."
            )

    def __wait_and_receive_result_file(self, file_path: str, overwrite_file: bool):
        self.__connection.settimeout(self.__file_transfer_timeout_seconds)

        request_json_data = wait_and_receive_response(self.__connection)
        procedure_receipt = from_dict(
            data_class=ProcedureReceiptMessage,
            data=request_json_data,
            config=Config(cast=[Enum]),
        )

        if procedure_receipt.is_processed_correctly:
            logging.info(f"Procedure succeed, processed file is coming.")
        else:
            logging.error(f"Procedure failed with error {procedure_receipt.message}.")
            raise ProcedureExecutionException(
                f"Procedure failed with error {procedure_receipt.message}."
            )

        self.__connection.settimeout(self.__communication_timeout_seconds)

        corrected_file_path = os.path.join(self.__temp_directory, file_path)
        if not overwrite_file:
            extension = pathlib.Path(corrected_file_path).suffix
            corrected_file_path = corrected_file_path.replace(
                extension, "_processed" + extension
            )

        wait_and_receive_file(
            self.__connection, corrected_file_path, procedure_receipt.file_size_bytes
        )

        data_crc32: int = 0
        with open(corrected_file_path, "rb") as processed_file:
            data = processed_file.read()
            data_crc32 = binascii.crc32(data) & 0xFFFFFFFF
            data_crc32_str = "%08X" % data_crc32
            logging.info(f"Received file CRC32: {data_crc32_str}.")

        if data_crc32_str != procedure_receipt.file_crc32:
            logging.error(
                f"File is received incorrectly, received CRC32 {data_crc32} differs to provided CRC32 {procedure_receipt.file_crc32}."
            )
            raise ProcedureApprovalException(
                f"File is received incorrectly, received CRC32 {data_crc32} differs to provided CRC32 {procedure_receipt.file_crc32}."
            )

        file_size_bytes = os.path.getsize(corrected_file_path)
        if file_size_bytes != procedure_receipt.file_size_bytes:
            logging.error(
                f"File is received incorrectly, received size {file_size_bytes} differs to provided size {procedure_receipt.file_size_bytes}."
            )
            raise ProcedureApprovalException(
                f"File is received incorrectly, received size {file_size_bytes} differs to provided size {procedure_receipt.file_size_bytes}."
            )

        logging.info(f"Processed file was received successfully.")

    def process_files(
        self,
        server_ip_address: str,
        server_port: int,
        username: str,
        password: str,
        procedure: str,
        file_list: list,
        overwrite_file: bool = True,
    ):
        if len(file_list) == 0:
            raise EmptyFileListException("Provided file list is empty!")

        zip_file_name = os.path.join(self.__temp_directory, str(uuid.uuid4()) + ".zip")

        logging.info(
            f"Files list was provided, zipping files into archive: {zip_file_name}."
        )

        with zipfile.ZipFile(zip_file_name, "w") as zip_file:
            for file in file_list:
                zip_file.write(
                    file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED
                )

        self.__connect(server_ip_address, server_port)
        self.__authenticate(username, password)
        self.__send_file_for_processing(procedure, zip_file_name, FileType.ARCHIVE)
        self.__wait_and_receive_result_file(zip_file_name, overwrite_file)

        with zipfile.ZipFile(zip_file_name, "r") as zip_file:
            for name in zip_file.namelist():
                original_filepaths = [s for s in file_list if s.__contains__(name)]
                for original_filepath in original_filepaths:
                    logging.info(f"Unzipping file {name} to {original_filepath}.")

                    original_folder_path = pathlib.Path(
                        original_filepath
                    ).parent.absolute()

                    zip_file.extract(name, original_folder_path)

        if os.path.exists(zip_file_name):
            logging.info(f"Deleting zip archive {zip_file_name}.")
            os.remove(zip_file_name)

    def process_file(
        self,
        server_ip_address: str,
        server_port: int,
        username: str,
        password: str,
        procedure: str,
        file_path: str,
        overwrite_file: bool = True,
    ):
        self.__connect(server_ip_address, server_port)
        self.__authenticate(username, password)
        self.__send_file_for_processing(procedure, file_path, FileType.SINGLE)
        self.__wait_and_receive_result_file(file_path, overwrite_file)
