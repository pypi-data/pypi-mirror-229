import os


def getFile(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", newline='') as csvFile:
            content = csvFile.read()
        return content
    else:
        raise FileNotFoundError(f"The csv-file at '{path}' could not be found.")


def conversion(file: str, delimiter1: str = "\t", delimiter2: str = ";") -> list:
    arr = []
    currentSubArr = []
    quoteOpen = False
    currentDelimiter = delimiter1  # Start with the first delimiter

    for char in file:
        if char == "\n":
            arr.append(currentSubArr)
            currentSubArr = []
            quoteOpen = False
        elif char == '"':
            quoteOpen = not quoteOpen
        elif (char == delimiter1 or char == delimiter2) and not quoteOpen:
            currentSubArr.append("")
            if char == delimiter1:
                currentDelimiter = delimiter1
            else:
                currentDelimiter = delimiter2
        else:
            currentSubArr[-1] += char

    return arr


def convert(filepath: str, delimiter1: str = "\t", delimiter2: str = ";") -> list:
    return conversion(getFile(filepath), delimiter1, delimiter2)
