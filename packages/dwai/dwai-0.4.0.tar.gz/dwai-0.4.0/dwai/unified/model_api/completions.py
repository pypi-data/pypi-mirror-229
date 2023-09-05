import json
import dwai
from jsonpath_ng import parse
from dwai.azure.model_api.completions import AzureCompletions
from dwai.bailian.model_api.completions import Completions
from dwai.mini.model_api.completions import MiniCompletions
from dwai.pangu.model_api.completions import PanGuCompletions
from dwai.tione.v20211111.tione_client import TioneClient
from dwai.zhipuai.model_api.api import ModelAPI


def azure_qa(**kwargs):
    chat = AzureCompletions()
    json_output = chat.call(prompt=kwargs.get('prompt'), model=kwargs.get('model'), stream=False)
    matches = parse('$.choices[0].message.content').find(json_output)
    if len(matches) > 0:
        return {"output": {"text": matches[0].value}, "Success": True}
    else:
        return {}


def mini_qa(**kwargs):
    chat = MiniCompletions()
    json_output = chat.call(prompt=kwargs.get('prompt'), model=kwargs.get('model'), stream=False)
    matches = parse('$.choices[0].messages[0].text').find(json_output)
    if len(matches) > 0:
        return {"output": {"text": matches[0].value}, "Success": True}
    else:
        return {}


def dwai_bailian_qa(**kwargs):
    chat = Completions()
    json_output = chat.call(app_id="1e4ddc3659324ad0b8a0039230f1dba3", prompt=kwargs.get('prompt'),
                            model=kwargs.get('model'))
    matches = parse('$.output.text').find(json_output)
    if len(matches) > 0:
        return {"output": {"text": matches[0].value}, "Success": True}
    else:
        return {}


def zhipuai_chatglm_std(**kwargs):
    model = ModelAPI()
    json_output = model.invoke(model=kwargs.get('model'), prompt=[{"role": "user", "content": kwargs.get('prompt')}],
                               top_p=kwargs.get('top_p', 0.7), temperature=kwargs.get('temperature', 0.9))
    matches = parse('$.data.choices[0].content').find(json_output)
    if len(matches) > 0:
        return {"output": {"text": matches[0].value}, "Success": True}
    else:
        return {}


def pangu_completions(**kwargs):
    chat = PanGuCompletions()
    json_output = chat.call(max_tokens=kwargs.get('max_tokens', 600), prompt="",
                            messages=[{"role": "user", "content": kwargs.get('prompt')}],
                            temperature=kwargs.get('temperature', 0.9), model=kwargs.get('model'))
    matches = parse('$.choices[0].message.content').find(json_output)
    if len(matches) > 0:
        return {"output": {"text": matches[0].value}, "Success": True}
    else:
        return {}


def tione_chat_completion(**kwargs):
    chat = TioneClient()
    content = chat.ChatCompletion(content=kwargs.get('prompt'), model=kwargs.get('model')).to_json_string()
    json_obj = json.loads(content)
    matches = parse('$.Choices[0].Message.Content').find(json_obj)
    if len(matches) > 0:
        return {"output": {"text": matches[0].value}, "Success": True}
    else:
        return {}


class UnifiedSDK:
    def __init__(self):

        dwai.api_base_china = "https://dwai.shizhuang-inc.com"
        dwai.api_base_singapore = "https://openai.shizhuang-inc.com"

        self.route_map = {
            'alibaba': dwai_bailian_qa,
            'zhipu': zhipuai_chatglm_std,
            'huawei': pangu_completions,
            'minimax': mini_qa,
            'azure': azure_qa,
            'tencent': tione_chat_completion
        }

    def call(self, cloud, **kwargs):
        func = self.route_map.get(cloud)
        if func:
            return func(**kwargs)
        else:
            raise ValueError(f"Unknown cloud: {cloud}")


dwai.api_key = "dw-BBAa68XBJUqiIj6xUQcC0KREnqmt5mPKQ52wkylD-Tw"

if __name__ == '__main__':
    sdk = UnifiedSDK()
    print(">>>")
    #
    # # 测试微软
    # resp = sdk.call('azure', model="gpt-35-turbo-16k", prompt="你的参数量大概是多少？")
    # print(resp)
    #
    # # 测试mini
    # resp = sdk.call('minimax', model="abab5.5-chat", prompt="你的参数量大概是多少？")
    # print(resp)
    #
    # # 测试dwai
    # resp = sdk.call('alibaba', model="qwen-plus-v1", prompt="你的参数量大概是多少？")
    # print(resp)

    # 测试zhipuai
    resp = sdk.call('zhipu', model="chatglm_std", prompt="你的参数量大概是多少？", top_p=0.7, temperature=0.9)
    print(resp)
    #
    # # 测试pangu
    # resp = sdk.call('huawei', model="default", prompt="你的参数量大概是多少？", max_tokens=600, temperature=0.9)
    # print(resp)
    #
    # # 测试tione
    # resp = sdk.call('tencent', model="default", prompt="你的参数量大概是多少？")
    # print(resp)
