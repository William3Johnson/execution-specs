"""
Ethereum Virtual Machine (EVM) Storage Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. contents:: Table of Contents
    :backlinks: none
    :local:

Introduction
------------

Implementations of the EVM storage related instructions.
"""

from ...state import get_storage, set_storage
from .. import Evm
from ..gas import (
    GAS_SLOAD,
    GAS_STORAGE_CLEAR_REFUND,
    GAS_STORAGE_SET,
    GAS_STORAGE_UPDATE,
    charge_gas,
)
from ..stack import pop, push


def sload(evm: Evm) -> None:
    """
    Loads to the stack, the value corresponding to a certain key from the
    storage of the current account.

    Parameters
    ----------
    evm :
        The current EVM frame.

    Raises
    ------
    :py:class:`~ethereum.tangerine_whistle.vm.exceptions.StackUnderflowError`
        If `len(stack)` is less than `1`.
    :py:class:`~ethereum.tangerine_whistle.vm.exceptions.OutOfGasError`
        If `evm.gas_left` is less than `50`.
    """
    # STACK
    key = pop(evm.stack).to_be_bytes32()

    # GAS
    charge_gas(evm, GAS_SLOAD)

    # OPERATION
    value = get_storage(evm.env.state, evm.message.current_target, key)

    push(evm.stack, value)

    # PROGRAM COUNTER
    evm.pc += 1


def sstore(evm: Evm) -> None:
    """
    Stores a value at a certain key in the current context's storage.

    Parameters
    ----------
    evm :
        The current EVM frame.

    Raises
    ------
    :py:class:`~ethereum.tangerine_whistle.vm.exceptions.StackUnderflowError`
        If `len(stack)` is less than `2`.
    :py:class:`~ethereum.tangerine_whistle.vm.exceptions.OutOfGasError`
        If `evm.gas_left` is less than `20000`.
    """
    # STACK
    key = pop(evm.stack).to_be_bytes32()
    new_value = pop(evm.stack)

    # GAS
    current_value = get_storage(evm.env.state, evm.message.current_target, key)
    if new_value != 0 and current_value == 0:
        gas_cost = GAS_STORAGE_SET
    else:
        gas_cost = GAS_STORAGE_UPDATE

    charge_gas(evm, gas_cost)

    if new_value == 0 and current_value != 0:
        evm.refund_counter += GAS_STORAGE_CLEAR_REFUND

    # OPERATION
    set_storage(evm.env.state, evm.message.current_target, key, new_value)

    # PROGRAM COUNTER
    evm.pc += 1
