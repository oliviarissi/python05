#!/usr/bin/env python3

from typing import Any, Union, Sequence, Protocol
from abc import ABC, abstractmethod


class DataProcessor(ABC):
    """Abstract base class for all data processors."""

    def __init__(self) -> None:
        self._data: list[tuple[int, str]] = []
        self._counter: int = 0

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

    def __init__(self) -> None:
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

    def __init__(self) -> None:
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

    def __init__(self) -> None:
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


class ExportPlugin(Protocol):
    """Interface for export plugins."""

    def process_output(self, data: list[tuple[int, str]]) -> None:
        ...


class CSVExporter():
    """Exports data as CSV string."""

    def process_output(self, data: list[tuple[int, str]]) -> None:
        """Print values as comma-separated string.

        Args:
            data (list[tuple[int, str]]): Input data to format.
        """

        values_csv = []
        for _, value in data:
            values_csv.append(value)
        row = ",".join(values_csv)

        print("CSV Output:")
        print(row)
        # row = ",".join(value for _, value in data)


class JSONExporter():
    """Exports data as JSON-like dict."""

    def process_output(self, data: list[tuple[int, str]]) -> None:
        """Print data as {"item_rank": "value"} mapping.

        Args:
            data (list[tuple[int, str]]): Input data to format.
        """

        result = {}
        for rank, value in data:
            result[f"item_{rank}"] = value

        json_format = "{" + ", ".join(
            f'"item_{k}": "{v}"'for k, v in [(r, val) for r, val in data]
        ) + "}"

        print("JSON Output:")
        print(json_format)
        # result = {f"item_{i}": value for i, (_, value) in enumerate(data)}


class DataStream:
    """Routes incoming data elements to the appropriate DataProcessor
    based on polymorphic validation rules.
    """

    def __init__(self) -> None:
        """Initialize DataStream with an empty list of processors."""
        self.processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        """Register a new data processor.

        Args:
            proc (DataProcessor): A processor that implements
            validate and ingest methods.
        """

        self.processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        """Process a stream of heterogeneous data elements.

        Each element is passed to registered processors. The first processor
        that validates the element will ingest it. If no processor can handle
        the element, an error message is printed.

        Args:
            stream (list[Any]): A list of arbitrary data elements to process.
        """

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
        """Print processing statistics for all registered processors.

        Displays:
        - Processor name (formatted for readability)
        - Total number of items processed
        - Remaining items currently stored in the processor
        """

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

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        """Extract up to `nb` items from each processor and export via plugin.

        Args:
            nb (int): Max items to extract per processor.
            plugin (ExportPlugin): Export handler for formatted output.
        """

        for processor in self.processors:
            data_export: list[tuple[int, str]] = []

            for x in range(nb):
                try:
                    data_export.append(processor.output())
                except IndexError:
                    break

            plugin.process_output(data_export)


def main() -> None:

    print("=== Code Nexus - Data Pipeline ===\n")

    print("Initialize Data Stream...\n")
    stream = DataStream()

    stream.print_processors_stats()

    print("\nRegistering Processors\n")
    numeric, text, log = NumericProcessor(), TextProcessor(), LogProcessor()
    stream.register_processor(numeric)
    stream.register_processor(text)
    stream.register_processor(log)

    data = [
        'Hello world', [3.14, -1, 2.71],
        [{'log_level': 'WARNING',
         'log_message': 'Telnet access! Use ssh instead'},
         {'log_level': 'INFO', 'log_message': 'User wil is connected'}],
        42, ['Hi', 'five']
    ]
    print(f"Send first batch of data on stream: {data}\n")
    stream.process_stream(data)
    stream.print_processors_stats()

    print("\nSend 3 processed data from each processor to a CSV plugin:")
    stream.output_pipeline(3, CSVExporter())

    print()
    stream.print_processors_stats()

    data_2 = [
        21, ['I love AI', 'LLMs are wonderful', 'Stay healthy'],
        [{'log_level': 'ERROR', 'log_message': '500 server crash'},
         {'log_level': 'NOTICE', 'log_message':
         'Certificate expires in 10 days'}],
        [32, 42, 64, 84, 128, 168], 'World hello'
    ]
    print(f"\nSend another batch of data: {data_2}\n")
    stream.process_stream(data_2)
    stream.print_processors_stats()

    print("\nSend 5 processed data from each processor to a JSON plugin:")
    stream.output_pipeline(5, JSONExporter())

    print()
    stream.print_processors_stats()


if __name__ == "__main__":
    main()
