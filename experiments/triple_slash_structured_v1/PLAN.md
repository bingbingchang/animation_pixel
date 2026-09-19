# Triple Slash Structured Reference Benchmark v1

状态：planned / not yet executed.

## 目的

在同一个三连斩任务、同一个帧数、同一个骨架输出合同下，比较“纯文字约束”与“明确结构参考”两条路线，记录整批成功率和人工介入次数。不是继续无限重生成，也不要求用户逐帧审批。

## 固定任务

- 16帧，4×4，row-major。
- skeleton_only。
- 固定相机，目标在screen-right。
- 三刀：screen upper-left→lower-right；upper-right→lower-left；low→high。
- grounded：无计划跳跃，连续运动至少一个可信支撑接触。
- 前脚身份按攻击阶段A→B→A。
- 固定weapon_hand_A肩—肘—腕拓扑；禁止镜像/换手。
- 身体转体、Head/Gaze、武器轨迹分离但耦合。
- 不允许服装、头发、FX、标题、箭头、UI。

配置来源：`configs/triple_slash_v2.json`和`docs/02_motion_spec_v2.md`。

## 比较条件

### A — text-only control

只给技能配置、骨架合同和必要的失败约束；不提供新制作的姿态结构参考。

### B — explicit structure reference

在A相同文本条件下，额外提供一份有永久肢体ID、头部前向、支撑接触、grip socket和关键语义节点的结构参考。结构参考不含角色外观和FX。

关键原则：B只增加“结构参考”这一变量，其他提示、尺寸、输出合同和后处理尽量保持一致。

## 小规模预算

每个条件最多3个初始batch；每个batch最多2次语义段定向修复。达到限制即FAIL/UNKNOWN并停止，不追加“再试一次直到好看”。

如果当前平台无法固定随机种子，则记录为seed=unknown，不声称严格随机对照。

## Batch级硬闸门

任一关键错误则该batch不算成功：

1. 输出类型漂移：不是纯骨架4×4动作表。
2. 拓扑错误：持剑手换肩链、肢体复制/消失、无记录镜像。
3. 目标/头部错误：语义节点明显失去screen-right目标；若无可判读前向标记则UNKNOWN而非PASS。
4. 步法错误：没有实际前后脚身份交换、passing step瞬移或无意义双脚腾空。
5. weapon path错误：三刀投影方向和规定不符，或回收被读成额外攻击。
6. 尺度/裁切错误：明显整体scale popping、武器/脚被切。
7. 过渡断裂：第一→第二或第二→第三缺少可读的支撑/转体/回收因果。

## 软评分（不替代硬闸门）

- silhouette readability
- heroic/game-action appeal
- impact contrast / compression-release
- transition elegance
- perceived explosiveness

每项只用低/中/高或简短说明，避免伪精确总分。

## 人工介入计数

一次介入 = 人对一个batch指出需要重算的“语义段/通道”并触发新的生成/编辑调用。

不把单纯浏览、程序切帧、哈希校验算作介入。

记录：
- initial_generation_calls
- targeted_repair_calls
- whole_batch_regeneration_calls
- human_interventions
- final_state: PASS / FAIL / UNKNOWN

## 成功率

`batch_success_rate = hard_PASS_batches / attempted_initial_batches`

小样本只报告原始计数（例如2/3），不外推总体概率，不做“提升xx%”宣传。

## 人工审查单位

默认审查完整GIF/contact sheet和语义段，不要求用户逐帧签字。若自动/模型判断无法确定头向、脚身份或遮挡，标记UNKNOWN；只在影响下一决策时让人看相应语义段。

## 结果文件

每次运行建立不可覆盖的run目录：

```
runs/<condition>/<run_id>/
  request.json
  actual_prompt_or_unknown.txt
  references.json
  output_original.*
  preview.gif
  contact_sheet.*
  qa.json
  interventions.jsonl
```

实际提示词不可得时写unknown，不用后来重构prompt冒充。

## 停止条件

- A/B各达到3个初始batch；或
- 权限/额度/平台能力阻塞；或
- 连续出现同一系统性硬失败，说明应先改结构参考/工具，不继续烧生成次数。

## 预注册结论边界

本实验只能回答：在这个三连斩和当前工具环境下，明确结构参考是否让batch更常通过硬闸门、是否减少定向人工介入。

它不能证明通用人体运动学正确、不能证明模型对所有技能都稳定，也不能用生成器自己的自评替代视觉/结构证据。
