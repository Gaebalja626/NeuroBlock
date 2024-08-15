"""
validation.py

Description:
    이 모듈은 블록의 이름, 타입, 연결 정보가 유효한지 검증하는 함수를 제공합니다.
"""

def validate_block_name(name: str) -> bool:
    """
    블록의 이름이 유효한지 검증합니다.

    Args:
        name (str): 블록의 이름.

    Returns:
        bool: 이름이 유효하면 True, 그렇지 않으면 False.
    """
    if not name:
        return False
    if not isinstance(name, str):
        return False
    if len(name.strip()) == 0:
        return False
    return True

def validate_block_type(block_type: str, allowed_types: list) -> bool:
    """
    블록 타입이 유효한지 검증합니다.

    Args:
        block_type (str): 블록의 타입.
        allowed_types (list): 허용된 블록 타입의 리스트.

    Returns:
        bool: 블록 타입이 유효하면 True, 그렇지 않으면 False.
    """
    return block_type in allowed_types

def validate_connections(connections: dict, expected_ports: dict) -> bool:
    """
    블록의 연결 정보가 유효한지 검증합니다.

    Args:
        connections (dict): 블록의 연결 정보.
        expected_ports (dict): 기대되는 포트 구조 (input과 output).

    Returns:
        bool: 연결 정보가 유효하면 True, 그렇지 않으면 False.
    """
    for port_type, ports in expected_ports.items():
        if port_type not in connections:
            return False
        if not all(port in connections[port_type] for port in ports):
            return False
    return True
