#!/usr/bin/env python
import json
import logging
import socket
from dataclasses import dataclass
from enum import Enum

MARKER_TRANSMISSION_START: str = "<TRANSMISSION_START>"
MARKER_TRANSMISSION_END: str = "<TRANSMISSION_END>"
MARKER_FILE_START: bytes = b"<FILE_START>"
MARKER_FILE_END: bytes = b"<FILE_END>"


class TransmissionType(str, Enum):
    UNKNOWN = "UNKNOWN"
    AUTH_REQUEST = "AUTH_REQUEST"
    AUTH_RESPONSE = "AUTH_RESPONSE"
    PROCEDURE_REQUEST = "PROCEDURE_REQUEST"
    PROCEDURE_RESPONSE = "PROCEDURE_RESPONSE"
    FILE_RECEIVING_RECEIPT = "FILE_RECEIVING_RECEIPT"
    PROCEDURE_RECEIPT = "PROCEDURE_RECEIPT"


class FileType(str, Enum):
    NONE = "NONE"
    SINGLE = "SINGLE"
    ARCHIVE = "ARCHIVE"


@dataclass
class AuthRequestMessage:
    type: TransmissionType = TransmissionType.AUTH_REQUEST
    username: str = ""
    password_hash: str = ""


@dataclass
class AuthResponseMessage:
    type: TransmissionType = TransmissionType.AUTH_RESPONSE
    is_authenticated: bool = False
    message: str = ""


@dataclass
class ProcedureRequestMessage:
    type: TransmissionType = TransmissionType.PROCEDURE_REQUEST
    procedure: str = ""
    file_type: FileType = FileType.NONE
    file_name: str = ""
    file_size_bytes: int = 0
    file_crc32: str = ""


@dataclass
class ProcedureResponseMessage:
    type: TransmissionType = TransmissionType.PROCEDURE_RESPONSE
    is_ready_for_procedure: bool = False
    message: str = ""


@dataclass
class FileReceivingReceiptMessage:
    type: TransmissionType = TransmissionType.FILE_RECEIVING_RECEIPT
    is_received_correctly: bool = False
    message: str = ""


@dataclass
class ProcedureReceiptMessage:
    type: TransmissionType = TransmissionType.PROCEDURE_RECEIPT
    is_processed_correctly: bool = False
    message: str = ""
    file_size_bytes: int = 0
    file_crc32: str = ""


class ConnectionBrokenException(Exception):
    pass


class ConnectionTimeoutException(Exception):
    pass


class InvalidMessageFormatException(Exception):
    pass


class UnexpectedMessageException(Exception):
    pass


class AuthenticationFailureException(Exception):
    pass


class ProcedureApprovalException(Exception):
    pass


class ProcedureExecutionException(Exception):
    pass


class ProcedureAlreadyPresentException(Exception):
    pass


class FileTransmissionException(Exception):
    pass


class EmptyFileListException(Exception):
    pass


class MissingWorkingDirectoryException(Exception):
    pass


def send_message(connection: socket.socket, json_data):
    logging.debug(f"Sending message: {json_data}.")
    json_data_str = json.dumps(json_data)
    connection.sendall(
        bytes(
            MARKER_TRANSMISSION_START + json_data_str + MARKER_TRANSMISSION_END,
            encoding="utf-8",
        )
    )


def send_file(connection: socket.socket, file: bytes):
    logging.debug(f"Sending file.")
    connection.send(MARKER_FILE_START)
    connection.sendall(file)
    connection.send(MARKER_FILE_END)


def wait_for_response(connection: socket.socket) -> dict:
    logging.debug(f"Waiting for response.")

    raw_data = ""
    message_json = dict()
    is_message_received = False
    while not is_message_received:
        raw_data += connection.recv(1).decode("utf-8")
        if len(raw_data) == 0:
            """
            socket returns 0 when other party calls socket.close().
            """
            raise ConnectionBrokenException("Connected party disconnected.")

        if (
            raw_data.find(MARKER_TRANSMISSION_START) != -1
            and raw_data.find(MARKER_TRANSMISSION_END) != -1
        ):
            message_start_marker_index = raw_data.find(MARKER_TRANSMISSION_START) + len(
                MARKER_TRANSMISSION_START
            )
            message_end_marker_index = raw_data.find(MARKER_TRANSMISSION_END)

            message_data = raw_data[message_start_marker_index:message_end_marker_index]
            message_json = json.loads(message_data)
            logging.debug(f"Received message: {message_json}")

            message_end_index = message_end_marker_index + len(MARKER_TRANSMISSION_END)
            if len(raw_data) <= message_end_index:
                raw_data = ""
            else:
                raw_data = raw_data[message_end_index:]

            is_message_received = True

    return message_json
