"""
    QuaO Project export_circuit.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import requests
from braket.circuits import Circuit
from qbraid import circuit_wrapper
from qiskit import transpile

from ..config.logging_config import logger
from ..enum.media_type import MediaType
from ..enum.provider_type import ProviderType
from ..enum.sdk import Sdk
from ..factory.provider_factory import ProviderFactory
from ..util.http_utils import HttpUtils

MAX_CIRCUIT_IMAGE_SIZE = 5 * (1024 ** 2)


def export_circuit_task(
        circuit_config_map: dict,
        backend_config_map: dict,
        user_token: str):
    """
      Export circuit to svg file then send to QuaO server for saving
      Args:
          circuit: circuit will be exported
          @param circuit_config_map: Circuit config map
          @param backend_config_map: Backend config map
          @param user_token: User token
    """
    logger.debug("[Circuit export] Start")

    circuit_export_url = circuit_config_map.get('circuit_export_url')

    if circuit_export_url is None or len(circuit_export_url) < 1:
        return

    figure_buffer = __convert(circuit_config_map=circuit_config_map,
                              backend_config_map=backend_config_map)

    buffer_value = figure_buffer.getvalue()
    content_type = MediaType.SVG_XML

    logger.debug("[Circuit export] Checking max file size")
    estimated_file_size = len(buffer_value)

    if estimated_file_size > MAX_CIRCUIT_IMAGE_SIZE:
        zip_file_buffer = __zip(io_buffer_value=buffer_value,
                                file_name="circuit_image.svg")

        buffer_value = zip_file_buffer.getvalue()
        content_type = MediaType.APPLICATION_ZIP

    __send(io_buffer=buffer_value,
           url=circuit_export_url,
           token=user_token,
           content_type=content_type)


def __convert(circuit_config_map, backend_config_map):
    """

    @param circuit_config_map:
    @param backend_config_map:
    @return:
    """
    logger.debug("[Circuit export] Preparing circuit figure...")
    transpiled_circuit = transpile_circuit(circuit_config_map.get('circuit'), backend_config_map)
    circuit_figure = transpiled_circuit.draw(output='mpl', fold=-1)

    logger.debug("[Circuit export] Converting circuit figure to svg file...")
    figure_buffer = BytesIO()
    circuit_figure.savefig(figure_buffer, format='svg', bbox_inches='tight')

    return figure_buffer


def transpile_circuit(circuit, backend_config_map: dict):
    """

    @param circuit: Circuit will be transpiled
    @param backend_config_map: Backend config map
    @return: Transpiled circuit
    """
    logger.debug("[Circuit export] Transpile circuit")

    if isinstance(circuit, Circuit):
        return circuit_wrapper(circuit).transpile(Sdk.QISKIT.value)

    provider_type = ProviderType.resolve(backend_config_map.get('provider_tag'))

    if ProviderType.AWS_BRAKET.__eq__(provider_type):
        provider_type = ProviderType.QUAO_QUANTUM_SIMULATOR

    provider = ProviderFactory.create_provider(
        provider_type=provider_type,
        sdk=Sdk.QISKIT,
        authentication=backend_config_map.get('authentication'))

    backend = provider.get_backend(backend_config_map.get('device_name'))

    return transpile(circuits=circuit, backend=backend)


def __zip(io_buffer_value, file_name):
    """

    @param io_buffer_value:
    @param file_name:
    @return:
    """
    logger.debug("[Circuit export] Zip file")

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, mode="w", compression=ZIP_DEFLATED) as zf:
        zf.writestr(file_name, io_buffer_value)

    return zip_buffer


def __send(io_buffer, url, token, content_type: MediaType):
    """

    @param io_buffer:
    @param url:
    @param token:
    @param content_type:
    """
    logger.debug("[Circuit export] Sending circuit svg image to [{0}] with POST method ...".format(
        url))

    payload = {'circuit': (
        'circuit_image.svg',
        io_buffer,
        content_type.value)}

    response = requests.post(url=url,
                             headers=HttpUtils.create_bearer_header(token),
                             files=payload)

    if response.ok:
        logger.debug("Sending request to QuaO backend successfully!")
    else:
        logger.debug("Sending request to QuaO backend failed with status {0}!".format(
            response.status_code))

    logger.debug("[Circuit export] Finish")
