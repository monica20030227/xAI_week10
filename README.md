# 🚦 模型可靠性分析 Dashboard（xAI 第十週）

Dashboard連結：https://xaiweek10-mafyqdyuycsn2xtmappc2mq.streamlit.app/

本專案實作一個基於 xAI 第十週概念的**模型可靠性診斷系統（Reliability Analysis）**，重點不在於提升模型準確率，而在於分析：

- 模型什麼時候會錯？
- 錯誤是否集中在特定情境？
- 模型的 confidence 是否可信？
- 是否存在 high-confidence error？

---

## 📌 專案目標

本專案模擬一個「車輛接近路口時的決策模型」，預測行為：

- `accelerate`（加速）
- `maintain`（維持速度）
- `decelerate`（減速）

並進一步分析模型的：

- 預測結果（prediction）
- 信心分數（confidence）
- 錯誤類型（error type）
- 子群表現（subgroup performance）

---

## 🧠 核心觀念

本專案對應以下 xAI 概念：

- **Accuracy ≠ Reliability（準確率不等於可靠性）**
- **Confidence ≠ Correctness（信心不代表正確）**
- Calibration（信心是否可信）
- High-confidence error（高信心錯誤）
- Error slicing（錯誤切片分析）
- Subgroup failure（子群失效）

---

## ⚙️ 方法說明

### 1️⃣ 模擬模型（Vibe Coding）

本專案採用「模擬模型（synthetic model）」：

- 隨機生成交通情境資料
- 使用規則 + 隨機方式模擬模型輸出
- 在特定條件（如高車流）刻意加入錯誤

👉 目的：用來分析模型「錯誤行為與可靠性」，而非訓練高準確模型

---

### 2️⃣ 輸入特徵（Input Features）

| 欄位 | 說明 |
|------|------|
| car_type | 車種（ICE / EV / HEV） |
| traffic_density | 車流密度（low / medium / high） |
| distance_to_light | 距離號誌距離 |
| signal_color | 號誌顏色 |
| speed | 車速 |
| waiting_time | 等待時間 |
| co2 | 排放量 |

---

### 3️⃣ 模型輸出（Outputs）

| 欄位 | 說明 |
|------|------|
| model_output | 模型預測行為 |
| confidence | 信心分數（0~1） |
| true_label | 正確答案 |
| error_type | correct / low-confidence error / high-confidence error |

---

## 📊 Dashboard 功能

本專案使用 **Streamlit** 建立互動式 Dashboard：

### ✔️ 整體指標（Performance）
- Accuracy（準確率）
- Error Rate（錯誤率）
- 平均 Confidence
- High-confidence Error Rate

---

### ✔️ Confidence 分布
- 顯示模型信心分布（Histogram）
- 判斷是否過度自信（overconfidence）

---

### ✔️ Error Slicing（錯誤切片）
- 依照 traffic density 分析錯誤率
- 找出模型在哪些情境失效

---

### ✔️ Subgroup Metrics（子群分析）
- 不同車種（ICE / EV / HEV）表現比較
- 找出 subgroup failure

---

### ✔️ High-confidence Error
- 顯示最危險的錯誤案例
- 提供完整 log（speed、co2、distance 等）

---

### ✔️ 自動報告生成
- 自動輸出可直接使用的分析文字（可貼報告）

---

## 🚀 如何執行

### 1️⃣ 安裝套件

```bash
pip install streamlit pandas matplotlib
