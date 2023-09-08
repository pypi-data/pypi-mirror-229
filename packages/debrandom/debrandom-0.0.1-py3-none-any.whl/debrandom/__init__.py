"""
debrandom - a dum package for Idiot Sandwiches
"""
import os
import random
import typer

app = typer.Typer()


def test_function(prefix:str="500") -> str:
    """Returns a test string"""
    random_int = drandom(prefix)
    responses = [
        
    ]
    if prefix == "wow":
        return "This is a test"
    else:
        response = random.choice(responses)
        return response


@app.callback(invoke_without_command=True)
def cli(
        prefix: str = typer.Option("500", help="Prefix if custom"),
) -> None:
    """
    A dum package for Idiot Sandwiches.. Some of our offerings include:
    
    drandom - prints a random number using the dum algorithm
    dball - prints a magic response for all your dum problems
    dprint - prints a dum ascii art for dum people
    
    """
    test_function(prefix)


def dball():
    # magic 8ball for an idiot sandwich
    responses = [
        "You're a dumb idiot sandwich, but yes.",
        "Even a dumb idiot sandwich would say yes.",
        "Are you really asking a sandwich this question? Yes.",
        "You must be as dense as a sandwich to ask that. Yes.",
        "In the world of sandwiches, that's a yes.",
        "Absolutely, you dumb idiot sandwich!",
        "The answer is as clear as two slices of bread. Yes.",
        "If you were a sandwich, you'd be a 'yes' sandwich.",
        "Yes, and mayonnaise agrees with you.",
        "Even a dumb idiot sandwich can see it's a yes.",
        "No, but only because you're a smart sandwich!",
        "You're not a dumb idiot sandwich today. It's a yes.",
        "Even the dumbest of sandwiches would say yes to that.",
        "If you were any dumber, you'd be a sandwich. So yes.",
        "Yes, and don't forget the extra mayo!",
        "Yes, but don't eat this answer; it's just a sandwich.",
    ]

    # Generate a random response
    response = random.choice(responses)

    return response


def drandom(prefix: str = "500") -> None:
    print(f"{prefix}{random.randint(0,1000)}")


def dprint():
    print("""
                             ,╔φφφ≡,,
                           ,╠╩└''''└┘└╙╙Σ%#φ╓,,
                          ╓║░'''.'''''''''''''└╙╙"Σδ#φ≡╓,,
                         ╔║░''┌]≥ε⌐.'''┌.;'''''''.:φ╕'''└┘╙╙╙Σ#φ≡
                        ╔╟░'"╠╠⌐└ ''''┌░░░░'.'''.'' '7╙''.',▄#Θ╩╩╚
                       ╔╠'''\φε╙░'''''.└!∩''''╚╩'''..;╓▄@▀╩╙└┐┐││░≥
                      «╩''''┌└└'''¡≤░'''''''''┌┌╓▄╗╣╫╣╩│┐░│┐│││││┐¡░
                     ;╩ '''^░░░.''┌Γ¡''''.,µ╗▒▀╬▒░░░░▌\││││││││││░ε
                    ;╩ ''''''''''''┌'╓▄φ▒╠╠╬╬░░░░░░░░╙╦;¡¡┐┐││││¡.
                   «╩ ╔∩''''''',▄φ▒╠╬╬╠╠▒  φ░░░░░░░░░░░░▒▒▒▒¡¡│││¡.
                  «╩'''.';µ╗φ╬╣╫╣╙╙╟╠╠╠╠╠╠▒░░░░░░░╚╙╚▒░░░░░░▒┐││││░.
                 «╬;╓▄φ▒╬╫╩╠▒░░░φφ╔╠▒╠╠╠╠╠╠▒░░░░░░, ;░░░░░░░░▒┐¡│┐¡\,
                 ]╬╠╠╝╝╬░░░░░░░░░░░╚╬▒╠╠╠╠╠╫▒░░░░░░░░░░░░░░░  ╙W▄▄#╙╚▒
                 .╬▒╓,▐░░░░░░░░░░░░░╚╣▒╠╠╠╠╠╠▒░░░░░░░░░░░░Åε^░'.''.'▐╫▌
                 ╠╠╠╠╠▒╫░░░░░░▒╙╙▌░░▒╚╣▒╠╠╠╠╠▒╠╚╝▄▄▒▒▄▄╩╨└'''.'''''.╬╬▒
                 ╬╠╠╠╠╠▒╫░░░░░▒≡╓░░░░░╚╣▒╠╠╠╠╠╠, ⌠░└└└''.''''┌'┌'''@╫╬~
                 └╬▒╠╠╠╠▒╫░░░░░░░░░░░░░╚╙╠╫╫╫╩┘'.'''╙╛┌''''.''░░~']╬╬▒
                  └╬╠▒╠╠╠▒╫░░░░░░░░░░▒▒ ^░' '''''''"";░ε;╙╙'''└'''╬╬╫∩
                   └▒╠╠╠╠╠▒╣▒░░░░▒Å╩╙└'''''''''''''''└>"¡''''''''▐╢╬▒
                    └▒╠╠╠╠╠▒╙└╠╝╨┘'''''''.¡░┌'''''''''''''''''''.╬╬╬░
                     `╚╝╣╣╬▄∩░ .''''''''':░░░'''''''''''''''''''▐╫╣▒
                        ╔╙''''''''''.;∩^└''''''''''''''''''''''¡╬▒╬⌐
                        ╬▒╗╦╓,'''''''░└╓.]▒ε.'''''≤░.''''''''''╠╬╟'
                        ╚╬╬╬╬╢╬╬▒M╗╦µ;. ''''''''''└└''''''''''@╟╬╜
                        `╬▒░╬╬╬╩╝╫╬╬╬╬╬╣╣▒▄╗╗╦╦╓µ╓,;,''''',;╓φ╠╬╜'
                             "╙╩╩╩╬╬╣╫╫╬▒╩╝╬╬╬╬╬╬╬╬╬╣╣╫╫╣╣╬╬╣╬╣╬Γ
                                     `""╙╚∩!≤╝╫╬▓▓╬╣╫╬╬╣╫╝╫╢╩╬╩"
                                                  `└╙╙╚╩╩╩╩╩╙`
          """)
