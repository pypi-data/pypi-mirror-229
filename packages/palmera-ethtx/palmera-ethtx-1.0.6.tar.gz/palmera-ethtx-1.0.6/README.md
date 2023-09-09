<h1 align='center' style='border-bottom: none'>
  <p>Palmera EthTx - Ethereum transactions decoder by Palmera </p>
</h1>

<p align="center">
<a target="_blank">
    <img src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg" alt="Python">
</a>
<a target="_blank">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
</a>
<a target="_blank">
    <img src="https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github" alt="OpenSource">
</a>
<a target="_blank">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="Apache">
</a>
<a target="_blank">
    <img src="https://img.shields.io/pypi/v/EthTx?label=pypi%20package" alt="EthTxPyPi">
</a>
</p>

## Introduction

Source Code: [https://github.com/ethtx/ethtx](https://github.com/ethtx/ethtx)

## Installation

```shell
pip install palmera-ethtx
```

## Requirements

The package needs a few external resources, defined in `EthTxConfig` object:

1. **RPC node** - required to have access to the raw Ethereum data; it must be a full archive node with
   the `debug` option ON
2. **Etherscan API key** - required to get the source code and ABI for smart contracts used in transaction
3. (Optional) **MongoDB database** - required to store smart contracts' ABI and semantics used in the decoding process.
   If you don't want to setup permanent database, you can enter `mongomock://localhost/ethtx`, then in-memory mongo will be
   set up that discards all data with every run.

## Getting started

```python
from ethtx import EthTx, EthTxConfig
from ethtx.models.decoded_model import DecodedTransaction

ethtx_config = EthTxConfig(
    mongo_connection_string="mongomock://localhost/ethtx",  ##MongoDB connection string,
    etherscan_api_key="",  ##Etherscan API key,
    web3nodes={
        "mainnet": {
            "hook": "_Geth_archive_node_URL_",  # multiple nodes supported, separate them with comma
            "poa": _POA_chain_indicator_  # represented by bool value
        }
    },
    default_chain="mainnet",
    etherscan_urls={"mainnet": "https://api.etherscan.io/api", },
)

ethtx = EthTx.initialize(ethtx_config)
decoded_transaction: DecodedTransaction = ethtx.decoders.decode_transaction(
    '0x50051e0a6f216ab9484c2080001c7e12d5138250acee1f4b7c725b8fb6bb922d')
```

## Features

EthTx most important functions:

1. Raw node data access:

```python
web3provider = ethtx.providers.web3provider

from ethtx.models.w3_model import W3Transaction, W3Block, W3Receipt, W3CallTree

# read raw transaction data directly from the node
w3transaction: W3Transaction = web3provider.get_transaction(
    '0x50051e0a6f216ab9484c2080001c7e12d5138250acee1f4b7c725b8fb6bb922d')
w3block: W3Block = web3provider.get_block(w3transaction.blockNumber)
w3receipt: W3Receipt = web3provider.get_receipt(w3transaction.hash.hex())
w3calls: W3CallTree = web3provider.get_calls(w3transaction.hash.hex())
```

2. ABI decoding:

```python
from ethtx.models.decoded_model import (
    DecodedTransfer,
    DecodedBalance,
    DecodedEvent, DecodedCall,
)
from ethtx.models.objects_model import Transaction, Event, Block, Call

# read the raw transaction from the node
transaction = Transaction.from_raw(
    w3transaction=w3transaction, w3receipt=w3receipt, w3calltree=w3calls
)

# get proxies used in the transaction
proxies = ethtx.decoders.get_proxies(transaction.root_call, "mainnet")

block: Block = Block.from_raw(
    w3block=web3provider.get_block(transaction.metadata.block_number),
    chain_id="mainnet",
)

# decode transaction components
abi_decoded_events: List[Event] = ethtx.decoders.abi_decoder.decode_events(
    transaction.events, block.metadata, transaction.metadata
)
abi_decoded_calls: DecodedCall = ethtx.decoders.abi_decoder.decode_calls(
    transaction.root_call, block.metadata, transaction.metadata, proxies
)
abi_decoded_transfers: List[
    DecodedTransfer
] = ethtx.decoders.abi_decoder.decode_transfers(abi_decoded_calls, abi_decoded_events)
abi_decoded_balances: List[DecodedBalance] = ethtx.decoders.abi_decoder.decode_balances(
    abi_decoded_transfers
)

# decode a single event
raw_event: Event = transaction.events[3]
abi_decoded_event: DecodedEvent = ethtx.decoders.abi_decoder.decode_event(
    raw_event, block.metadata, transaction.metadata
)

# decode a single call
raw_call: Call = transaction.root_call.subcalls[0]
abi_decoded_call: DecodedCall = ethtx.decoders.abi_decoder.decode_call(
    raw_call, block.metadata, transaction.metadata, proxies
)
```

3. Semantic decoding:

```python
from ethtx.models.decoded_model import DecodedTransactionMetadata

# semantically decode transaction components
decoded_metadata: DecodedTransactionMetadata = (
    ethtx.decoders.semantic_decoder.decode_metadata(
        block.metadata, transaction.metadata, "mainnet"
    )
)
decoded_events: List[DecodedEvent] = ethtx.decoders.semantic_decoder.decode_events(
    abi_decoded_events, decoded_metadata, proxies
)

decoded_calls: Call = ethtx.decoders.semantic_decoder.decode_calls(
    abi_decoded_calls, decoded_metadata, proxies
)
decoded_transfers: List[
    DecodedTransfer
] = ethtx.decoders.semantic_decoder.decode_transfers(
    abi_decoded_transfers, decoded_metadata
)
decoded_balances: List[
    DecodedBalance
] = ethtx.decoders.semantic_decoder.decode_balances(
    abi_decoded_balances, decoded_metadata
)

# semantically decode a single event
decoded_event: DecodedEvent = ethtx.decoders.semantic_decoder.decode_event(
    abi_decoded_events[0], decoded_metadata, proxies
)
# semantically decode a single call
decoded_call: Call = ethtx.decoders.semantic_decoder.decode_call(
    abi_decoded_calls.subcalls[0], decoded_metadata, proxies
)
```

4. ABI decoding:

Test the Eth.tx:

```
make script
```

5. Example

```
# Decoding transaction on Goerli
decoded_transaction_goerli: DecodedTransaction = ethtx.decoders.decode_transaction(
    "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b", "goerli"
)
```

Etherscan Link: [Tx of Safe Address  in Goerli](https://goerli.etherscan.io/tx/0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b)

Ethtx.Info Link: [Tx of Safe Address  in Goerli](https://ethtx.info/goerli/0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b/)

Response

```json
{
  "balances": [
    {
      "holder": {
        "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
        "badge": "receiver",
        "name": "GnosisSafeProxy"
      },
      "tokens": [
        {
          "balance": "-100,000.0000",
          "token_address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
          "token_standard": "ERC20",
          "token_symbol": "OmniseaBaseToken"
        }
      ]
    },
    {
      "holder": {
        "address": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4",
        "badge": null,
        "name": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4"
      },
      "tokens": [
        {
          "balance": "100,000.0000",
          "token_address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
          "token_standard": "ERC20",
          "token_symbol": "OmniseaBaseToken"
        }
      ]
    }
  ],
  "block_metadata": {
    "block_hash": "0xc52f44b85b399d3341181864f85ebbcbf92f6081f74ded078dbbfd8d8b388b03",
    "block_number": "9647726",
    "canonical": true,
    "gas_limit": "30000000",
    "gas_used": "16010508",
    "miner": "0x8dc847af872947ac18d5d63fa646eb65d4d99560",
    "parent_hash": "0x9103881de8ca4f9e7ac0b76114a66fe68be4d5d1991c1bde64ae5a996d8f6883",
    "timestamp": "2023-09-06T16:04:36",
    "tx_count": "90"
  },
  "calls": {
    "arguments": [
      {
        "name": "to",
        "type": "address",
        "value": {
          "address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
          "badge": null,
          "name": "OmniseaBaseToken"
        }
      },
      {
        "name": "value",
        "type": "uint256",
        "value": "0"
      },
      {
        "name": "data",
        "type": "bytes",
        "value": "0xa9059cbb00000000000000000000000000b97496700288c1bceb90ecc0...800000"
      },
      {
        "name": "operation",
        "type": "uint8",
        "value": "0"
      },
      {
        "name": "safeTxGas",
        "type": "uint256",
        "value": "0"
      },
      {
        "name": "baseGas",
        "type": "uint256",
        "value": "0"
      },
      {
        "name": "gasPrice",
        "type": "uint256",
        "value": "0"
      },
      {
        "name": "gasToken",
        "type": "address",
        "value": {
          "address": "0x0000000000000000000000000000000000000000",
          "badge": null,
          "name": "0x0000000000000000000000000000000000000000"
        }
      },
      {
        "name": "refundReceiver",
        "type": "address",
        "value": {
          "address": "0x0000000000000000000000000000000000000000",
          "badge": null,
          "name": "0x0000000000000000000000000000000000000000"
        }
      },
      {
        "name": "signatures",
        "type": "bytes",
        "value": "0x3fe2737edc8e26ab9aa25ae3f03b783032f140d87d382ca4b1400d8994...000001"
      }
    ],
    "call_id": "",
    "call_type": "call",
    "chain_id": "goerli",
    "error": null,
    "from_address": {
      "address": "0xf285e70ca2002b796a575e473285282bbf39d790",
      "badge": "sender",
      "name": "0xf285e70ca2002b796a575e473285282bbf39d790"
    },
    "function_guessed": false,
    "function_name": "execTransaction",
    "function_signature": "0x6a761202",
    "gas_used": "90538",
    "indent": "0",
    "outputs": [
      {
        "name": "",
        "type": "bool",
        "value": "True"
      }
    ],
    "status": true,
    "subcalls": [
      {
        "arguments": [
          {
            "name": "to",
            "type": "address",
            "value": {
              "address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
              "badge": null,
              "name": "OmniseaBaseToken"
            }
          },
          {
            "name": "value",
            "type": "uint256",
            "value": "0"
          },
          {
            "name": "data",
            "type": "bytes",
            "value": "0xa9059cbb00000000000000000000000000b97496700288c1bceb90ecc0...800000"
          },
          {
            "name": "operation",
            "type": "uint8",
            "value": "0"
          },
          {
            "name": "safeTxGas",
            "type": "uint256",
            "value": "0"
          },
          {
            "name": "baseGas",
            "type": "uint256",
            "value": "0"
          },
          {
            "name": "gasPrice",
            "type": "uint256",
            "value": "0"
          },
          {
            "name": "gasToken",
            "type": "address",
            "value": {
              "address": "0x0000000000000000000000000000000000000000",
              "badge": null,
              "name": "0x0000000000000000000000000000000000000000"
            }
          },
          {
            "name": "refundReceiver",
            "type": "address",
            "value": {
              "address": "0x0000000000000000000000000000000000000000",
              "badge": null,
              "name": "0x0000000000000000000000000000000000000000"
            }
          },
          {
            "name": "signatures",
            "type": "bytes",
            "value": "0x3fe2737edc8e26ab9aa25ae3f03b783032f140d87d382ca4b1400d8994...000001"
          }
        ],
        "call_id": "0",
        "call_type": "delegatecall",
        "chain_id": "goerli",
        "error": null,
        "from_address": {
          "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
          "badge": "receiver",
          "name": "GnosisSafeProxy"
        },
        "function_guessed": false,
        "function_name": "execTransaction",
        "function_signature": "0x6a761202",
        "gas_used": "65065",
        "indent": "1",
        "outputs": [
          {
            "name": "",
            "type": "bool",
            "value": "True"
          }
        ],
        "status": true,
        "subcalls": [
          {
            "arguments": [
              {
                "name": "hash",
                "type": "bytes32",
                "value": "0x2f1aa87e0b2fc0d0f8b6b33ec3718da2b110d59197ceb66e3c74c338b169a6e2"
              },
              {
                "name": "v",
                "type": "bytes8",
                "value": "0x000000000000000000000000000000000000000000000000000000000000001b"
              },
              {
                "name": "r",
                "type": "bytes32",
                "value": "0x3fe2737edc8e26ab9aa25ae3f03b783032f140d87d382ca4b1400d899483f17a"
              },
              {
                "name": "s",
                "type": "bytes32",
                "value": "0x71292f1b4be1e6b8caf9927caade2fdc5043aed142a34d2ef4af23ed809ef558"
              }
            ],
            "call_id": "0_0000",
            "call_type": "staticcall",
            "chain_id": "goerli",
            "error": null,
            "from_address": {
              "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
              "badge": "receiver",
              "name": "GnosisSafeProxy"
            },
            "function_guessed": false,
            "function_name": "ecrecover",
            "function_signature": "0x2f1aa87e",
            "gas_used": "3000",
            "indent": "2",
            "outputs": [
              {
                "name": "",
                "type": "address",
                "value": {
                  "address": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4",
                  "badge": null,
                  "name": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4"
                }
              }
            ],
            "status": true,
            "subcalls": [],
            "timestamp": "2023-09-06T16:04:36",
            "to_address": {
              "address": "0x0000000000000000000000000000000000000001",
              "badge": null,
              "name": "Precompiled"
            },
            "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b",
            "value": "0.0"
          },
          {
            "arguments": [
              {
                "name": "recipient",
                "type": "address",
                "value": {
                  "address": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4",
                  "badge": null,
                  "name": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4"
                }
              },
              {
                "name": "amount",
                "type": "uint256",
                "value": "100000"
              }
            ],
            "call_id": "0_0001",
            "call_type": "call",
            "chain_id": "goerli",
            "error": null,
            "from_address": {
              "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
              "badge": "receiver",
              "name": "GnosisSafeProxy"
            },
            "function_guessed": false,
            "function_name": "transfer",
            "function_signature": "0xa9059cbb",
            "gas_used": "13260",
            "indent": "2",
            "outputs": [
              {
                "name": "",
                "type": "bool",
                "value": "True"
              }
            ],
            "status": true,
            "subcalls": [],
            "timestamp": "2023-09-06T16:04:36",
            "to_address": {
              "address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
              "badge": null,
              "name": "OmniseaBaseToken"
            },
            "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b",
            "value": "0.0"
          }
        ],
        "timestamp": "2023-09-06T16:04:36",
        "to_address": {
          "address": "0x3e5c63644e683549055b9be8653de26e0b4cd36e",
          "badge": null,
          "name": "GnosisSafeL2"
        },
        "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b",
        "value": "0.0"
      }
    ],
    "timestamp": "2023-09-06T16:04:36",
    "to_address": {
      "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
      "badge": "receiver",
      "name": "GnosisSafeProxy"
    },
    "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b",
    "value": "0.0"
  },
  "events": [
    {
      "call_id": null,
      "chain_id": "goerli",
      "contract": {
        "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
        "badge": "receiver",
        "name": "GnosisSafeProxy"
      },
      "event_guessed": false,
      "event_name": "SafeMultiSigTransaction",
      "event_signature": "0x66753cd2356569ee081232e3be8909b950e0a76c1f8460c3a5e3c2be32b11bed",
      "index": "81",
      "parameters": [
        {
          "name": "to",
          "type": "address",
          "value": {
            "address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
            "badge": null,
            "name": "OmniseaBaseToken"
          }
        },
        {
          "name": "value",
          "type": "uint256",
          "value": "0"
        },
        {
          "name": "data",
          "type": "bytes",
          "value": "0xa9059cbb00000000000000000000000000b97496700288c1bceb90ecc0...800000"
        },
        {
          "name": "operation",
          "type": "uint8",
          "value": "0"
        },
        {
          "name": "safeTxGas",
          "type": "uint256",
          "value": "0"
        },
        {
          "name": "baseGas",
          "type": "uint256",
          "value": "0"
        },
        {
          "name": "gasPrice",
          "type": "uint256",
          "value": "0"
        },
        {
          "name": "gasToken",
          "type": "address",
          "value": {
            "address": "0x0000000000000000000000000000000000000000",
            "badge": null,
            "name": "0x0000000000000000000000000000000000000000"
          }
        },
        {
          "name": "refundReceiver",
          "type": "address",
          "value": {
            "address": "0x0000000000000000000000000000000000000000",
            "badge": null,
            "name": "0x0000000000000000000000000000000000000000"
          }
        },
        {
          "name": "signatures",
          "type": "bytes",
          "value": "0x3fe2737edc8e26ab9aa25ae3f03b783032f140d87d382ca4b1400d8994...000001"
        },
        {
          "name": "additionalInfo",
          "type": "bytes",
          "value": "0x0000000000000000000000000000000000000000000000000000000000...000002"
        }
      ],
      "timestamp": "2023-09-06T16:04:36",
      "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b"
    },
    {
      "call_id": null,
      "chain_id": "goerli",
      "contract": {
        "address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
        "badge": null,
        "name": "OmniseaBaseToken"
      },
      "event_guessed": false,
      "event_name": "Transfer",
      "event_signature": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
      "index": "82",
      "parameters": [
        {
          "name": "from",
          "type": "address",
          "value": {
            "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
            "badge": "receiver",
            "name": "GnosisSafeProxy"
          }
        },
        {
          "name": "to",
          "type": "address",
          "value": {
            "address": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4",
            "badge": null,
            "name": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4"
          }
        },
        {
          "name": "value",
          "type": "uint256",
          "value": "100000"
        }
      ],
      "timestamp": "2023-09-06T16:04:36",
      "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b"
    },
    {
      "call_id": null,
      "chain_id": "goerli",
      "contract": {
        "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
        "badge": "receiver",
        "name": "GnosisSafeProxy"
      },
      "event_guessed": false,
      "event_name": "ExecutionSuccess",
      "event_signature": "0x442e715f626346e8c54381002da614f62bee8d27386535b2521ec8540898556e",
      "index": "83",
      "parameters": [
        {
          "name": "txHash",
          "type": "bytes32",
          "value": "0x2f1aa87e0b2fc0d0f8b6b33ec3718da2b110d59197ceb66e3c74c338b169a6e2"
        },
        {
          "name": "payment",
          "type": "uint256",
          "value": "0"
        }
      ],
      "timestamp": "2023-09-06T16:04:36",
      "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b"
    }
  ],
  "metadata": {
    "block_hash": "0xc52f44b85b399d3341181864f85ebbcbf92f6081f74ded078dbbfd8d8b388b03",
    "block_number": "9647726",
    "chain_id": "goerli",
    "from_address": null,
    "gas_limit": "96325",
    "gas_price": "1",
    "gas_used": "90538",
    "receiver": {
      "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
      "badge": "receiver",
      "name": "GnosisSafeProxy"
    },
    "sender": {
      "address": "0xf285e70ca2002b796a575e473285282bbf39d790",
      "badge": "sender",
      "name": "0xf285e70ca2002b796a575e473285282bbf39d790"
    },
    "success": true,
    "timestamp": "2023-09-06 16:04:36",
    "to_address": null,
    "tx_hash": "0xd028241a7bbd2068439351994c286614190b26ecbc1cc27f6f2e76c7d2325f5b",
    "tx_index": "21",
    "tx_value": "0"
  },
  "status": true,
  "transfers": [
    {
      "from_address": {
        "address": "0x7161be2924b4710d3754be067e01b0cd4544c695",
        "badge": "receiver",
        "name": "GnosisSafeProxy"
      },
      "to_address": {
        "address": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4",
        "badge": null,
        "name": "0x00b97496700288c1bceb90ecc04a40c4aeac8bb4"
      },
      "token_address": "0xaaaa826d36d58a9b0e1055a75dce79ae99751c18",
      "token_standard": "ERC20",
      "token_symbol": "OmniseaBaseToken",
      "value": "100000"
    }
  ]
}
```
