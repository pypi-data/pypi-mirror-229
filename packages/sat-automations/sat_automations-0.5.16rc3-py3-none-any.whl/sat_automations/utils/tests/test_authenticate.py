import google
import requests

from sat_automations.manage_automations.models import ServiceAccount

DUMMY_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCukEnX6uQ4usr1
GDlPoIkyhTRjsgARojUlFwV8tZJmFdtP1l4L9P4M84P4fK9emkbTL9PPL6/vtfZt
QAmM3c6b64+lUicWoyQ08ITk0wWfhsE1MydwT/vxJNzs/7u/YODfvQAizhRPy4pW
u2EvJ0rlggbv1LDlYsKwFYWyrXh2AHWhjUgYOQxzme/gDGZ2pjwQ3R4Hdn4yB0dA
NnKIBWeieD4UX8e7+TQoFUEziUEIfLZdkfzis/jFTeQyd8kihl8LQPTNHOsric5r
m5I+CqHgphJarj7IEJrx8duovAQQ2/6r8uWqa+Nxtrh7G+ah6pYQ8hzsCpYH6KIo
ZP8GgZ3jAgMBAAECggEAAjtDS7prox4DuxEGbhW18mNibBBIO3+ycqrucwaPLlGR
NXq7Ke6iC26PtjXsfxinHjzk8n0Vkjw7eOIOdhYW52LpSBGFOfRpRTBsJgmVb3wu
ZeHsokCxuSL+Kqs05zXXKhNBxoV1qlhbwUD4Z0s+LsACVAaI6NBwKgZOL6zFWlWv
EGoiVN7T8/J/F8scaP8Kk95zDBPT18ZHb2HPg4ZkVv6fQVko1XuhQmrhNACWwg5V
NnBeT7HTIOu4/lx1B4Ui7tfgW8J4B7sZYeGnAWdkf4KZeevfDjCfAmxte+o3JNc9
l1Yd4+IASPR/qsnA9vjqorI7XemhK5JmQxKU1m7QgQKBgQDsRt2tuEuRvvLV8BrS
b3chfYsFNtGCYaZ3ibSXuRet5IBYh414O/j3WFYGOnxrFpX+RUCMo95MpaXvF3vZ
uDSiPZtFDflmJ/GrqFJbkrtEQaMxwF4M8EIobm1QAwX/l1ya/QNtuBe5ZGxDlgtA
6+CH2Sc+ELrIUOtxe0bo91vOUQKBgQC9IqNbHsreOHQx0anx1t4n8jWANVnn1foc
Er+T6lKsR9wu5WDJU/4tYfiFmh2C+ObOigzls3P6U1fJ0xrzOZTBstlm7awSZeoY
jJQLf6lef+pEIJ/Afd0n1s4L4dSXKkV4fVGOJsjF30ijBCN26B8FpP1N54BujZAe
TLT/VzuX8wKBgDTr3oUljU+UvGFsySUvMDjBHN1LHPweESIfJuMA4yvgzVqG6gnv
LOGB2KrGeM2nnmr4ae/WWFlElPkLgoMOfkOElv2Nlrnp4nh3WBMIt4cfSIVBOA+f
1MGnkjZkpvhLl8NjPlxZ6n5s3s74kYa2DnF/EwoUxzFM5p9hZE2T8e0xAoGAYnfO
JHp7lAZAOE+38rizIIjxYbZlAFZeyI7aPuAX+qnO8HtrUGXyRx5ijOwXwUBkqdMl
s9Eh6InLgr/toAOydsXuea/zjgCRSAaobPQh8ZkXFjEF+umMYllrHLSOQcU4NerI
swFuNdZxsq1M6XMf84haeFy2eNgq2BuHgAiidhECgYEAtnhsoF5zDT/XLLPlCY+5
lTs4LS3h0/j/ulFnVR3CbStPawdEvH7qyGukU2UXEekggRLK5tDkLqdlxf5XUHyE
ysth8IzmDA3Wre+hoL6eLa9u4PIxvSmy6PTITK2XGhnTbhj9jAUzFSGHU3tVx47l
XzOHQt8ahUjsmVGQsiWAV3I=
-----END PRIVATE KEY-----
"""

DUMMY_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArpBJ1+rkOLrK9Rg5T6CJ
MoU0Y7IAEaI1JRcFfLWSZhXbT9ZeC/T+DPOD+HyvXppG0y/Tzy+v77X2bUAJjN3O
m+uPpVInFqMkNPCE5NMFn4bBNTMncE/78STc7P+7v2Dg370AIs4UT8uKVrthLydK
5YIG79Sw5WLCsBWFsq14dgB1oY1IGDkMc5nv4AxmdqY8EN0eB3Z+MgdHQDZyiAVn
ong+FF/Hu/k0KBVBM4lBCHy2XZH84rP4xU3kMnfJIoZfC0D0zRzrK4nOa5uSPgqh
4KYSWq4+yBCa8fHbqLwEENv+q/Llqmvjcba4exvmoeqWEPIc7AqWB+iiKGT/BoGd
4wIDAQAB
-----END PUBLIC KEY-----
"""


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mock_google_authenticate(monkeypatch):
    def mock_signer_from_file(key):
        return google.auth.crypt.RSASigner.from_string(key)

    def mock_response_200(*args, **kwargs):
        return MockResponse({"message": "dummy"}, 200)

    monkeypatch.setattr(
        google.auth.crypt.RSASigner, "from_service_account_info", mock_signer_from_file
    )
    monkeypatch.setattr(requests, "post", mock_response_200)

    ServiceAccount.o
