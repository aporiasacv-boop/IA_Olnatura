from app.services.prompts.business_summary import build_business_summary_prompt

def test_build_business_summary_prompt_includes_data() -> None:
    prompt = build_business_summary_prompt(ventas_mes=125000, clientes=230)
    assert '125,000.00' in prompt
    assert '230' in prompt
    assert 'Ventas del mes' in prompt
    assert 'Total de clientes' in prompt

def test_build_business_summary_prompt_includes_interpretation_rules() -> None:
    prompt = build_business_summary_prompt(ventas_mes=1000, clientes=10)
    assert 'NO recomiendes' in prompt
    assert 'NO tomes decisiones' in prompt
    assert 'SOLO interpreta' in prompt
    assert 'se recomienda' in prompt
