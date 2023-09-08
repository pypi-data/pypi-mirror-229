import asyncio
import logging
import time
from decimal import Decimal
from time import sleep
from typing import List, Union

import requests
import web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import Address, ChecksumAddress
from multicallable.async_multicallable import AsyncCall, AsyncMulticall
from requests import ConnectionError, JSONDecodeError, ReadTimeout, RequestException
from web3 import Web3
from web3._utils.contracts import encode_transaction_data
from web3.exceptions import TimeExhausted, TransactionNotFound

from .exceptions import (
    FailedOnAllRPCs,
    FailedToGetGasPrice,
    OutOfRangeTransactionFee,
    TransactionFailedStatus,
    Web3InterfaceException,
)
from .utils import TxPriority, get_span_proper_label_from_provider, get_unix_time


class ContractFunctionType:
    View = "view"
    Transaction = "transaction"


class MultiRpc:
    """
    This class is used to be more sure when running web3 view calls and sending transactions by using of multiple RPCs.
    """

    def __init__(
            self,
            rpc_urls: List[str],
            contract_address: str,
            contract_abi: dict,
            gas_limit: int = 1_000_000,
            gas_upper_bound: int = 26_000,
            gas_multiplier_low: float = 1,
            gas_multiplier_medium: float = 1.8,
            gas_multiplier_high: float = 3.84,
            apm=None,
    ):
        self.rpc_urls = rpc_urls
        self.providers = [
            web3.AsyncWeb3(Web3.AsyncHTTPProvider(r))
            if r.startswith("http")
            else web3.AsyncWeb3(Web3.WebsocketProvider(r))
            for r in rpc_urls
        ]
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract_abi = contract_abi
        self.apm = apm
        self.gas_multiplier_low = gas_multiplier_low
        self.gas_multiplier_medium = gas_multiplier_medium
        self.gas_multiplier_high = gas_multiplier_high

        self.contracts = []
        self.multi_calls = []

        self.functions = type("functions", (object,), {})()
        for func_abi in self.contract_abi:
            if func_abi.get("stateMutability") in ("view", "pure"):
                function_type = ContractFunctionType.View
            elif func_abi.get("type") == "function":
                function_type = ContractFunctionType.Transaction
            else:
                continue
            self.functions.__setattr__(
                func_abi["name"],
                self.ContractFunction(func_abi["name"], func_abi, self, function_type),
            )

        self.gas_limit = gas_limit
        self.gas_upper_bound = gas_upper_bound
        self.address = None
        self.private_key = None
        self.chain_id = None

    async def setup(self):
        self.chain_id = await self.providers[0].eth.chain_id
        for rpc, wb3 in zip(self.rpc_urls, self.providers):
            try:
                mc = AsyncMulticall()
                await mc.setup(w3=wb3)
                self.multi_calls.append(mc)
                self.contracts.append(
                    wb3.eth.contract(self.contract_address, abi=self.contract_abi)
                )
            except (ConnectionError, ReadTimeout) as e:
                # fixme: at least we should retry not ignoring rpc
                logging.warning(f"Ignore rpc {rpc} because of {e}")
        if not self.multi_calls:
            raise ValueError("No correct rpc provided")

    def set_account(self, address, private_key):
        """
        Set public key and private key for sending transactions. If these values set, there is no need to pass address,
        private_key in "call" function.
        Args:
            address: sender public_key
            private_key: sender private key
        """
        self.address = address
        self.private_key = private_key

    @staticmethod
    async def __gather_tasks(execution_list) -> List[any]:
        """
        Get an execution list and wait for all to end. If all executable raise an exception, it will raise a
        'Web3InterfaceException' exception, otherwise returns all results which has no exception
        Args:
            execution_list:

        Returns:

        """
        base_results = await asyncio.gather(*execution_list, return_exceptions=True)
        results = [res for res in base_results if not isinstance(res, Exception)]
        if len(results) == 0:
            exceptions = [res for res in base_results if isinstance(res, Exception)]
            for exc in exceptions:
                logging.exception(exc)
            raise Web3InterfaceException(
                f"All of RPCs raise exception. first exception: {exceptions[0]}"
            )
        return results

    async def __call_view_function(self, func_name: str, *args, **kwargs):
        """
        Calling view function 'func_name' by using of multicall

        Args:
            func_name: view function name
            *args:
            **kwargs:

        Returns:
            the results of multicallable object for each rpc
        """
        calls = [AsyncCall(cont, func_name, args, kwargs) for cont in self.contracts]
        execution_list = [mc.call([call]) for mc, call in zip(self.multi_calls, calls)]
        return await self.__gather_tasks(execution_list)

    async def get_nonce(self, address: Union[Address, ChecksumAddress, str]):
        execution_list = [
            provider.eth.get_transaction_count(address) for provider in self.providers
        ]
        return max(await self.__gather_tasks(execution_list))

    def __get_gas_from_metaswap(self, priority, gas_upper_bound):
        gas_provider = f"https://gas-api.metaswap.codefi.network/networks/{self.chain_id}/suggestedGasFees"
        try:
            resp = requests.get(gas_provider)
            resp_json = resp.json()
            max_fee_per_gas = Decimal(resp_json[priority]["suggestedMaxFeePerGas"])
            max_priority_fee_per_gas = Decimal(
                resp_json[priority]["suggestedMaxPriorityFeePerGas"]
            )
            if self.apm:
                self.apm.span_label(
                    max_fee_per_gas=max_fee_per_gas,
                    max_priority_fee_per_gas=max_priority_fee_per_gas,
                    gas_price_provider=gas_provider,
                )
            if max_fee_per_gas > gas_upper_bound:
                raise OutOfRangeTransactionFee(
                    f"gas price exceeded. {gas_upper_bound=} but it is {max_fee_per_gas}"
                )
            gas_params = {
                "maxFeePerGas": Web3.to_wei(max_fee_per_gas, "GWei"),
                "maxPriorityFeePerGas": Web3.to_wei(max_priority_fee_per_gas, "GWei"),
            }
            return gas_params
        except (RequestException, JSONDecodeError, KeyError):
            raise FailedToGetGasPrice("Failed to get gas info from metaswap")

    async def _get_gas_from_rpc(self, priority, gas_upper_bound):
        gas_price = None
        for provider_url, provider in zip(self.rpc_urls, self.providers):
            try:
                gas_price = await provider.eth.gas_price
                if self.apm:
                    self.apm.span_label(
                        gas_price=str(gas_price / 1e9), gas_price_provider=provider_url
                    )
            except (ConnectionError, ReadTimeout) as e:
                logging.error(f"Failed to get gas price from {provider_url}, {e=}")
                continue
            break
        if gas_price is None:
            raise FailedToGetGasPrice("Non of RCP could provide gas price!")
        if gas_price / 1e9 > gas_upper_bound:
            raise OutOfRangeTransactionFee(
                f"gas price exceeded. {gas_upper_bound=} but it is {gas_price / 1e9}"
            )
        multipliers = {
            TxPriority.Low: self.gas_multiplier_low,
            TxPriority.Medium: self.gas_multiplier_medium,
            TxPriority.High: self.gas_multiplier_high,
        }
        return dict(gasPrice=int(gas_price * multipliers.get(priority, 1)))

    async def _get_gas_price(self, gas_upper_bound, priority) -> dict:
        gas_params = {}
        if self.chain_id == 97:  # Test BNB Network
            gas_params["gasPrice"] = Web3.to_wei(10.1, "GWei")
        elif self.chain_id == 56:
            gas_params = await self._get_gas_from_rpc(priority, gas_upper_bound)
        else:
            try:
                gas_params = self.__get_gas_from_metaswap(priority, gas_upper_bound)
            except FailedToGetGasPrice:
                gas_params = await self._get_gas_from_rpc(priority, gas_upper_bound)
        return gas_params

    async def _get_tx_params(
            self, nonce, address, gas_limit, gas_upper_bound, priority
    ):
        gas_params = await self._get_gas_price(gas_upper_bound, priority)
        tx_params = {
            "from": address,
            "nonce": nonce,
            "gas": gas_limit or self.gas_limit,
            "chainId": self.chain_id,
        }
        tx_params.update(gas_params)
        return tx_params

    def _build_transaction(
            self, contract, func_name, func_args, func_kwargs, tx_params
    ):
        func_args = func_args or []
        func_kwargs = func_kwargs or {}
        return contract.functions.__getattribute__(func_name)(
            *func_args, **func_kwargs
        ).build_transaction(tx_params)

    async def _build_and_sign_transaction(
            self, contract, func_name, func_args, func_kwargs, signer_private_key, tx_params
    ):
        try:
            tx = await self._build_transaction(
                contract, func_name, func_args, func_kwargs, tx_params
            )
            account: LocalAccount = Account.from_key(signer_private_key)
            return account.sign_transaction(tx)
        except Exception as e:
            logging.error(
                "exception in build and sign transaction: %s, %s",
                e.__class__.__name__,
                str(e),
            )
            raise

    async def _send_transaction(self, provider: web3.AsyncWeb3, raw_transaction):
        try:
            rpc_label_prefix = get_span_proper_label_from_provider(
                provider.provider.endpoint_uri
            )
            transaction = await provider.eth.send_raw_transaction(raw_transaction)
            if self.apm:
                self.apm.span_label(
                    **{f"{rpc_label_prefix}_post_send_time": get_unix_time()}
                )
            return provider, transaction
        except ValueError as e:
            logging.error(f"value error: {str(e)}")
            t_bnb_flag = (
                    "transaction would cause overdraft" in str(e).lower()
                    and (await provider.eth.chain_id) == 97
            )
            if not (
                    t_bnb_flag
                    or "nonce too low" in str(e).lower()
                    or "already known" in str(e).lower()
            ):
                logging.exception("_send_transaction_exception")
                raise
        except (
                ConnectionError,
                ReadTimeout,
        ) as e:  # FIXME complete list
            logging.debug(
                "network exception in send transaction: %s, %s",
                e.__class__.__name__,
                str(e),
            )
        except Exception as e:
            # FIXME needs better exception handling
            logging.error(
                "exception in send transaction: %s, %s", e.__class__.__name__, str(e)
            )

    @staticmethod
    async def __wait_and_get_tx_receipt(provider, tx, timeout=60):
        con_err_count = tx_err_count = 0
        while True:
            try:
                receipt = await provider.eth.wait_for_transaction_receipt(
                    tx, timeout=timeout
                )
                if receipt.status != 1:
                    return provider, TransactionFailedStatus(Web3.to_hex(tx))
                break
            except ConnectionError:
                if con_err_count >= 5:
                    raise
                con_err_count += 1
                sleep(5)
            except (TimeExhausted, TransactionNotFound):
                if tx_err_count >= 1:  # double-check the endpoint_uri
                    raise
                tx_err_count += 1
                timeout *= 2
        return provider, None

    async def __call_tx(
            self,
            func_name: str,
            func_args: List,
            func_kwargs: dict,
            address: str,
            private_key: str,
            gas_limit: int,
            gas_upper_bound: int,
            wait_for_receipt: int,
            priority: str,
    ):
        nonce = await self.get_nonce(address)
        tx_params = await self._get_tx_params(
            nonce, address, gas_limit, gas_upper_bound, priority
        )
        signed_transaction = await self._build_and_sign_transaction(
            self.contracts[0], func_name, func_args, func_kwargs, private_key, tx_params
        )
        tx_hash = Web3.to_hex(signed_transaction.hash)
        if self.apm:
            self.apm.span_label(tx_hash=tx_hash)
        execution_list = [
            self._send_transaction(p, signed_transaction.rawTransaction)
            for p in self.providers
        ]
        result = None
        for task in asyncio.as_completed(execution_list):
            _start = time.time()
            result = await task
            if result:
                if self.apm:
                    self.apm.span_label(tx_send_time=int(time.time() * 1000))
                break
        if not result:
            raise FailedOnAllRPCs

        provider, tx = result
        if self.apm:
            self.apm.span_label(
                sent_provider=provider.provider.endpoint_uri
            )  # Double check endpoint_uri
        if not wait_for_receipt:
            return tx_hash

        execution_list = [
            self.__wait_and_get_tx_receipt(p, tx, wait_for_receipt)
            for p in self.providers
        ]
        occurred_exception = None
        for task in asyncio.as_completed(execution_list):
            try:
                result = await task
                if self.apm:
                    self.apm.span_label(
                        received_provider=provider.provider.endpoint_uri
                    )
                if result[1]:
                    raise result[1]
                return tx_hash
            except TransactionFailedStatus:
                raise
            except (ConnectionError, ReadTimeout) as e:
                logging.exception(e)
                occurred_exception = e
                continue
            except (TimeExhausted, TransactionNotFound) as e:
                occurred_exception = e
                continue
        raise occurred_exception

    async def _call_view_function(self, func_name: str, *args, **kwargs):
        results = await self.__call_view_function(func_name, *args, **kwargs)
        max_block_number = results[0][0]
        max_index = 0
        for i, result in enumerate(results):
            if result[0] > max_block_number:
                max_block_number = result[0]
                max_index = i
        return results[max_index][2][0]

    async def _call_tx_function(self, *args, **kwargs):
        return await self.__call_tx(*args, **kwargs)

    class ContractFunction:
        def __init__(self, name: str, abi: dict, multi_rpc_web3: "MultiRpc", typ: str):
            self.name = name
            self.mr = multi_rpc_web3
            self.typ = typ
            self.abi = abi
            self.args = None
            self.kwargs = None

        def __call__(self, *args, **kwargs):
            cf = MultiRpc.ContractFunction(self.name, self.abi, self.mr, self.typ)
            cf.args = args
            cf.kwargs = kwargs
            return cf

        def get_encoded_data(self):
            return encode_transaction_data(
                self.mr.providers[0],
                self.name,
                self.mr.contract_abi,
                self.abi,
                self.args,
                self.kwargs,
            )

        async def call(
                self,
                address: str = None,
                private_key: str = None,
                gas_limit: int = None,
                gas_upper_bound: int = None,
                wait_for_receipt: int = 90,
                priority: str = TxPriority.Low,
        ):
            if self.typ == ContractFunctionType.View:
                return await self.mr._call_view_function(
                    self.name, *self.args, **self.kwargs
                )
            elif self.typ == ContractFunctionType.Transaction:
                return await self.mr._call_tx_function(
                    self.name,
                    self.args,
                    self.kwargs,
                    address or self.mr.address,
                    private_key or self.mr.private_key,
                    gas_limit or self.mr.gas_limit,
                    gas_upper_bound or self.mr.gas_upper_bound,
                    wait_for_receipt,
                    priority,
                )
