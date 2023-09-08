"""
    QuaO Project quao_provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC

from ...enum.provider_type import ProviderType
from ...model.provider.provider import Provider


class QuaoProvider(Provider, ABC):
    def __init__(self):
        super().__init__(ProviderType.QUAO_QUANTUM_SIMULATOR)
