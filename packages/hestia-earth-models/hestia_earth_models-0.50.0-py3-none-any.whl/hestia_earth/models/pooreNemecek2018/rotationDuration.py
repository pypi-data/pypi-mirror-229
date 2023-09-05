from hestia_earth.schema import PracticeStatsDefinition

from hestia_earth.models.utils.practice import _new_practice
from hestia_earth.models.utils import sum_values
from .plantationLifespan import _get_value as get_plantationLifespan
from .longFallowPeriod import _get_value as get_longFallowPeriod
from .utils import run_products_average
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}]
    }
}
LOOKUPS = {
    "crop": ["Plantation_lifespan", "Plantation_longFallowPeriod"]
}
RETURNS = {
    "Practice": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'rotationDuration'


def _get_value(product: dict):
    plantationLifespan = get_plantationLifespan(product)
    longFallowPeriod = get_longFallowPeriod(product)
    return sum_values([plantationLifespan, longFallowPeriod])


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    practice['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return practice


def run(cycle: dict):
    value = run_products_average(cycle, TERM_ID, _get_value)
    return [_practice(value)] if value is not None else []
