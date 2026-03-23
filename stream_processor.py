#!/usr/bin/env python3

from typing import Any, List, Dict, Union, Optional
from abc import ABC, abstractmethod


class DataProcessor(ABC):
    """Abstract base class for all data processors."""

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
    def process(self, data: Any) -> str:
        """Process the data and return a formatted string.

        Args:
            data (Any): The data to process.

        Returns:
            str: Processed output as string.

        Raises:
            ValueError: If data is invalid.
        """
        pass

    def format_output(self, result: str) -> str:
        """Format the output string.

        Args:
            result (str): The processed result string.

        Returns:
            str: Formatted output.
        """
        return f"Output: {result}"


class NumericProcessor(DataProcessor):
    """Processor for numeric lists."""
    
    def validate(self, data: Any) -> bool:
        
        return isinstance(data, list) and all(isinstance(x, (int, float)) for x in data)

    def process(self, data: Any) -> str:
        
        
        try:
            if not self.validate(data):
                raise ValueError("Invalid numeric data")
            
            count = len(data)
            total = sum(data)
            avg = total / count if count else 0

            result = f"Processed {count} numeric values, sum={total}, avg={avg}"
            return super().format_output(result)

        except Exception as e:
            return self.format_output(f"Error processing numeric data: {e}")


class TextProcessor(DataProcessor):

    def validate(self, data: Any) -> bool:
        return isinstance(data, str)

    def process(self, data: Any) -> str:

        try:
            if not self.validate(data):
                raise ValueError("Invalid text data")

            chars = len(data)
            words = len(data.split())

            result = f"Processed text: {chars} characters, {words} words"
            return super().format_output(result)
        
        except Exception as e:
            return self.format_output(f"Error processing text: {e}")


class LogProcessor(DataProcessor):

    def validate(self, data: Any) -> bool:

        if not isinstance(data, str) or ":" not in data:
            return False
        
        level = data.split(":", 1)[0].strip().upper()
        return level in ["ERROR", "INFO", "WARNING", "DEBUG"]

    def process(self, data: Any) -> str:
        try:
            if not self.validate(data):
                raise ValueError("Invalid log entry")

            level, message = data.split(":", 1)
            level = level.strip().upper()
            message = message.strip()

            if level == "ERROR":
                result = f"[ALERT] ERROR level detected: {message}"
            elif level =="INFO":
                result = f"[INFO] INFO level detected: {message}"
            else:
                result = f"[LOG] {level}: {message}"
            
            return super().format_output(result)

        except Exception as e:
            return self.format_output(f"Error processing log: {e}")


def main() -> None:
    
    print("=== CODE NEXUS- DATA PROCESSOR FOUNDATION ===\n")

     # Numeric Processor
    print("Initializing Numeric Processor...")
    numeric = NumericProcessor()
    data = [1, 2, 3, 4, 5]
    print(f"Processing data: {data}")
    print("Validation:", "Numeric data verified" if numeric.validate(data) else "Invalid data")
    print(numeric.process(data), "\n")

    # Text Processor
    print("Initializing Text Processor...")
    text = TextProcessor()
    data = "Hello Nexus World"
    print(f'Processing data: "{data}"')
    print("Validation:", "Text data verified" if text.validate(data) else "Invalid data")
    print(text.process(data), "\n")

    # Log Processor
    print("Initializing Log Processor...")
    log = LogProcessor()
    data = "ERROR: Connection timeout"
    print(f'Processing data: "{data}"')
    print("Validation:", "Log entry verified" if log.validate(data) else "Invalid data")
    print(log.process(data), "\n")

    print("=== Polymorphic Processing Demo === ")
    print("Processing multiple data types through same interface...")

    processors: Dict[DataProcessor, Any] = {
        NumericProcessor(): [1, 2, 3],
        TextProcessor(): "Hello Nexus!",
        LogProcessor(): "INFO: System ready",
    }

    i: int  = 1
    for processor, data in processors.items():
        result = processor.process(data).replace("Output: ", "")
        print(f"Result {i}: {result}")
        i += 1


    print("\nFoundation systems online. Nexus ready for advanced streams.")

if __name__ == "__main__":
    main()
