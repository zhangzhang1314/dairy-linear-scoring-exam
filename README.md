# 奶牛体型线性评定考试

一个无需数据库、无需账号密码的 Streamlit 在线考试程序。

## 功能

- 选择题、填空题、判断题三种题型
- 按 14 个体型性状的 1–9 分测量值对照表随机组卷
- 自动判分、逐题反馈、正确答案与解析
- 支持考前查看完整评分对照表
- 不收集姓名，不保存任何答题记录

## 本地启动

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run streamlit_app.py
```

浏览器打开 `http://localhost:8501`。

## 部署

入口文件为 `streamlit_app.py`，可直接部署到 Streamlit Community Cloud。
