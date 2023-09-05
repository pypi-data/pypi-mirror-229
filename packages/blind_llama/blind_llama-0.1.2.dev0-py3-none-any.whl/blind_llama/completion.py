from typing import Optional, List
from pydantic import BaseModel, validator
from .errors import *
from .request_adapters import ForcedIPHTTPSAdapter
from .verify import *

import os
import requests
import json
import blind_llama
import tempfile
import typer
import warnings

# class Parameters(BaseModel):
#     # Activate logits sampling
#     do_sample: bool = False
#     # Maximum number of generated tokens
#     max_new_tokens: int = 20
#     # The parameter for repetition penalty. 1.0 means no penalty.
#     # See [this paper](https://arxiv.org/pdf/1909.05858.pdf) for more details.
#     repetition_penalty: Optional[float] = None
#     # Whether to prepend the prompt to the generated text
#     return_full_text: bool = False
#     # Stop generating tokens if a member of `stop_sequences` is generated
#     stop: List[str] = []
#     # Random sampling seed
#     seed: Optional[int]
#     # The value used to module the logits distribution.
#     temperature: Optional[float]
#     # The number of highest probability vocabulary tokens to keep for top-k-filtering.
#     top_k: Optional[int]
#     # If set to < 1, only the smallest set of most probable tokens with probabilities that add up to `top_p` or
#     # higher are kept for generation.
#     top_p: Optional[float]
#     # truncate inputs tokens to the given size
#     truncate: Optional[int]
#     # Typical Decoding mass
#     # See [Typical Decoding for Natural Language Generation](https://arxiv.org/abs/2202.00666) for more information
#     typical_p: Optional[float]
#     # Generate best_of sequences and return the one if the highest token logprobs
#     best_of: Optional[int]
#     # Watermarking with [A Watermark for Large Language Models](https://arxiv.org/abs/2301.10226)
#     watermark: bool = False
#     # Get generation details
#     details: bool = False
#     # Get decoder input token logprobs and ids
#     decoder_input_details: bool = False

#     @validator("best_of")
#     def valid_best_of(cls, field_value, values):
#         if field_value is not None:
#             if field_value <= 0:
#                 raise ValidationError("`best_of` must be strictly positive")
#             if field_value > 1 and values["seed"] is not None:
#                 raise ValidationError("`seed` must not be set when `best_of` is > 1")
#             sampling = (
#                 values["do_sample"]
#                 | (values["temperature"] is not None)
#                 | (values["top_k"] is not None)
#                 | (values["top_p"] is not None)
#                 | (values["typical_p"] is not None)
#             )
#             if field_value > 1 and not sampling:
#                 raise ValidationError("you must use sampling when `best_of` is > 1")

#         return field_value

#     @validator("repetition_penalty")
#     def valid_repetition_penalty(cls, v):
#         if v is not None and v <= 0:
#             raise ValidationError("`repetition_penalty` must be strictly positive")
#         return v

#     @validator("seed")
#     def valid_seed(cls, v):
#         if v is not None and v < 0:
#             raise ValidationError("`seed` must be positive")
#         return v

#     @validator("temperature")
#     def valid_temp(cls, v):
#         if v is not None and v <= 0:
#             raise ValidationError("`temperature` must be strictly positive")
#         return v

#     @validator("top_k")
#     def valid_top_k(cls, v):
#         if v is not None and v <= 0:
#             raise ValidationError("`top_k` must be strictly positive")
#         return v

#     @validator("top_p")
#     def valid_top_p(cls, v):
#         if v is not None and (v <= 0 or v >= 1.0):
#             raise ValidationError("`top_p` must be > 0.0 and < 1.0")
#         return v

#     @validator("truncate")
#     def valid_truncate(cls, v):
#         if v is not None and v <= 0:
#             raise ValidationError("`truncate` must be strictly positive")
#         return v

#     @validator("typical_p")
#     def valid_typical_p(cls, v):
#         if v is not None and (v <= 0 or v >= 1.0):
#             raise ValidationError("`typical_p` must be > 0.0 and < 1.0")
#         return v

# class Request(BaseModel):
#     inputs: str
#     parameters: Optional[Parameters]
#     stream: bool = False

#     @validator("inputs")
#     def valid_input(cls, v):
#         if not v:
#             raise ValidationError("The prompt cannot be empty")
#         return v

PCR_FOR_MEASUREMENT = 16
PCR_FOR_CERTIFICATE = 15

class AICertInvalidAttestationFormatException(AICertException):
    """AICert attestation parsing error (json)"""
    def __init__(self, err: Exception) -> None:
        self.__err = err
        self.message = f"Invalid attestation format\n{self.__err}"
        super().__init__(self.message)


class AICertInvalidAttestationException(AICertException):
    """Invalid attestation error"""
    pass


class PromptRequest(BaseModel):
    inputs: str

    @validator("inputs")
    def valid_input(cls, v):
        if not v:
            raise ValidationError("The prompt cannot be empty")
        return v

class Client():
    """A class to represent a connection to a BlindLlama server."""

    def __init__(
        self
    ):
        #self.__base_url = f"{openai2.api_base}:8000"
        self.__base_url = "https://llama_worker"
        self.__attest_url = "https://aicert_worker"
        self.__session = requests.Session()
        self.__session.mount(
            self.__base_url, ForcedIPHTTPSAdapter(dest_ip=blind_llama.api_base)
        )

        ca_cert = self.verify_server_certificate(blind_llama.security_config["expected_pcrs"]["codebasepcr"])

        server_ca_crt_file = tempfile.NamedTemporaryFile(mode="w+t", delete=False)
        server_ca_crt_file.write(ca_cert)
        server_ca_crt_file.flush()
        self.__session.verify = server_ca_crt_file.name

        super(Client, self).__init__()

    def verify_server_certificate(self, expected_pcr):
        """Retrieve server certificate and validate it with 
        the attestation report.
        """
        session = requests.Session()
        session.mount(
                self.__attest_url, ForcedIPHTTPSAdapter(dest_ip=blind_llama.api_base)
            )
        
        attestation = session.get(f"{self.__attest_url}/aTLS",verify=False)

        attestation_json = json.loads(attestation.content)
        print(attestation_json)
        ca_cert = attestation_json["ca_cert"]

        # Verify quote and CA TLS certificate
        self.verify_build_response(attestation.content, False, ca_cert, expected_pcr)
        return ca_cert
    
    def verify_build_response(self, build_response: bytes, verbose: bool = True, ca_cert = "", expected_pcr = ""):
        """Verify received attesation validity

        1. Parse the JSON reponse
        2. Check simulation mode
        3. Verify certificate chain
        4. Verify quote signature
        5. Verify boot PCRs (firmware, bootloader, initramfs, OS)
        6. Verify event log (final hash in PCR_FOR_MEASUREMENT) by replaying it (works like a chain of hashes)
        7. Verify TLS certificate (final hash in PCR_FOR_CERTIFICATE)
        
        Args:
            build_response (bytes): reponse of the attestation endpoint
            verbose (bool, default = False): whether to print verification information in stdout
        """
        try:
            build_response = json.loads(build_response)
        except Exception as e:
            AICertInvalidAttestationFormatException(e)
        
        if "simulation_mode" in build_response["remote_attestation"]:
            if self.__simulation_mode:
                warnings.warn(f"👀 Attestation generated in simulation mode", RuntimeWarning)
                return
            else:
                raise AICertInvalidAttestationException(f"❌ Attestation generated in simulation mode")

        build_response["remote_attestation"]["cert_chain"] = [
            decode_b64_encoding(cert_b64_encoded)
            for cert_b64_encoded in build_response["remote_attestation"]["cert_chain"]
        ]

        ak_cert = verify_ak_cert(
            cert_chain=build_response["remote_attestation"]["cert_chain"]
        )
        warnings.warn(f"⚠️ Bypassing certificate chain verification", RuntimeWarning)

        ak_cert_ = load_der_x509_certificate(ak_cert)
        ak_pub_key = ak_cert_.public_key()
        ak_pub_key_pem = ak_pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        build_response["remote_attestation"]["quote"] = {
            k: decode_b64_encoding(v)
            for k, v in build_response["remote_attestation"]["quote"].items()
        }
        att_document = check_quote(
            build_response["remote_attestation"]["quote"], ak_pub_key_pem
        )

        if verbose:
            typer.secho(f"✅ Valid quote", fg=typer.colors.GREEN)

            log.info(
                f"Attestation Document > PCRs :  \n{yaml.safe_dump(att_document['pcrs']['sha256'])}"
            )

        # We should check the PCR to make sure the system has booted properly
        # This is an example ... the real thing will depend on the system.
        # assert (
        #     att_document["pcrs"]["sha256"][0]
        #     == "d0d725f21ba5d701952888bcbc598e6dcef9aff4d1e03bb3606eb75368bab351"
        # )
        # assert (
        #     att_document["pcrs"]["sha256"][1]
        #     == "fe72566c7f411900f7fa1b512dac0627a4cac8c0cb702f38919ad8c415ca47fc"
        # )
        # assert (
        #     att_document["pcrs"]["sha256"][2]
        #     == "3d458cfe55cc03ea1f443f1562beec8df51c75e14a9fcf9a7234a13f198e7969"
        # )
        # assert (
        #     att_document["pcrs"]["sha256"][3]
        #     == "3d458cfe55cc03ea1f443f1562beec8df51c75e14a9fcf9a7234a13f198e7969"
        # )
        # assert (
        #     att_document["pcrs"]["sha256"][4]
        #     == "1f0105624ab37b9af59da6618a406860e33ef6f42a38ddaf6abfab8f23802755"
        # )
        # assert (
        #     att_document["pcrs"]["sha256"][5]
        #     == "d36183a4ce9f539d686160695040237da50e4ad80600607f84eff41cf394dcd8"
        # )

        # if verbose:
        #     typer.secho(f"✅ Checking reported PCRs are as expected", fg=typer.colors.GREEN)

        # To make test easier we use the PCR 16 since it is resettable `tpm2_pcrreset 16`
        # But because it is resettable it MUST NOT be used in practice.
        # An unused PCR that cannot be reset (SRTM) MUST be used instead
        # PCR 14 or 15 should do it
        event_log = check_event_log(
            build_response["event_log"],
            att_document["pcrs"]["sha256"][PCR_FOR_MEASUREMENT],
        )

        measured_pcr = att_document["pcrs"]["sha256"][PCR_FOR_MEASUREMENT]

        log.info(f"Server's Codebase PCR : {measured_pcr}")
        log.info(f"Expected Codebase PCR : {expected_pcr}")

        if expected_pcr == measured_pcr:
            typer.secho(f"✅ Code base PCR is expected value", fg=typer.colors.GREEN)
        else:
            typer.secho(f"❌ Codebase PCR does not match expected value", fg=typer.colors.RED)
            raise ValidationError(f"Expected Codebase PCR does not match the one provided by the server. Expected PCR: {expected_pcr} Measured PCR: {measured_pcr}")


        result = check_server_cert(
            ca_cert,
            att_document["pcrs"]["sha256"][PCR_FOR_CERTIFICATE],
        )
        if not result:
            # Disconnect destroys the runner, this might not be required for an attestation failure
            # self.disconnect()
            raise AICertInvalidAttestationException(f"❌ Attestation validation failed.")
        
        if verbose:
            typer.secho(f"✅ Valid event log", fg=typer.colors.GREEN)
            print(yaml.safe_dump(event_log))


        warnings.warn(f"The quote from the TPM is not endorsed by the Cloud provider for the alpha version of BlindLlama v0.1. For more information look at https://github.com/mithril-security/blind_llama")
        typer.secho(f"✨✨✨ ALL CHECKS PASSED", fg=typer.colors.GREEN)

    def predict(
        self,
        prompt: str
    ) -> str:
        """Start a prediction.
        Args:
            prompt (str): The prompt on which you want to run a prediction on.
        Returns:
            str: The result of the prediction made by the server
        """

        req = PromptRequest(inputs=prompt)
        resp = self.__session.post(
            self.__base_url + "/",
            json=req.dict(),
        )
        ret_json = resp.json()
        generated_text = ""
        for elem in ret_json:
            if "error" in elem:
                raise PredictionException(elem)
            if "generated_text" in elem:
                generated_text += f"{elem['generated_text'].strip()}\n"
        return generated_text.strip()

def create(model: str = "", prompt: str = "", temperature: float = 0.7) -> str:
    """
        Creates a new completion for the provided prompt and parameters.

        See https://platform.openai.com/docs/api-reference/completions/create for a list
        of valid parameters.
    """
    return Client().predict(prompt)
