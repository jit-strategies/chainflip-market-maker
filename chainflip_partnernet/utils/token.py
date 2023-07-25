import json
import os


class ERC20Token(object):
    def __init__(self, name: str, address: str):
        """
        :param name: name of the token
        :param address: token contract address
        """
        self._name = name.lower()
        self._address = address
        self._path = os.path.dirname(os.path.abspath(__file__))
        self._abi = None
        self._token = None
        self._load_abi_json()

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return f'{self._name} @ {self._address}'

    def _load_abi_json(self):
        """
        load abi from utils/abi/
        """
        with open(f'{self._path}/abi/{self._name}.json') as abi_file:
            self._abi = json.load(abi_file)

    def __call__(self, web3):
        """
        :param web3: web3 client
        :return: web3 loaded token contract
        """
        return web3.eth.contract(address=self._address, abi=self._abi)
