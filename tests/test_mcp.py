from common.mcp_tools import lookup


def test_real_stdio_mcp_roundtrip():
    result = lookup('C001', 'ORD1001')
    assert result['order_id'] == 'ORD1001'
    assert result['customer_id'] == 'C001'
