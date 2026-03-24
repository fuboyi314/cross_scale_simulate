# 基于LBM的跨尺度多孔介质渗流模拟平台（V1.0）

## 1. 项目简介
本项目是用于软件著作权申请准备的科研软件工程，实现二维多孔介质导入、预处理、LBM 渗流模拟、等效渗透率估算、REV 跨尺度分析、可视化与导出。

## 2. 技术栈
- Python 3.10+
- PySide6
- NumPy
- Matplotlib
- imageio

## 3. 目录结构
- `app.py`
- `requirements.txt`
- `AGENTS.md`
- `src/ui`
- `src/core`
- `src/geometry`
- `src/lbm`
- `src/upscaling`
- `src/visualization`
- `src/io`
- `docs`
- `tests`

## 4. 安装与运行
```bash
pip install -r requirements.txt
python app.py
```

## 5. 测试
```bash
pytest -q
```

## 6. 当前实现能力
- 项目新建/打开/保存
- 二维图像导入与预处理（ROI、阈值、反转、小区域过滤、小孔填充）
- D2Q9 BGK 基础求解
- lattice-unit 渗透率估算接口
- REV 基础分析与建议尺寸
- 结果可视化（原图、二值图、速度场、REV 曲线）
- 结构化导出（PNG/CSV/JSON/报告）

## 7. 当前限制
- 物理单位换算仍为接口层（需后续标定）
- 高阶边界条件、三维、多相等不在 V1.0 范围内
