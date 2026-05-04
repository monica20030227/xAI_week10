import random
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reliability Dashboard", layout="wide")

# =========================
# 1. 模擬模型
# =========================

def simulate_model(row):
    if row["signal_color"] == "red" and row["distance_to_light"] < 35:
        true_label = "decelerate"
    elif row["signal_color"] == "yellow" and row["distance_to_light"] < 25:
        true_label = "decelerate"
    elif row["signal_color"] == "green":
        true_label = "maintain"
    else:
        true_label = "maintain"

    risky_case = (
        row["traffic_density"] == "high"
        and row["distance_to_light"] < 40
    )

    if risky_case and random.random() < 0.45:
        wrong_actions = [
            a for a in ["accelerate", "maintain", "decelerate"]
            if a != true_label
        ]
        model_output = random.choice(wrong_actions)
        confidence = round(random.uniform(0.85, 0.98), 2)
    else:
        model_output = true_label
        confidence = round(random.uniform(0.60, 0.95), 2)

    if model_output == true_label:
        error_type = "correct"
    elif confidence >= 0.85:
        error_type = "high-confidence error"
    else:
        error_type = "low-confidence error"

    return model_output, confidence, true_label, error_type


# =========================
# 2. 產生資料
# =========================

@st.cache_data
def generate_data(n=120, seed=42):
    random.seed(seed)
    data = []

    for i in range(n):
        row = {
            "sample_id": i + 1,
            "car_type": random.choice(["ICE", "EV", "HEV"]),
            "traffic_density": random.choice(["low", "medium", "high"]),
            "distance_to_light": random.randint(5, 100),
            "signal_color": random.choice(["red", "yellow", "green"]),
            "speed": round(random.uniform(5, 14), 2),
            "waiting_time": random.randint(0, 20),
            "co2": round(random.uniform(70, 160), 2)
        }

        model_output, confidence, true_label, error_type = simulate_model(row)

        row["model_output"] = model_output
        row["confidence"] = confidence
        row["true_label"] = true_label
        row["error_type"] = error_type

        data.append(row)

    return pd.DataFrame(data)


# =========================
# 3. Sidebar
# =========================

st.sidebar.title("設定")

sample_size = st.sidebar.slider(
    "模擬資料筆數",
    min_value=50,
    max_value=500,
    value=120,
    step=10
)

seed = st.sidebar.number_input(
    "Random Seed",
    min_value=1,
    max_value=9999,
    value=42
)

df = generate_data(sample_size, seed)

selected_car = st.sidebar.multiselect(
    "選擇車種",
    options=df["car_type"].unique(),
    default=list(df["car_type"].unique())
)

selected_density = st.sidebar.multiselect(
    "選擇車流密度",
    options=df["traffic_density"].unique(),
    default=list(df["traffic_density"].unique())
)

filtered_df = df[
    (df["car_type"].isin(selected_car)) &
    (df["traffic_density"].isin(selected_density))
]


# =========================
# 4. 標題
# =========================

st.title("Reliability Dashboard")
st.caption("模型可靠性診斷：Performance、Confidence Distribution、Error Slicing、Subgroup Metrics、High-confidence Errors")


# =========================
# 5. Overall Metrics
# =========================

accuracy = (filtered_df["model_output"] == filtered_df["true_label"]).mean()
error_rate = 1 - accuracy
avg_confidence = filtered_df["confidence"].mean()
high_conf_error_rate = (
    filtered_df["error_type"] == "high-confidence error"
).mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Accuracy", f"{accuracy:.3f}")
col2.metric("Error Rate", f"{error_rate:.3f}")
col3.metric("Average Confidence", f"{avg_confidence:.3f}")
col4.metric("High-confidence Error Rate", f"{high_conf_error_rate:.3f}")


# =========================
# 6. 原始資料
# =========================

st.subheader("模型輸出資料")

st.dataframe(
    filtered_df,
    use_container_width=True
)

csv = filtered_df.to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="下載 reliability_data.csv",
    data=csv,
    file_name="reliability_data.csv",
    mime="text/csv"
)


# =========================
# 7. Confidence Distribution
# =========================

st.subheader("Confidence Distribution")

fig1, ax1 = plt.subplots(figsize=(7, 4))
ax1.hist(filtered_df["confidence"], bins=10)
ax1.set_xlabel("Confidence")
ax1.set_ylabel("Count")
ax1.set_title("Confidence Distribution")
st.pyplot(fig1)


# =========================
# 8. Error Slicing
# =========================

st.subheader("Error Slicing")

error_by_density = filtered_df.groupby("traffic_density").apply(
    lambda x: pd.Series({
        "sample_count": len(x),
        "error_rate": (x["model_output"] != x["true_label"]).mean(),
        "high_conf_error_count": (
            x["error_type"] == "high-confidence error"
        ).sum()
    })
).reset_index()

st.write("依照 traffic density 切片：")
st.dataframe(error_by_density, use_container_width=True)

fig2, ax2 = plt.subplots(figsize=(7, 4))
ax2.bar(error_by_density["traffic_density"], error_by_density["error_rate"])
ax2.set_xlabel("Traffic Density")
ax2.set_ylabel("Error Rate")
ax2.set_title("Error Rate by Traffic Density")
ax2.set_ylim(0, 1)
st.pyplot(fig2)


# =========================
# 9. Subgroup Metrics
# =========================

st.subheader("Subgroup Metrics")

subgroup_metrics = filtered_df.groupby("car_type").apply(
    lambda x: pd.Series({
        "sample_count": len(x),
        "accuracy": (x["model_output"] == x["true_label"]).mean(),
        "avg_confidence": x["confidence"].mean(),
        "error_rate": (x["model_output"] != x["true_label"]).mean(),
        "high_conf_error_count": (
            x["error_type"] == "high-confidence error"
        ).sum()
    })
).reset_index()

st.write("依照車種切片：")
st.dataframe(subgroup_metrics, use_container_width=True)

fig3, ax3 = plt.subplots(figsize=(7, 4))
ax3.bar(subgroup_metrics["car_type"], subgroup_metrics["accuracy"])
ax3.set_xlabel("Car Type")
ax3.set_ylabel("Accuracy")
ax3.set_title("Accuracy by Car Type")
ax3.set_ylim(0, 1)
st.pyplot(fig3)


# =========================
# 10. High-confidence Errors
# =========================

st.subheader("High-confidence Error Cases")

high_conf_errors = filtered_df[
    filtered_df["error_type"] == "high-confidence error"
]

if len(high_conf_errors) == 0:
    st.info("目前沒有 high-confidence error。")
else:
    st.dataframe(
        high_conf_errors.head(10),
        use_container_width=True
    )

    st.markdown("### 可放進報告的 3 個案例")

    for idx, row in high_conf_errors.head(3).iterrows():
        st.markdown(f"""
        **Case {row["sample_id"]}**

        - 模型輸出：{row["model_output"]}
        - Confidence：{row["confidence"]}
        - 正確答案：{row["true_label"]}
        - 錯誤類型：{row["error_type"]}
        - 車種：{row["car_type"]}
        - 車流密度：{row["traffic_density"]}
        - 距離號誌：{row["distance_to_light"]} m
        - 號誌顏色：{row["signal_color"]}
        - 可觀測 log：speed={row["speed"]}, waiting_time={row["waiting_time"]}, co2={row["co2"]}
        """)


# =========================
# 11. 自動產生報告文字
# =========================

st.subheader("自動產生報告摘要")

if len(filtered_df) > 0:
    worst_density = error_by_density.sort_values(
        "error_rate", ascending=False
    ).iloc[0]

    worst_car = subgroup_metrics.sort_values(
        "accuracy", ascending=True
    ).iloc[0]

    report = f"""
本次實作使用一個模擬車速控制模型，任務是根據車種、車流密度、距離號誌距離與號誌顏色，
預測車輛在路口前應採取的行為，包括 accelerate、maintain、decelerate。

整體模型 accuracy 為 {accuracy:.3f}，平均 confidence 為 {avg_confidence:.3f}。
雖然模型整體表現尚可，但 high-confidence error rate 為 {high_conf_error_rate:.3f}，
代表模型仍可能在錯誤預測時給出很高的信心分數。

Error slicing 結果顯示，錯誤率最高的交通情境為 {worst_density["traffic_density"]}，
其 error rate 為 {worst_density["error_rate"]:.3f}。
這表示模型在特定交通密度下較容易失效，不能只看 overall accuracy。

Subgroup metrics 顯示，表現最差的車種為 {worst_car["car_type"]}，
其 accuracy 為 {worst_car["accuracy"]:.3f}。
這代表不同車種之間可能存在 subgroup performance gap。

可能錯誤來源包含：
1. 資料層錯誤：高車流或接近路口的訓練樣本不足。
2. 模型層錯誤：模型 confidence 未校準，導致 overconfidence。

修正策略包含：
1. 增加高車流、黃燈、紅燈與接近路口情境的訓練資料。
2. 使用 temperature scaling 或 ensemble 方法校準 confidence。
3. 在低可靠或高風險情境加入人工覆核或 reject option。

若此錯誤出現在真實交通情境中，會造成高風險。
因為 high-confidence error 可能讓系統在錯誤決策時仍看起來很可靠，
例如在應該減速時卻加速，可能導致闖紅燈、追撞或能源浪費。
"""

    st.text_area("報告文字", report, height=450)