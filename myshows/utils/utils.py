from random import sample

from django.urls import reverse


def sample_facts(fact_set, necessary_fact_id=None):
    """Function to get a list of 5 random facts, including necessary fact is provided"""

    facts = sample(list(fact_set), k=5) if len(fact_set) > 5 else fact_set.all()

    if necessary_fact_id:
        facts[0] = fact_set.get(id=necessary_fact_id)

    for fact in facts:
        for occurrence in fact.entity_occurrences.all():
            fact.string = f'''{fact.string[:occurrence.position_start]}
                                <a class="btn badge bg-occurrence" href="{
                                    reverse("named_entity", args=[occurrence.named_entity.id])
                                }" id="occurrence-{occurrence.id}">
                                    {fact.string[occurrence.position_start:occurrence.position_end]}
                                </a>{fact.string[occurrence.position_end:]}'''

    return facts
