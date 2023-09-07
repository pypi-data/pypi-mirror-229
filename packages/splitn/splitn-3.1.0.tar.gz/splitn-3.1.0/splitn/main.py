import typer
from typing_extensions import Annotated
from typing import Optional

from os import path
from re import fullmatch

from loguru import logger

from utils.sequences import random_sequence
from utils.split import split_sequences

@logger.catch
def generate_output(
    operand: str,
    separator: str,
    times: int,
    as_string: bool,
    patterns: list[str] | None
) -> None:
    try:
        if as_string or detect_string(operand):
            # handle simple strings
            generate_split_sequences(operand, separator, patterns)
        else: 
            # handle regular expressions
            for counter in range(times):
                sequence = random_sequence(operand)
                generate_split_sequences(sequence, separator, patterns)
                if counter < times - 1:
                    print()
    except Exception as e:
        raise typer.Abort(f"Program aborted with exception: {e}.")

@logger.catch
def generate_split_sequences(
    sequence: str,
    separator: str,
    patterns: list[str] | None
) -> None:
    for split_sequence in split_sequences(sequence, separator):
        printable: bool = False if patterns else True
        if patterns:
            for pattern in patterns:
                printable = fullmatch(pattern, split_sequence.strip())
                if printable:
                    break
        if printable:
            print(split_sequence)

@logger.catch
def detect_string(
    input: str
) -> bool:
    try:
        return True if fullmatch(input, input) else False
    except:
        return False

app = typer.Typer()

@app.command()
def main(
    operands: Annotated[Optional[list[str]], typer.Argument(
        help="""
        List of strings, regular expressions or files.

        Provided files should contain a list of strings or regular expressions.

        Regular expressions should have "\\" escaped (eg. "\\\\d") or be inside quotes.

        Given operands are treated as regular expressions by default.
        """
    )] = None,
    separator: Annotated[str, typer.Option(
        "--separator", "-s",
        help="Separator used in splitting generated sequences."
    )] = " ",
    times: Annotated[int, typer.Option(
        "--times", "-t",
        help="Number of times splitn generates sequences for each specification. Applied only for regular expressions."
    )] = 1,
    secondary_separator: Annotated[str, typer.Option(
        "--secondary-separator",
        help="Separator used to separate outputs from different provided specifications. Use empty string for having new line."
    )] = "---",
    as_string: Annotated[bool, typer.Option(
        "--as-string",
        help="Interpret provided operands as simple strings."
    )] = False,
    patterns: Annotated[list[str], typer.Option(
        "--pattern", "-p",
        help="Use this option to either generate random sequence from regular expressions without splitting, or to narrow down sequences generated from given operands to those matching provided regular expressions.",
    )] = None
) -> None:
    if operands:
        for operand, counter in zip(operands, range(len(operands), 0, -1)):
            if path.exists(operand):
                with open(operand) as file:
                    lines = file.readlines()
                    for line, line_counter in zip(lines, range(len(lines), 0, -1)):
                        generate_output(line.strip(), separator, times, as_string, patterns)
                        if line_counter > 1:
                            print(secondary_separator)
            else:
                generate_output(operand, separator, times, as_string, patterns)
            if counter > 1:
                print(secondary_separator)
    elif patterns:
        for pattern, counter in zip(patterns, range(len(patterns), 0, -1)):
            print(random_sequence(pattern))
        if counter > 1:
            print(secondary_separator)
    else:
        print("Missing argument 'OPERANDS...' or an option.")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
