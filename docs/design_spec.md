# design_spec.md

## 架构分层
- `src/ui`: Qt 主界面与控制器
- `src/core`: 配置模型、项目管理、日志、任务执行
- `src/geometry`: 图像预处理
- `src/lbm`: D2Q9 求解器与渗透率接口
- `src/upscaling`: REV 分析
- `src/io`: 图像读写与结果导出
- `src/visualization`: 图像与曲线渲染

## 关键设计
- GUI 与算法解耦，控制器负责调用链组织。
- 长任务通过 `TaskRunner` 异步执行，避免界面阻塞。
- 项目配置统一由 `ProjectConfig` 序列化到 JSON。
