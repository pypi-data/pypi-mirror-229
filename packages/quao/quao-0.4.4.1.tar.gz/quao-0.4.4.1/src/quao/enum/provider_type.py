"""
    QuaO Project base_enum.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""

from ..enum.base_enum import BaseEnum


class ProviderType(BaseEnum):
    QUAO_QUANTUM_SIMULATOR = 'QUAO_QUANTUM_SIMULATOR'
    IBM_QUANTUM = 'IBM_QUANTUM'
    IBM_CLOUD = 'IBM_CLOUD'
    AWS_BRAKET = 'AWS_BRAKET'

    @staticmethod
    def resolve(provider_type: str):
        for element in ProviderType:
            if element.value.__eq__(provider_type):
                return element

        raise Exception("Provider type is not supported!")
