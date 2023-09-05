import os

__all__ = []

try:
    from . import completion
    from .completion import Client, create

    api_key = ""
    api_base = "108.143.136.201"
    security_config = {
        "description": "Base config of BlindLlama",
        "expected_pcrs":
        {
            "codebasepcr": "6d46df491071512c4cfeba099bc8b09ccb3f8d75342820282919d85851178fa3",
            "tpmcert_pcr": "0f1893cf4d82f22112991eb3d5b9a236183385eaa80bc724d5a05c109ea19bc1"
        },
        "source_binary": "ghcr.io/mithril-security/text-generation-inference:sha256-5c5f1fbaae44e760fe46c792d8bff31d52cd572c6ade394617f7867b7400cd2d.att",
        "source_code": "https://github.com/mithril-security/text-generation-inference",
        "audit_certificates":
        {
            ""
        }
    }

    __all__ += ["completion", "Client", "create", "api_base", "api_key", "security_config"]

except ImportError as e:
    print(e)
    pass
