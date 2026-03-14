#!/usr/bin/env python3

from typing import Any, List, Dict, Union, Optional
from abc import ABC, abstractmethod


def DataProcessor(ABC):

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def process(self, data: Any) -> str:
        pass

    def format_output(self, result: str) -> str:
        return f"Output: {result}"


def NumericProcessor(DataProcessor):

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


def TextProcessor(DataProcessor):

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


def LogProcessor(DataProcessor):

    def validate(self, data: Any) -> bool:

        #asi include key words namiesto :(INFO ERROR)

        return isinstance(data, str) and ":" in data

    def process(self, data: Any) -> str:
        try:
            if not self.validate(data):
                raise ValueError("Invalid log entry")

            level, message = data.split(":", 1)
            level = level.strip().upper()
            message = message.strip()

            if level == "ERROR":
                result = f"[ALERT] ERROR level detected: {message}"
            else:
                result = f"[INFO] {level} level detected: {message}"
            
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
    print("Processing multiple data types through same interface...\n")

    processors: List[DataProcessor] = [
        NumericProcessor(),
        TextProcessor(),
        LogProcessor(),
    ]

    inputs: List[Any] = [
        [1, 2, 3],
        "Hello Nexus",
        "INFO: System ready",
    ]

    for i, (processor, data) in enumerate(zip(processors, inputs), start=1):
        result = processor.process(data)
        print(f"Result {i}: {result.replace('Output: ', '')}")


    print("Foundation systems online. Nexus ready for advanced streams.")

if __name__ == "__main__":
    main()
