"""Test qci-client utilities."""

from concurrent.futures import Future, ThreadPoolExecutor
import time
import unittest

import pytest

from qci_client.utils import _buffered_generator

MAX_WORKERS = 8
NUM_TASKS = 10


def _short_task(*args, **kwargs) -> tuple:
    """Simulate short 0.1s task, with pass-through args and kwargs."""

    time.sleep(0.1)

    return args, kwargs


def _medium_task(*args, **kwargs) -> tuple:
    """Simulate medium 1s task, with pass-through args and kwargs."""

    time.sleep(1)

    return args, kwargs


def _long_task_timeout(*args, **kwargs) -> tuple:
    """Simulate long 5s task that may time out, with pass-through args and kwargs."""

    for _ in range(5):
        time.sleep(1)

        if args[0] == int(NUM_TASKS / 2):
            raise TimeoutError("This long task timed out.")

    return args, kwargs


@pytest.mark.offline
class TestBufferedGeneration(unittest.TestCase):
    """Test various usages of utils._buffered_generator."""

    def test__buffered_generator_typical_usage(self):
        """Test buffered generator using typical usage pattern."""
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

            def _short_task_wrapper(*args, **kwargs) -> Future:
                return executor.submit(_short_task, *args, **kwargs)

            args_kwargs_generator = (
                (
                    ("fixed arg", idx),
                    {"key_fixed": "value_fixed", f"key_{idx}": f"value_{idx}"},
                )
                for idx in range(NUM_TASKS)
            )
            generator = _buffered_generator(
                buffer_length=MAX_WORKERS,
                task=_short_task_wrapper,
                args_kwargs_generator=args_kwargs_generator,
            )

            idx = 0
            for generated_value in generator:
                self.assertEqual(
                    generated_value,
                    (
                        ("fixed arg", idx),
                        {f"key_{idx}": f"value_{idx}", "key_fixed": "value_fixed"},
                    ),
                )
                idx += 1

            generator.close()  # Should not raise.
            self.assertEqual(idx, NUM_TASKS)

    def test__buffered_generator_internal_exception(self):
        """Test buffered generator with exception inside generator."""
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

            def _long_task_timeout_wrapper(*args, **kwargs) -> Future:
                return executor.submit(_long_task_timeout, *args, **kwargs)

            args_kwargs_generator = (
                (
                    (idx,),
                    {},
                )
                for idx in range(NUM_TASKS)
            )
            generator = _buffered_generator(
                buffer_length=MAX_WORKERS,
                task=_long_task_timeout_wrapper,
                args_kwargs_generator=args_kwargs_generator,
            )

            # An exception should occur in one task.
            with self.assertRaises(TimeoutError):
                idx = 0
                for generated_value in generator:
                    self.assertEqual(generated_value, ((idx,), {}))
                    idx += 1

            generator.close()  # Should not raise.

    def test__buffered_generator_external_exception(self):
        """Test buffered generator with exception outside generator (during yield)."""
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

            def _medium_task_wrapped(*args, **kwargs) -> Future:
                return executor.submit(_medium_task, *args, **kwargs)

            args_kwargs_generator = (
                (
                    (idx,),
                    {},
                )
                for idx in range(NUM_TASKS)
            )
            generator = _buffered_generator(
                buffer_length=MAX_WORKERS,
                task=_medium_task_wrapped,
                args_kwargs_generator=args_kwargs_generator,
            )

            idx = 0
            for generated_value in generator:
                self.assertEqual(generated_value, ((idx,), {}))

                if idx == int(NUM_TASKS / 2):
                    # Proceed as if an exception occurred in yield.
                    with self.assertRaises(StopIteration):
                        # Cancel tasks and close generator.
                        generator.throw(Exception)

                idx += 1

            generator.close()  # Should not raise.
