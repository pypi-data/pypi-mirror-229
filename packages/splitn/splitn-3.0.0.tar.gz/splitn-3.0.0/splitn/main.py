import typer
from typing_extensions import Annotated

from os import path
from re import fullmatch

from loguru import logger

from utils.sequences import random_sequence
from utils.split import splitted

@logger.catch
def generate_output(
    operand: str,
    separator: str,
    times: int,
    as_string: bool
) -> None:
    try:
        if as_string or detect_string(operand):
            # handle simple strings
            generate_splitted_sequences(operand, separator)
        else: 
            # handle regular expressions
            for counter in range(times):
                sequence = random_sequence(operand)
                generate_splitted_sequences(sequence, separator)
                if counter < times - 1:
                    print()
    except Exception as e:
        raise typer.Abort(f"Program aborted with exception: {e}.")

@logger.catch
def generate_splitted_sequences(
    sequence: str,
    separator: str
) -> None:
    for splitted_sequence in splitted(sequence, separator):
        print(splitted_sequence)

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
    operands: Annotated[list[str], typer.Argument(
        help="""
        List of strings, regular expressions or files.

        Provided files should contain a list of strings or regular expressions.

        Regular expressions should have "\\" escaped (eg. "\\\\d") or be inside quotes.

        Given operands are treated as regular expressions by default.
        """
    )],
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
    )] = False
):
    for operand, counter in zip(operands, range(len(operands), 0, -1)):
        if path.exists(operand):
            with open(operand) as file:
                lines = file.readlines()
                for line, line_counter in zip(lines, range(len(lines), 0, -1)):
                    generate_output(line.strip(), separator, times, as_string)
                    if line_counter > 1:
                        print(secondary_separator)
        else:
            generate_output(operand, separator, times, as_string)
        if counter > 1:
            print(secondary_separator)

if __name__ == "__main__":
    app()
