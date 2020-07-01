# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.


define e = Character("Eileen")


init python:
    import re
    NVLMODE = True
    def char(who_adv):
        def say(what, **kwargs):
            # ",,," and ",.," is shorthand for cases around unquoted/
            # quoted parts, to follow the rules for commas near quotes.
            # NVL>> "I said something," she said.
            # ADV>> I said something.
            if NVLMODE:
                what = what.replace(',,,', ",''").replace(',.,', ",''").replace(',!,', "!''")
                what = what.replace("<", '').replace(">", '')
                return nvl(what, **kwargs)
            else:
                what = what.replace(',,,', ", ").replace(',.,', ". ").replace(',!,', "! ")
                what = re.sub("<.*?>", '', what)
                return who_adv(what, **kwargs)
        return say
    e = char(e)
    narrator = char(adv)
    def mono(what, **kwargs):
        if NVLMODE:
            nvl(what, **kwargs)


# The game starts here.

label start:
    # Before we start, choose a mode -- NVL or ADV.

    menu:
        "Choose presentation mode."
        "ADV-style":
            $ NVLMODE = False
        "NVL-style":
            $ NVLMODE = True

    nvl clear


    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene bg room

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.

    show eileen happy

    # These display lines of dialogue.

    e "<''>Good morning,,,< said Eileen, ''>and welcome to my VN!<''>"
    e "<She said, ''>Right now there's not much here, except for tests of the text substitution function.<''>"
    e "<''>That way, you can read this in both ADV and NVL mode,.,< she continued.>"
    e "<''>It lets me write the text in short-story style, and then disable exposition that will be given by pictures rather than words in ADV mode,., <she concluded. ''>Isn't that neat?<''>"

    nvl clear

    mono """
        This text won't even be seen in ADV mode. It's only used for monologues in NVL mode.
        
        This will be used for long-winded exposition, like scene descriptions or describing the thoughts of characters.

        I'm not sure there are many VNs whose creators tried to do this sort of mode switching. It's mostly only one or the other.

        And I'm not even sure it'll work all that well. But it seems like it's worth a try.
    """

    # This ends the game.

    
    return
