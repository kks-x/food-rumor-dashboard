# 数据规范 DATA_SPEC.md
> 所有组员产出分析结果后，填入 rumo1/2/3.json，放入 dataSets
## 字段清单
### A（传播时间线）
time_series: [{"date":"YYYY-MM-DD","count":数字,"interact":数字}]
time_phase: [{"phase":"爆发期","start":"日期","end":"日期","desc":"说明"}]

### B（传播网络）
network_nodes: [{"uid":"id","username":"昵称","weight":权重,"x":坐标x,"y":坐标y}]
network_edges: [{"source":"uid","target":"uid","x1":数字,"y1":数字,"x2":数字,"y2":数字}]
network_summary: {"max_degree":数值,"core_user_count":数值}

### C（情感演化）
sentiment_time: [{"date":"日期","neg":负面数量,"neu":中性,"pos":正面}]
sentiment_word_list: ["词1","词2"]

### D（内容地域）
hot_word_list: ["词1"]
word_time_series: [{"date":"日期","word":"关键词","cnt":词频}]
region_data: [{"province":"省份","count":发帖数}]

### 公共字段
event_list, quality
