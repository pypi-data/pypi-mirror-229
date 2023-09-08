from pyfiglet import Figlet

class Text():
    """Classe para formatar textos com cores e criar titulos com Figlet"""

    def __init__(self, content: str) -> None:
        self.text = content


    def clear() -> None:
        print("\033[H\033[2J\033[3J")


    def title(self, style="rozzo"):
        ascii = Figlet(font=style)
        arte = ascii.renderText(text=self.text)
        return Text(arte).blue()


    def red(self):
        return f"\033[1;31m{self.text}\033[0m"


    def blue(self):
        return f"\033[1;34m{self.text}\033[0m"


    def green(self):
        return f"\033[1;32m{self.text}\033[0m"


    def yellow(self):
        return f"\033[1;33m{self.text}\033[0m"


def create_menu(lista: list):
    string = ""
    
    for c, item in enumerate(lista):
        string += f"[{c+1}] - {Text(item).green()}\n"
    
    return string