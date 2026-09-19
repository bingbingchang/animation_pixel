# 三连斩案例 001：不要重复把失败当成完成

日期：2026-09-19。范围：本会话相关讨论和图像；不含其他个人聊天。

## 当前需求

两次交叉下劈（左上→右下、右上→左下）接上挑；攻击目标仍在屏幕右侧；16帧输出；真实有意图的换步、转体、重心变化；关键姿势要酷、利落、有游戏美感；默认至少一脚接地。不是信息图，不在骨架阶段套角色。

早期组合曾是横斩→上挑→下劈。本案例中的G01–G10属于早期组合，不能误当成当前需求的合格样本。

## 版本索引

原始字节在完整ZIP中；首次GitHub文档提交暂只含少量诊断预览，原图远端状态见`assets/manifest.json`及后续上传回执。版本号G01–G15是本次归档新建的稳定ID，不等于聊天里反复使用的V2/V3/V4。

| ID | 阶段 | 记录状态 | 完整原图路径 |
|---|---|---|---|
| G01 | `initial_colored` | `upper_body_only` | `assets/originals/G01_initial_colored.png` |
| G02 | `full_body_attempt` | `insufficient_leg_support` | `assets/originals/G02_full_body_attempt.png` |
| G03 | `explosive_attempt` | `irregular_grid` | `assets/originals/G03_explosive_attempt.png` |
| G04 | `trajectory_attempt` | `trajectory_and_footwork_unverified` | `assets/originals/G04_trajectory_attempt.png` |
| G05 | `reference_informed_attempt` | `footwork_unresolved` | `assets/originals/G05_reference_informed_attempt.png` |
| G06 | `skeleton_v1` | `user_reported_timing_success_later_footwork_rejected` | `assets/originals/G06_skeleton_v1.png` |
| G07 | `character_transfer` | `user_reported_preview_success_not_motion_approval` | `assets/originals/G07_character_transfer.png` |
| G08 | `smear_enhancement` | `intermediate_not_final` | `assets/originals/G08_smear_enhancement.png` |
| G09 | `fx_showcase` | `user_reported_visual_approval_not_engine_approval` | `assets/originals/G09_fx_showcase.png` |
| G10 | `claimed_game_export` | `regenerated_not_lossless_export` | `assets/originals/G10_claimed_game_export.png` |
| G11 | `skeleton_v2` | `lead_leg_exchange_unproven` | `assets/originals/G11_skeleton_v2.png` |
| G12 | `v3_attempt` | `wrong_output_infographic_and_character` | `assets/originals/G12_v3_attempt.png` |
| G13 | `skeleton_v3` | `awkward_transition_and_missing_turn` | `assets/originals/G13_skeleton_v3.png` |
| G14 | `heroic_pose_attempt` | `better_appeal_but_wrong_output_and_details` | `assets/originals/G14_heroic_pose_attempt.png` |
| G15 | `rule_driven_skeleton_attempt` | `user_reported_head_facing_error_frames_09_10` | `assets/originals/G15_rule_driven_skeleton_attempt.png` |

## 正向经验必须限定范围

用户实际制作并观看GIF后，对G06骨架、G07套皮、G09最终效果给过积极反馈。这支持“节奏和视觉有一定效果”，不证明我们执行过运动学测量，也不证明换腿/头朝向正确。用户制作的那些GIF未附在会话中，本档案不伪造或重建后冒称原预览。

## 必須保留的负面样本

G01：上身挥剑，下肢重复。G03：分格错误。G10：把重生图当作导出。G11：下半身虽然变化但交替未被证实。G12：纯骨架任务变成彩色说明海报。G13：换步与转体衔接不成立。G14：美感提升，但回到带服装/标题的说明图。G15：用户指出F9–F10头朝向错误。

后一个版本不能只修最后被指出的问题，而必须回归已有故障列表。现有无面部标记人偶对头转向的自动识别证据不足，状态应为UNKNOWN/用户指出失败，而不是伪造精确头部角度。

## 关于参考素材

R00：用户剑士原图。R01–R05：用户拳皇GIF和本会话派生研究图。R06–R08：用户DNF收尾姿态截图。仅作为研究来源，不授权作为本项目原创商用角色。B站链接保留在讨论档案中；没有完整审阅视频流的证据，不写“已逐帧看完”。

## 下一次实验的最小增量

先冻结角色拓扑、视角、地面和攻击方向；生成带可见头部朝向标记的人偶参考。保持骨架阶段干净。按整段动画评估，在预算内修复语义段；不让用户重复逐帧审批。导出只处理既有像素，不再生图。
