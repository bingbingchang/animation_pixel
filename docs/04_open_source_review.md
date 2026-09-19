# Image2相关开源项目研究（核查日：2026-09-19）

用户只描述了“利用image2生图、很火的开源项目”，尚未给出确切项目名。因此下面保留候选，不把其中一个说成用户已经确认的目标。研究只读公开文档，不安装、不运行付费调用、不复制整套图库。

## 1 候选与边界

| 项目 | 本次读到什么 | 对本项目的作用 | 不应夸大的能力 |
|---|---|---|---|
| [EvoLinkAI/awesome-gpt-image-2-API-and-Prompts](https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts) | 主页约17.2k stars；CONTRIBUTING要求完整原prompt、作者、来源、输出、参考输入；展示图不能冒充可复现prompt案例 | 建立有来源的案例库和回归台账 | 不是自动近战运动求解器，也不以“高星”证明动作质量 |
| [YouMind-OpenLab/awesome-gpt-image-2](https://github.com/YouMind-OpenLab/awesome-gpt-image-2) | 主页约9.9k stars；场景/画风分类、预览、原prompt、作者/来源、参数替换 | 按任务检索，不把整段历史与全图库都塞进提示词 | README中的像素级一致性/直接商用等描述是项目表述，不是本项目已验证保证 |
| [wuyoscar/GPT-Image2-Skill](https://github.com/wuyoscar/GPT-Image2-Skill) | 主页约5.5k stars；图库+Agent Skill+CLI；分类生成/编辑/蒙版/多参考，preflight、参考与编辑约束、最小相关上下文、错误回报 | 最值得借鉴执行层合同：输入角色、编辑范围、模式、成本边界和结果记录 | CLI与Skill不是开源图像模型权重；它没有证明三连斩全身一致性 |
| [WU-HAOTIAN34/2dimg2motion](https://github.com/WU-HAOTIAN34/2dimg2motion) | 读取SKILL.md：角色身份锁、关键锚点、同段中间帧、清单、预览、失败库、结构验证不能代替视觉验证 | 更接近像素动作；参考其“知识先读、冻结锚点、保留证据”的思想 | 不照抄固定14帧、固定屏幕侧持剑、删中间稿等与本项目冲突的规定 |

Star是访问当时近似值，会变化；它不能表示哪个项目就是用户所指，也不是性能指标。

## 2 我们立即采用的做法

### 证据链优先于漂亮结果

借鉴EvoLink的贡献规范：保存需求/原始提示词、参考输入、输出、作者或来源、验证记录。若最终提交给图像工具的prompt不可得，标unknown；后写的提示词只能叫重构版。

本项目更进一步保留失败输出、用户反馈、故障标签和状态撤销记录。某图先被认可“有力量”，后被发现腿不对，两条历史都保留。

来源：[CONTRIBUTING.md](https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts/blob/main/CONTRIBUTING.md)，本次读取blob `783c00ad149ac4d9a38fc4bead46d79cfc3b9191`。

### 参考图要分工，编辑要有不变量

借鉴wuyoscar：先区分新生成、参考编辑、蒙版编辑、多参考，不把它们当成同一请求。我们划分identity/motion/style/layout参考，并写出允许改变和禁止改变的内容。

“换角色皮肤”只改外观；“补刀光”只改FX；“导出”只做程序处理。即便使用编辑接口，未编辑区域是否不变仍要实际检查。

来源：[SKILL.md](https://github.com/wuyoscar/GPT-Image2-Skill/blob/main/skills/gpt-image/SKILL.md)，blob `a622dca6973cc99835b520afb06f3eca9b028609`；[CONTRIBUTING.md](https://github.com/wuyoscar/GPT-Image2-Skill/blob/main/CONTRIBUTING.md)，blob `08fc8225d051e06856b89e067d15c4a79f470192`。研究时仓库tree为`05cb1130bba29e0fc028220376280a2e934a8041`。

### 少量相关规则，而不是全历史堆叠

借鉴YouMind的分类和wuyoscar的最小参考切片。请求骨架时只加载运动与骨架规范，不带服装/FX/信息图示例。按技能标签检索失败库，再生成短而明确的任务合同。

来源：[YouMind 中文README](https://github.com/YouMind-OpenLab/awesome-gpt-image-2/blob/main/README_zh.md)、上述wuyoscar SKILL。

### 冻结结构锚点，按语义段修复

借鉴2dimg2motion的关键帧与中间段分离。我们不要求用户逐帧审；系统保留边界锚点，对有问题的过渡段限次修复，再整套回归。

来源：[2dimg2motion/SKILL.md](https://github.com/WU-HAOTIAN34/2dimg2motion/blob/main/SKILL.md)。它是外部参考，不是本项目已安装的Skill。

## 3 必须修正后再借鉴

- **屏幕左手永久持剑**：转体和越过身体中线时会错误限制姿态。改成同一解剖/拓扑ID持剑，屏幕位置只是投影。
- **永远头朝右**：不能用不合理颈部扭转实现。目标意识与头/胸相对运动要共同约束。
- **固定14帧并首尾同图**：不是本项目16帧连招的必需条件；恢复可以衔接下个动作，不必硬循环。
- **删掉中间失败图**：与用户“吸取教训”的目标相反。本项目研究档案保留失败，只让release目录保持干净。
- **自动视觉QA已可靠**：未找到能凭这些无标记骨架稳定识别所有头朝向/足接触的本项目证据；保留UNKNOWN和抽样审查。
- **模型/API能力宣传**：只把OpenAI官方当前文档当作产品能力依据。没有验证第三方服务价格、密钥方案，也没有授权替用户调用。

官方核查入口：[Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)。本次不据第三方README写死生产模型ID、价格或支持参数。

## 4 具体实施建议

第一轮先做不消耗生图额度的实验记录器和导出校验。然后比较两条生产路线：

A：参数化prompt + 真实参考 + 冻结锚点的生成/编辑。
B：可渲染的带身份人偶/2.5D或3D骨架提供硬结构参考，再由图像模型完成风格化。

两条路线使用同一组三连斩、相同预算和输出合同，记录失败率、人工介入次数、修复次数与耗时。路线B更易形成可检验的结构约束是工程判断，不是已取得的实验结果。

**本次没有复制或运行这些仓库的代码；借鉴的是公开设计，外部仓库的许可证不自动适用于它们收集的全部图片，更不自动适用于用户提供的游戏参考。**
