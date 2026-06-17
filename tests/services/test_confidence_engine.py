from app.services.confidence_engine import ConfidenceEngine

def test_analytics_level_high() -> None:
    engine = ConfidenceEngine()
    assert engine.analytics_level(100) == 'HIGH'
    assert engine.analytics_level(250) == 'HIGH'

def test_analytics_level_medium() -> None:
    engine = ConfidenceEngine()
    assert engine.analytics_level(50) == 'MEDIUM'
    assert engine.analytics_level(99) == 'MEDIUM'

def test_analytics_level_low() -> None:
    engine = ConfidenceEngine()
    assert engine.analytics_level(49) == 'LOW'

def test_document_level_rules() -> None:
    engine = ConfidenceEngine()
    assert engine.document_level(0.85, 3) == 'HIGH'
    assert engine.document_level(0.70, 2) == 'MEDIUM'
    assert engine.document_level(0.50, 1) == 'LOW'
    assert engine.document_level(0.95, 0) == 'LOW'

def test_hybrid_level_combines_sources() -> None:
    engine = ConfidenceEngine()
    assert engine.hybrid_level('HIGH', 'HIGH') == 'HIGH'
    assert engine.hybrid_level('HIGH', 'MEDIUM') == 'MEDIUM'
    assert engine.hybrid_level('HIGH', 'LOW') == 'LOW'

def test_memory_level_rules() -> None:
    engine = ConfidenceEngine()
    assert engine.memory_level(2) == 'HIGH'
    assert engine.memory_level(1) == 'MEDIUM'
    assert engine.memory_level(0) == 'LOW'
