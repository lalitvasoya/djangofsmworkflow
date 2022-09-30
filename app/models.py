from itertools import permutations

from django.db import models
from workflow.models import Workflow
from django_fsm import FSMField, transition, RETURN_VALUE, GET_STATE, TransitionNotAllowed


department = [
    'inward',
    'assortment',
    'main_table',
    'plotting',
    'planning',
    'sawing',
    'manufacture',
    'grading',
    'dispatch'
]

source_departments = [
    'assortment',
    'plotting',
    'planning',
    'sawing',
    'manufacture',
    'grading',
    'dispatch'
]


class DiamondManager(models.QuerySet):
    def next(self, instance, target=None):
        if target:
            instance.generic(target=target)

        if not instance.workflows.exists():
            raise Exception('Add at least one workflow')

        workflow = instance.workflows.first()
        states = workflow.states.split(',')
        len_states = len(states)
        index = states.index(instance.state)

        if index+1 < len_states:
            next_state = states[index+1]
            try:
                instance.generic(target=next_state)
            except TransitionNotAllowed:
                getattr(instance, next_state)()
        return self


class Diamond(models.Model):
    weight = models.FloatField()
    color = models.CharField(max_length=50)
    workflows = models.ManyToManyField(Workflow, through="DiamondWorkflow")
    state = FSMField(default='main_table')

    objects = DiamondManager.as_manager()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     states = permutations(department, 2)
    #
    #     for state_from, state_to in states:
    #         name = state_from + "_to_" + state_to
    #         setattr(Diamond, name, self.generic)

    @transition(field=state, source="main_table", target="inward")
    def inward(self):
        pass

    @transition(field=state, source="inward", target="assortment")
    def assortment(self):
        pass

    @transition(field=state, source='*', target=RETURN_VALUE(*source_departments[1:]))
    def generic(self, target='plotting'):
        return target


class DiamondWorkflow(models.Model):
    diamond = models.ForeignKey(Diamond, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
