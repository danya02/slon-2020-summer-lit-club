label incident1:
    "Инцидент 1: предварительное описание"
    jump incident1_options

default incident1_visited = []

label incident1_options:
    menu:
        set incident1_visited
        "Что мне теперь стоит сделать?"
        
        "Изучить подробнее.":
            jump incident1_explore
        
        "Обсудить с знакомым.":
            jump incident1_talk

        "Сделать что-то срочное.":
            jump incident1_urgent


    jump incident1_after_actions

label incident1_explore:
    "Я изучаю этот инцидент."
    "Наблюдения показывают: всё плохо."
    jump incident1_options

label incident1_talk:
    "Я обсуждаю ситуацию с знакомым."
    if len(incident1_visited)==1:
        "Поскольку я это делаю первым делом, что-то дополнительное может произойти."
    "Это ни к чему не приводит, но я узнаю какую-то информацию."
    jump incident1_options

label incident1_urgent:
    "Я делаю что-то срочное."
    if len(incident1_visited) == 3:
        "Но из-за того, что я дождался последнего момента, чтобы делать эту срочную вещь, я получаю отдельную концовку."
        return
    jump incident1_options

label incident1_after_actions:
    "Я сделал всё, что мог. Теперь инцидент разрешается."
    $ order = '->'.join(incident1_visited)
    "$$$ Порядок моих действий: [order] $$$"
    jump incident2
