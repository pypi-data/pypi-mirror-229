from .context_manager import GlooCtx
from .common import EventBase, event_chain_var, event_metadata_var, event_tags_var
import asyncio
import pytest
import typing


def print_event_chain() -> None:
    event_chain = event_chain_var.get()
    print("Entered context")
    if event_chain is not None and all(
        isinstance(event, EventBase) for event in event_chain
    ):
        for i, event in enumerate(event_chain):
            print(f"{'    ' * (i + 1)} Event {i}: {event.func_name}")
            for prop, value in vars(event).items():
                print(f"{'    ' * (i + 1)}{prop}: {value}")
        print("-----")


@pytest.mark.asyncio
async def test_context_adds_parent_id() -> None:
    # Setup
    function = "test_function"
    variant = "test_variant"
    arg = "test_arg"
    ctx = GlooCtx[str, typing.Any](
        function=function, variant=variant, event_type="func_llm", arg=arg
    )

    # Execute
    await ctx.__aenter__()

    # Verify
    event_chain = event_chain_var.get()
    print("Entered context")
    print_event_chain()

    assert (
        event_chain is not None
    ), "Event chain should not be None after entering context"
    assert (
        len(event_chain) == 1
    ), "Event chain should have one event after entering context"
    event = event_chain[0]
    assert event
    assert event.func_name == function, "Function name in event does not match expected"
    # Enter another nested context
    nested_ctx = GlooCtx[str, typing.Any](
        function=function, variant=variant, event_type="func_llm", arg=arg
    )
    await nested_ctx.__aenter__()

    # Verify
    nested_event_chain = event_chain_var.get()
    print("Entered nested context")
    print_event_chain()

    assert (
        nested_event_chain is not None
    ), "Event chain should not be None after entering nested context"
    assert (
        len(nested_event_chain) == 2
    ), "Event chain should have two events after entering nested context"
    nested_event = nested_event_chain[1]
    assert nested_event
    assert (
        nested_event.func_name == function
    ), "Function name in nested event does not match expected"
    await nested_ctx.__aexit__(None, None, None)

    # Cleanup
    await ctx.__aexit__(None, None, None)
    assert (
        event_chain_var.get() is None
    ), "Event chain should be None after exiting context"
