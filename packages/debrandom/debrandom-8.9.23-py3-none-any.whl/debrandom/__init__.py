"""
debrandom - a dum package for Idiot Sandwiches
"""
import os
import random
import typer

app = typer.Typer()


def test_function(prefix:str="500") -> str:
    """Returns a test string"""
    random_int = drandom(prefix, ret=True)
    print("I took my liberty with trimming the sample list, it is by no means all instances.. also the number in the actual chat has been replaced by debrandom o7 \n")
    responses = [
        "15/07/22, 09:05 - Noble Mathews: Also your random number generator is 🙇‍♂️",
        "13/03/23, 18:19 - Idiot Sandwich 🥪: My random number generated is skewed😂🙇‍♀️",
        f'19/06/20, 14:16 - Idiot Sandwich 🥪: Oh yeah.. I had every installation problem ever...and my way of fixing things is undoing everything and attempting {random_int} "clean " installations...its finally working now😂',
        f'17/08/20, 23:29 - Idiot Sandwich 🥪: Imma go read all the {random_int} e book pdfs that Ive been downloading😂',
        f'11/11/20, 12:30 - Idiot Sandwich 🥪: Like do you do flutter among all the other {random_int} things that you do?',
        f'25/10/21, 15:52 - Idiot Sandwich 🥪: And only on 2 places...out of the {random_int} other places',
        f'21/12/21, 07:41 - Idiot Sandwich 🥪: 😂😂😂😂 wow noble, losing track of your {random_int} tasks',
        f'03/01/22, 14:56 - Idiot Sandwich 🥪: I did nothing🤦‍♀️🤦‍♀️🤦‍♀️sorry for calling you {random_int} times...you have a safe trip',
        f'16/03/22, 13:29 - Idiot Sandwich 🥪: thats because you are Noble and you do {random_int} things irrespective of the courseload😂',
        f'25/03/22, 09:11 - Idiot Sandwich 🥪: Hows your {random_int} course projects going?',
        f'28/03/22, 14:20 - Idiot Sandwich 🥪: The calculate some stuff part I know how to do....BUT.....do you know how one can upload a generic model and dataset? There can be some {random_int} compatability issues right?',
        f'14/04/22, 01:57 - Idiot Sandwich 🥪: 😂😂 Thank you!! I hope you do your {random_int} things and have a great day!!!',
        f'06/07/22, 23:50 - Idiot Sandwich 🥪: oh no no, no issues at all, you please do your {random_int} other things also🙇‍♀️',
        f'24/08/22, 07:28 - Idiot Sandwich 🥪: Ill get started on the eulogy then, pretty sure I can write {random_int} pages, youre so awesome! 🤷‍♀️😭😭',
        f'14/12/22, 19:26 - Idiot Sandwich 🥪: Nope...I just need real time info on whether I need to call him {random_int} times or not',
        f'11/01/23, 02:33 - Idiot Sandwich 🥪: And. I promise Ill get started on all the {random_int} pending things, I am very very sorry',
        f'22/01/23, 10:21 - Idiot Sandwich 🥪: Not everyones shameless like me....I have no shame and hence i ask you {random_int} questions shamelessly...but other mundane people prolly let pride get in their way and they feel ...I dunno...bad asking you too many questions?',
        f'26/03/23, 15:09 - Idiot Sandwich 🥪: You can them come off accordingly...whenever you feel like getting ofd your {random_int} desktops🥲',
        f'29/04/23, 23:00 - Idiot Sandwich 🥪: Are you sleeping right now? I dunno...I hope these pings dont disturb you and you wake up to {random_int} messages from me😂❤️'
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


def drandom(prefix: str = "500", ret=False) -> None:
    if ret:
        return f"{prefix}{random.randint(0,1000)}"
    else:
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
