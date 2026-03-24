# Architecture (V1.0)

## 分层模块
- `src/ui`: 主窗口、控制器、控件
- `src/core`: 配置模型、项目管理、日志、异步任务
- `src/geometry`: 图像预处理
- `src/lbm`: D2Q9 BGK 求解器 + 渗透率接口
- `src/upscaling`: REV 分析模块
- `src/visualization`: 图像与曲线渲染
- `src/io`: 图像导入与结果导出

## 工作流
1. 新建/打开项目
2. 导入二维图像
3. 执行预处理并计算孔隙统计
4. 运行 LBM 获取速度场与收敛信息
5. 运行 REV 形成跨尺度统计与建议尺寸
6. 导出 figures/tables/configs/logs/reports
