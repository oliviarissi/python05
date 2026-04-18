#!/usr/bin/env python3

from typing import Any, Union, Sequence
from abc import ABC, abstractmethod


class DataProcessor(ABC):
    """Abstract base class for all data processors."""

    def __init__(self):
        self._data = []
        self._counter = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Check whether the provided data can be ingested by this processor.

        Args:
            data (Any): The data to validate.

        Returns:
            bool: True if the data is valid for processor, False otherwise.
        """
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        """Ingest and store the provided data after validation.

        Args:
            data (Any): The data to ingest.

        Raises:
            ValueError: If the provided data is invalid.
        """
        pass

    def output(self) -> tuple[int, str]:
        """Extract the oldest stored data item and its processing rank.

        Returns:
            tuple[int, str]: A tuple containing the rank and
            the stored data as a string.

        Raises:
            IndexError: If no data is available.
        """
        if not self._data:
            raise IndexError("No data available")

        rank, value = self._data.pop(0)
        return rank, value


class NumericProcessor(DataProcessor):
    """Processor for numeric data (int, float, and lists of both)."""

    def __init__(self):
        super().__init__()

    def validate(self, data: Any) -> bool:
        """Check whether the data is a valid numeric input.

        Accepts integers, floats, or lists containing only these types.

        Args:
            data (Any): The data to validate.

        Returns:
            bool: True if valid numeric data, False otherwise.
        """

        if isinstance(data, (int, float)):
            return True

        if isinstance(data, list):
            return all(isinstance(x, (int, float)) for x in data)

        return False

    def ingest(
        self,
        data: Union[int, float, Sequence[Union[int, float]]]
    ) -> None:
        """Ingest numeric data and store it as strings.

        Args:
            data (int | float | list[int | float]): Numeric data to ingest.

        Raises:
            ValueError: If the provided data is invalid.
        """

        if not self.validate(data):
            raise ValueError("Improper numeric data")

        if isinstance(data, (int, float)):
            self._data.append((self._counter, str(data)))
            self._counter += 1

        else:
            for item in data:
                self._data.append((self._counter, str(item)))
                self._counter += 1


class TextProcessor(DataProcessor):

    def __init__(self):
        super().__init__()

    def validate(self, data: Any) -> bool:
        """Check whether the data is a valid text input.

        Accepts strings or lists of strings.

        Args:
            data (Any): The data to validate.

        Returns:
            bool: True if valid text data, False otherwise.
        """

        if isinstance(data, str):
            return True

        if isinstance(data, list):
            return all(isinstance(x, str) for x in data)

        return False

    def ingest(self, data: Union[str, list[str]]) -> None:
        """Ingest text data and store it.

        Args:
            data (str | list[str]): Text data to ingest.

        Raises:
            ValueError: If the provided data is invalid.
        """
        if not self.validate(data):
            raise ValueError("Improper text data")

        if isinstance(data, str):
            self._data.append((self._counter, data))
            self._counter += 1

        else:
            for item in data:
                self._data.append((self._counter, item))
                self._counter += 1


class LogProcessor(DataProcessor):

    def __init__(self):
        super().__init__()

    def validate(self, data: Any) -> bool:
        """Check whether the data is a valid log entry.

        Accepts dictionaries with string keys and values containing
        'log_level' and 'log_message', or lists of such dictionaries.

        Args:
            data (Any): The data to validate.

        Returns:
            bool: True if valid log data, False otherwise.
        """

        def validate_dict(d: dict) -> bool:
            if not isinstance(d, dict):
                return False

            if not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in d.items()
            ):
                return False

            return "log_level" in d and "log_message" in d

        if isinstance(data, dict):
            return validate_dict(data)

        if isinstance(data, list):
            return all(validate_dict(x) for x in data)

        return False

    def ingest(self, data: Union[dict, list[dict]]) -> None:
        """Ingest log data and store formatted log messages.

        Args:
            data (dict | list[dict]): Log data to ingest.

        Raises:
            ValueError: If the provided data is invalid.
        """
        if not self.validate(data):
            raise ValueError("Improper log entry")

        if isinstance(data, dict):
            entry = f"{data['log_level']}: {data['log_message']}"
            self._data.append((self._counter, entry))
            self._counter += 1

        else:
            for item in data:
                entry = f"{item['log_level']}: {item['log_message']}"
                self._data.append((self._counter, entry))
                self._counter += 1


class DataStream:

    def __init__(self):
        self.processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self.processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:

        for item in stream:
            handled = False

            for processor in self.processors:
                if processor.validate(item):
                    processor.ingest(item)
                    handled = True
                    break

            if not handled:
                print("DataStream error - "
                      f"Can't process element in stream: {item}")

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")

        if not self.processors:
            print("No processor found, no data")
            return

        for processor in self.processors:
            name = processor.__class__.__name__
            name_form = name.replace("Processor", " Processor")
            total = processor._counter
            remaining = len(processor._data)

            print(f"{name_form}: total {total} items processed,",
                  f"remaining {remaining} on processor")


def main() -> None:

    print("=== Code Nexus - Data Stream ===\n")

    print("Initialize Data Stream...")
    stream = DataStream()
    stream.print_processors_stats()

    # Numeric Processor
    print("\nRegistering Numeric Processor\n")
    numeric = NumericProcessor()
    stream.register_processor(numeric)

    data = [
        'Hello world', [3.14, -1, 2.71],
        [{'log_level': 'WARNING',
         'log_message': 'Telnet access! Use ssh instead'},
         {'log_level': 'INFO', 'log_message': 'User wil is connected'}],
        42, ['Hi', 'five']
    ]
    print(f"Send first batch of data on stream: {data}")
    stream.process_stream(data)
    stream.print_processors_stats()

    # Other Processors
    print("\nRegistering other data processors")
    text = TextProcessor()
    log = LogProcessor()
    stream.register_processor(text)
    stream.register_processor(log)

    print("Send the same batch again")
    stream.process_stream(data)
    stream.print_processors_stats()

    print("\nConsume some elements from the data processors:",
          "Numeric 3, Text 2, Log 1")
    for i in range(3):
        numeric.output()
    for i in range(2):
        text.output()
    log.output()
    stream.print_processors_stats()


if __name__ == "__main__":
    main()
