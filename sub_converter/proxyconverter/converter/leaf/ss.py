from ...model import NodeInfo


def convert(node: NodeInfo) -> str:
    encrypt_method = f', encrypt-method={node.crypto_method}' if node.crypto_method else ''
    password = f', password={node.crypto_str}' if node.crypto_str else ''

    link = f'{node.protocol}, {node.server}, {node.port}{encrypt_method}{password}'

    return link
