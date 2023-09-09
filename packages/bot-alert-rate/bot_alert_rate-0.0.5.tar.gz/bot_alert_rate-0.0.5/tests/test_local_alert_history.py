import math
import pytest
import random

from bot_alert_rate.local_alert_history import (
    init_alert_history,
    update_alert_history,
    calculate_alert_rate,
    alert_history)

# FINDING #####################################################################

class Finding: # minimal port of the finding class
    def __init__(self, data):
        self.alert_id = data.get('alert_id', 'id1')
        self.metadata = data.get('metadata', {})

# FIXTURES ####################################################################

@pytest.fixture
def fixed_handle_transaction():
    def handle_transaction():
        return [Finding({'alert_id': 'id1', 'metadata': {}})]
    return handle_transaction

@pytest.fixture
def random_handle_transaction():
    def handle_transaction():
        _findings = []
        if random.uniform(0., 1.) <= 0.5:
            _findings.append(Finding({'alert_id': 'id1', 'metadata': {}}))
        if random.uniform(0., 1.) <= 0.1:
            _findings.append(Finding({'alert_id': 'id2', 'metadata': {}}))
        return _findings
    return handle_transaction

@pytest.fixture
def random_alert_history(random_handle_transaction):
    _history = init_alert_history(size=1024)
    for _ in range(1024):
        update_alert_history(fifo=_history, alerts=tuple(_f.alert_id for _f in random_handle_transaction()))
    return _history

# BUFFER ######################################################################

def test_history_has_fixed_size(random_alert_history):
    _before = len(random_alert_history)
    for _ in range(128):
        update_alert_history(fifo=random_alert_history, alerts=())
    _after = len(random_alert_history)
    assert _before == _after

# CALCULATION #################################################################

def test_alert_rate_is_a_probability(random_alert_history): # between 0. and 1.
    _rate_1 = calculate_alert_rate(fifo=random_alert_history, alert='id1')
    _rate_2 = calculate_alert_rate(fifo=random_alert_history, alert='id2')
    assert 0. <= _rate_1 and _rate_1 <= 1.
    assert 0. <= _rate_2 and _rate_2 <= 1.

def test_alert_rate_calculation_is_correct(random_alert_history):
    _rate_1 = calculate_alert_rate(fifo=random_alert_history, alert='id1')
    _rate_2 = calculate_alert_rate(fifo=random_alert_history, alert='id2')
    assert math.isclose(_rate_1, 0.5, abs_tol=0.05)
    assert math.isclose(_rate_2, 0.1, abs_tol=0.05)

# DECORATOR ###################################################################

def test_decorator_adds_anomaly_score_to_handle_transaction_output(fixed_handle_transaction):
    @alert_history(size=64)
    def decorated_handle_transaction():
        return fixed_handle_transaction()
    _findings_without_decorator = fixed_handle_transaction()
    _findings_with_decorator = decorated_handle_transaction()
    assert 'anomaly_score' not in _findings_without_decorator[0].metadata
    assert 'anomaly_score' in _findings_with_decorator[0].metadata

def test_decorator_alert_rate_calculation_is_correct(fixed_handle_transaction):
    @alert_history(size=64)
    def decorated_handle_transaction():
        return fixed_handle_transaction()
    _findings = decorated_handle_transaction()
    assert _findings[0].metadata['anomaly_score'] == 1. / 64.
