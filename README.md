# 大模型辅助的复杂任务规划：任务分解、结构表示与任务分配

本仓库选取 **6 个真实家具装配任务**，展示任务分解、任务分解矩阵（TDM）、多机器人分配及冲突消解结果，并提供主要实验的汇总统计。

## 研究内容

- **大模型多智能体任务分解：**设计任务分类、任务分级和结构生成三个LLM智能体，结合示例检索与校验反馈，生成子任务及其依赖关系。
- **任务结构表示与推理增强：**提出任务分解矩阵（TDM），设计矩阵编码与图重构算法，并从理论上建立入树型任务图同构类与矩阵等价类的一一对应关系，保证对该类任务图的无损表示。
- **多机器人任务分配与冲突消解：**利用任务结构表示引导大模型预测任务属性、分配机器人，再通过约束检验定位并修复分配冲突。

## 家具模型与任务样例

| 椅子 | 桌子 | 书柜 | 柜体 | 置物架 | 床架 |
| --- | --- | --- | --- | --- | --- |
| ![椅子模型](images/01_chair.png) | ![桌子模型](images/02_table.png) | ![书柜模型](images/03_bookcase.png) | ![柜体模型](images/04_cabinet.png) | ![置物架模型](images/05_shelf.png) | ![床架模型](images/06_bed.png) |

图片为原家具环境中的模型展示图。下表中的模型链接提供原始模型文件及规划结果。

| 样例 | 子任务数 | 模型 | 任务结构 | TDM | 初始分配 | 最终分配 | 修复记录 |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| 椅子 | 3 | [模型](models/chair_ingolf_0650.xml) | [结构](examples/01_chair/task.json) | [矩阵](examples/01_chair/tdm.csv) | [分配](examples/01_chair/allocation_initial.csv) | [分配](examples/01_chair/allocation_final.csv) | [结果](examples/01_chair/repair_result.json) |
| 桌子 | 4 | [模型](models/table_bjorkudden_0207.xml) | [结构](examples/02_table/task.json) | [矩阵](examples/02_table/tdm.csv) | [分配](examples/02_table/allocation_initial.csv) | [分配](examples/02_table/allocation_final.csv) | [结果](examples/02_table/repair_result.json) |
| 书柜 | 5 | [模型](models/bookcase_besta_0172.xml) | [结构](examples/03_bookcase/task.json) | [矩阵](examples/03_bookcase/tdm.csv) | [分配](examples/03_bookcase/allocation_initial.csv) | [分配](examples/03_bookcase/allocation_final.csv) | [结果](examples/03_bookcase/repair_result.json) |
| 柜体 | 7 | [模型](models/cabinet_akurum_0014.xml) | [结构](examples/04_cabinet/task.json) | [矩阵](examples/04_cabinet/tdm.csv) | [分配](examples/04_cabinet/allocation_initial.csv) | [分配](examples/04_cabinet/allocation_final.csv) | [结果](examples/04_cabinet/repair_result.json) |
| 置物架 | 5 | [模型](models/shelf_lillagen_0927.xml) | [结构](examples/05_shelf/task.json) | [矩阵](examples/05_shelf/tdm.csv) | [分配](examples/05_shelf/allocation_initial.csv) | [分配](examples/05_shelf/allocation_final.csv) | [结果](examples/05_shelf/repair_result.json) |
| 床架 | 9 | [模型](models/bed_dalselv_0270.xml) | [结构](examples/06_bed/task.json) | [矩阵](examples/06_bed/tdm.csv) | [分配](examples/06_bed/allocation_initial.csv) | [分配](examples/06_bed/allocation_final.csv) | [结果](examples/06_bed/repair_result.json) |

## 主要实验结果

| 实验 | 试验范围 | 成功次数 / 试验次数 | 成功率 |
| --- | --- | ---: | ---: |
| 独立任务分解 | 47 项任务，各重复 5 次 | 199 / 235 | **84.68%** |
| 表示方法对照：不使用 TDM | 60 项任务，各重复 5 次 | 133 / 300 | 44.33% |
| 表示方法对照：使用 TDM | 60 项任务，各重复 5 次 | 244 / 300 | **81.33%** |
| 独立任务分配 | 60 项任务、5 种模型，各重复 5 次 | 1484 / 1500 | **98.93%** |
| 完整任务规划 | 47 项任务，各重复 5 次 | 197 / 235 | **83.83%** |

- 表示方法对照统计的是反馈和修复之前的初始候选分配可行率，使用 TDM 后提高 **37 个百分点**。
- 独立任务分配以人工确认的任务结构为输入，统计包含反馈与修复的流程结果。
- 完整任务规划使用实际生成的任务分解结果，任务分解与最终分配均成功才计为成功；它与独立任务分配的实验条件不同。

## 提示词与模型接口大纲

[提示词大纲](interfaces/prompt_outline.json) 仅列出任务分类、分级、结构生成、属性预测与分配、检验反馈各阶段的输入输出；[模型调用接口](interfaces/model_api.py) 仅给出调用签名；[配置示例](interfaces/model_config.example.json) 中的地址、密钥与模型名称均为空。

这些接口文件用于说明各阶段如何衔接，未实现真实模型调用。使用本仓库查看矩阵、模型和结果无需密钥；公开文件不包含真实提示词、示例检索库或在线服务配置。

## 来源与公开范围

家具模型和图片来自 [IKEA Furniture Assembly Environment](https://github.com/clvrai/furniture)，随附[原项目许可](third_party/furniture-LICENSE.txt)。任务分解、矩阵与分配结果来自本研究筛选的实验记录。

本仓库用于展示研究内容和部分真实结果。完整实验数据、未发表工作的核心实现、真实提示词、内部日志与后续研究资料暂不公开。
