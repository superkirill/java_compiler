from scanner import TScanner
from LL1 import Analyser
from optimizer import Optimizer
from generator import Generator

def main():
    scan = TScanner("data.java")
    scan.set_pointer(0)
    while True:
        lexeme = scan.next_lexeme()
        print("| %20s | %20s | %5d | %2d: %4d - %2d|" % (lexeme[0], 
                                        lexeme[1],
                                        lexeme[2],
                                        lexeme[3],
                                        lexeme[4],
                                        lexeme[5]))
        if lexeme[1] == "TEnd":
            break
    scan.set_pointer(0)
    analyser = Analyser(scan)
    triads, tree = analyser.analyse()

    lexeme = scan.next_lexeme()
    if lexeme[1] == "TEnd":
        print("\n\n\nСинтаксических ошибок не обнаружено\n\n\n")
    else:
        scan.print_error("\n\n\nЛишний текст в конце программы\n\n\n")

    #optimizer = Optimizer(triads)
    #triads = optimizer.optimize()

    generator = Generator(triads, tree)
    generator.generate()


if __name__ == '__main__':
    main()