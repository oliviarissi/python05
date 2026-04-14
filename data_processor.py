#!/usr/bin/env python3

from typing import Any, List, Dict, Union, Optional
from abc import ABC, abstractmethod


class DataProcessor(ABC):
    """Abstract base class for all data processors."""
    
    def __init__(self):
        self._data = []
        self._counter = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Check if the data is valid for this processor.

        Args:
            data (Any): The data to validate.

        Returns:
            bool: True if data is valid, False otherwise.
        """
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        """Process the data and return a formatted string.

        Args:
            data (Any): The data to process.

        Returns:
            str: Processed output as string.

        Raises:
            ValueError: If data is invalid.
        """
        pass

    def output(self) -> tuple[int, str]:
        """Output the ingested data as a tuple.

        Returns:
            tuple: Formatted output.
        """
        if not self._data:
            raise IndexError("No data available")

        rank, value = self._data.pop(0)
        return rank, value


class NumericProcessor(DataProcessor):
    """Processor for numeric lists."""

    def __init__(self):
        super().__init__()
    
    def validate(self, data: Any) -> bool:
        
        if isinstance(data, (int, float)):
            return True 
        
        if isinstance(data, list):
            return all(isinstance(x, (int, float)) for x in data)

        return False

    def ingest(self, data: Union[int, float, list[Union[int, float]]]) -> None:

        if not self.validate(data):
            raise ValueError("Invalid numeric data")

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
        
        if isinstance(data, str):
            return True
        
        if isinstance(data, list):
            return all(isinstance(x, str) for x in data)
        
        return False

    def ingest(self, data: Union[str, list[str]]) -> None:

        if not self.validate(data):
            raise ValueError("Invalid text data")

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

        def validate_dict(d: dict) -> bool:
            if not isinstance(d, dict):
                return False
            
            if not all(isinstance(k, str) and isinstance(v, str) for k, v in d.items()):
                return False

            return "log_level" in d and "log_message" in d
        
        if isinstance(data, dict):
            return validate_dict(data)

        if isinstance(data, list):
            return all(validate_dict(x) for x in data)
        
        return False

    def ingest(self, data: Union[dict, list[dict]]) -> None:

        if not self.validate(data):
            raise ValueError("Invalid log entry")

        if isinstance(data, dict):
            self._data.append((self._counter, f"{data['log_level']} : {data['log_message']}"))
            self._counter += 1

        else:
            for item in data:
                self._data.append((self._counter, f"{item['log_level']} : {item['log_message']}"))
                self._counter += 1



def main() -> None:
    
    print("=== Code Nexus - Data Processor ===\n")

     # Numeric Processor
    print("Testing Numeric Processor...")

    numeric = NumericProcessor()

    print(f"Trying to validate input '42': {numeric.validate(42)}")
    print(f"Trying to validate input 'Hello': {numeric.validate('Hello')}")

    print("Test invalid ingestion of string 'foo' without prior validation:")
    """TEST THIS"""

    data = [1, 2, 3, 4, 5]
    print(f"Processing data: {data}")
    numeric.ingest(data)
    if numeric._data == 1:
        print(f"Extracting {len(numeric._data)} value...")
    else:
        print(f"Extracting {len(numeric._data)} values...")
    
    # NOT LEN, determine how many will be extraced by fixed int (example has 3)


    # # Text Processor
    # print("Initializing Text Processor...")
    # text = TextProcessor()
    # data = "Hello Nexus World"
    # print(f'Processing data: "{data}"')
    # print("Validation:", "Text data verified" if text.validate(data) else "Invalid data")
    # print(text.process(data), "\n")

    # # Log Processor
    # print("Initializing Log Processor...")
    # log = LogProcessor()
    # data = "ERROR: Connection timeout"
    # print(f'Processing data: "{data}"')
    # print("Validation:", "Log entry verified" if log.validate(data) else "Invalid data")
    # print(log.process(data), "\n")

    # print("=== Polymorphic Processing Demo === ")
    # print("Processing multiple data types through same interface...")

    # processors: Dict[DataProcessor, Any] = {
    #     NumericProcessor(): [1, 2, 3],
    #     TextProcessor(): "Hello Nexus!",
    #     LogProcessor(): "INFO: System ready",
    # }

    # i: int  = 1
    # for processor, data in processors.items():
    #     result = processor.process(data).replace("Output: ", "")
    #     print(f"Result {i}: {result}")
    #     i += 1


if __name__ == "__main__":
    main()
