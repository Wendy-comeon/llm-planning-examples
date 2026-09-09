"""模型调用接口示意，仅说明输入输出，不包含真实服务和提示词。"""
from typing import Any, Mapping


class ModelAPI:
    """由使用者自行实现调用方式。"""

    def generate(
        self,
        *,
        stage: str,
        input_data: Mapping[str, Any],
        prompt_outline: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """输入阶段名称、任务数据及提示词大纲，返回该阶段的结构化结果。

        各阶段输入输出见同目录的提示词大纲文件。
        """
        raise NotImplementedError("此处仅提供接口大纲，请自行实现模型调用。")
