from __future__ import print_function
from IPython.html.widgets import interact, interactive, fixed
from IPython.display import display, display_html
from IPython.html import widgets
import pandas as pd
import numpy as np
from time import sleep

def init():
    display_html("""
<style type="text/css">
    .state {
        width: 110px;
        height: 50px;
        background: pink;
        font-weight: bold;
    }
    .box {
        display: flex;
        justify-content: center;
        align-items: center;
        border: 3px solid grey;
        margin: 5px;
        padding: 5px;
    }
    .tape {
        width: 50px;
        height: 50px;
    }
    .head {
        background: yellow;
        font-weight: bold;
    }
    .configuration {
        display: flex;
        flex-wrap: wrap;
        flex-direction: row;
    }
</style>
""", raw=True)

def tape_html(tape, head):
    h = ""
    for i in xrange(0, len(tape)):
        symbol_html = str(tape[i]) if tape[i] != ' ' else '&nbsp;'
        head_class = ' head' if i == head else ''
        h += "<span class='box tape%s'>%s</span>" % (head_class, symbol_html)
    return h

def state_html(state):
    return "<span class='box state'>%s</span>" % state

class Configuration:
    def __init__(self,state,head,tape):
        self.state = state
        self.head = head
        self.tape = tape
    def __str__(self):
        return str({'state': self.state,
                    'head': self.head,
                    'tape': self.tape})
    def _repr_html_(self):
        return "<div class='configuration'>" + state_html(self.state) + tape_html(self.tape,self.head) + '</div>'

def sanitize_transitions(transitions):
    """sanitize transitions for 'accept' and 'reject' states and for '|>' (beginning of the tape)"""

    def new_transitions(state, read):
        if state in ('accept','reject'):
            return state, read, (1 if read == '|>' else -1)
        elif read == '|>':
            return 'start', read, 1
        else:
            return transitions(state, read)

    return new_transitions

def unary_wrap(run):
    """convert input to unary"""

    def run_unary(transitions, input, steps):
        return run(transitions, '1' * input, steps)

    return run_unary

def display_wrap(run):
    """display output of run"""

    def display_run(transitions, input, steps):
        display(run(transitions, input, steps))

    return display_run

def check_transitions(transitions, states, alphabet):
    pass

def transitions_table(transitions, states, alphabet):
    """represent transitions as table"""
    transitions = sanitize_transitions(transitions)

    check_transitions(transitions, states, alphabet)

    table = []
    for current in states:
        for read in alphabet:
            # DEBUG: print(state, read)
            next, write, move = transitions(current, read)
            table.append([current, read, next, write, move])

    df = pd.DataFrame(table, columns = ['current', 'read', 'next', 'write', 'move'])
    return df

def simulate(transitions,
             input='10101', unary=False, input_unary=12,
             pause=0.05, step_from=0, step_to=100, step_slack=100):
    """loads widget to simulate a given TM"""


    # widgets to specify the range of steps to simulate
    from_w = widgets.IntText(value=step_from, description="simulate from step")
    to_w = widgets.IntText(value=step_to, description="simulate to step")

    pause_w = widgets.FloatText(value=pause, description="pause between steps");

    # widget to indicate current step
    steps_w = widgets.IntSlider(min=0, max=step_to + step_slack, value=0, description="current step")

    # subroutine to animate the simulation
    def animate(x):
        steps_w.max = to_w.value + step_slack
        for steps in xrange(from_w.value, to_w.value+1):
            steps_w.value = steps
            sleep(pause_w.value)

    # button to start animated simulation
    simulate_w = widgets.Button(description='simulate')
    simulate_w.on_click(animate)

    input_w = widgets.Text(value=input, description="input")

    unary_w = widgets.Checkbox(value=unary, description='unary?')

    input_unary_w = widgets.IntText(value=input_unary, description='input number')

    def update():
        if unary_w.value:
            input_w.disabled = True
            input_unary_w.visible = True
            input_w.value = '1' * input_unary_w.value
        else:
            input_w.disabled = False
            input_unary_w.visible = False

    update()
    unary_w.on_trait_change(update)
    input_unary_w.on_trait_change(update)

    # display control widgets
    box = widgets.VBox(children=[simulate_w, from_w, to_w, pause_w, unary_w, input_unary_w])
    display(box)

    # widgets to display simulation
    interact(display_wrap(run),
             transitions=fixed(transitions), input=input_w, steps=steps_w)
