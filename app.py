import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib import font_manager
from itertools import combinations

# 加载本地字体文件
font_path = "fonts/SimHei.ttf"  # 确保字体文件路径正确
font = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.sans-serif'] = [font.get_name()]
plt.rcParams['axes.unicode_minus'] = False

# 生肖的正确顺序
zodiac_order = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

# 更新数据的功能
def update_csv():
    # 添加User-Agent请求头，模拟来自浏览器的请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # 从网页读取HTML内容
    url = 'https://333220a.ad2e9u6zhrfxhui.top:16688/kj/3/2024.html'  # 替换为实际的网页URL
    response = requests.get(url, headers=headers)

    # 检查是否成功获取页面内容
    if response.status_code == 200:
        html_content = response.content.decode('utf-8')
    else:
        st.error(f"无法获取网页内容，状态码: {response.status_code}")
        return None

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到所有的开奖记录容器
    kj_boxes = soup.find_all('div', class_='kj-box')

    # 初始化结果列表
    results = []

    # 遍历每个开奖记录容器
    for kj_box in kj_boxes:
        # 获取期数信息
        period_info = kj_box.find_previous_sibling('div', class_='kj-tit').text
        period = period_info.split("第")[1].split("期")[0].strip()
        
        # 获取每个号码和对应的生肖信息
        numbers = kj_box.find_all('dt', class_=['ball-green', 'ball-blue', 'ball-red'])
        
        # 初始化当前期的号码和生肖列表
        period_numbers = []
        period_zodiacs = []
        
        # 遍历每个号码并获取对应的生肖信息
        for number in numbers:
            number_text = number.text.strip()
            period_numbers.append(number_text)
            
            # 获取号码元素的下一个兄弟元素，该元素应包含生肖信息
            zodiac_element = number.find_next('dd')
            zodiac_text = zodiac_element.text.strip().split('/')[0]
            period_zodiacs.append(zodiac_text)
        
        # 检查提取的数据长度是否正确
        if len(period_numbers) == 7 and len(period_zodiacs) == 7:
            # 将结果添加到列表中
            results.append([period] + period_numbers + period_zodiacs)
        else:
            st.warning(f"数据提取错误: 期数 {period} 有 {len(period_numbers)} 个号码和 {len(period_zodiacs)} 个生肖")

    # 创建DataFrame
    columns = ['期数'] + [f'号码{i}' for i in range(1, 8)] + [f'生肖{i}' for i in range(1, 8)]
    df = pd.DataFrame(results, columns=columns)

    # 保存为CSV文件
    df.to_csv('六合彩开奖记录.csv', index=False, encoding='utf-8-sig')

    st.success("数据更新完成并保存为六合彩开奖记录.csv")
    return df

# Streamlit应用程序
st.title("澳门六合彩-分析")

# 更新数据按钮
if st.sidebar.button("更新数据"):
    df = update_csv()
else:
    # 读取CSV文件
    df = pd.read_csv('六合彩开奖记录.csv', encoding='utf-8-sig')

    if df is not None:
        # 选择数据范围
        st.sidebar.header("选择数据范围")
        latest_period = len(df)
        start_row = st.sidebar.number_input("起始行（最老一期）", min_value=1, max_value=latest_period, value=1)
        end_row = st.sidebar.number_input("结束行（最新一期）", min_value=1, max_value=latest_period, value=latest_period)

        # 将起始行和结束行转换为数据索引
        start_index = latest_period - start_row
        end_index = latest_period - end_row

        # 根据选择的范围过滤数据
        filtered_data = df.iloc[end_index:start_index + 1]

        # 显示原始数据
        if st.sidebar.checkbox("显示原始数据"):
            st.subheader("原始数据")
            st.write(filtered_data)

        # 选择普通分析或特码分析或猜码分析
        analysis_type = st.sidebar.selectbox("选择分析类型", ["普通分析", "特码分析", "组合猜码分析"])

        # 开始分析按钮
        if st.sidebar.button("开始分析"):
            if analysis_type == "普通分析":
                # 获取数字列和生肖列
                number_columns = [f'号码{i}' for i in range(1, 8)]
                zodiac_columns = [f'生肖{i}' for i in range(1, 8)]
                
                # 绘制号码出现次数的柱状图
                st.subheader('每个号码出现的次数')
                number_counts = filtered_data[number_columns].apply(pd.Series.value_counts).sum(axis=1)
                fig, ax = plt.subplots(figsize=(12, 6))
                number_counts.sort_index().plot(kind='bar', color='skyblue', ax=ax)
                ax.set_title('每个号码出现的次数', fontproperties=font)
                ax.set_xlabel('号码', fontproperties=font)
                ax.set_ylabel('出现次数', fontproperties=font)
                ax.grid(axis='y')
                ax.set_xticklabels(ax.get_xticklabels(), fontproperties=font, rotation=45, ha='right')
                for p in ax.patches:
                    ax.annotate(str(int(p.get_height())), (p.get_x() * 1.005, p.get_height() * 1.005))
                st.pyplot(fig)

                # 绘制生肖出现次数的柱状图
                st.subheader('每个生肖出现的次数')
                zodiac_counts = filtered_data[zodiac_columns].apply(pd.Series.value_counts).sum(axis=1)
                zodiac_counts = zodiac_counts.reindex(zodiac_order, fill_value=0)
                fig, ax = plt.subplots(figsize=(12, 6))
                zodiac_counts.plot(kind='bar', color='lightgreen', ax=ax)
                ax.set_title('每个生肖出现的次数', fontproperties=font)
                ax.set_xlabel('生肖', fontproperties=font)
                ax.set_ylabel('出现次数', fontproperties=font)
                ax.grid(axis='y')
                ax.set_xticklabels(zodiac_order, fontproperties=font)
                for p in ax.patches:
                    ax.annotate(str(int(p.get_height())), (p.get_x() * 1.005, p.get_height() * 1.005))
                st.pyplot(fig)

                # 最常出现的号码组合
                st.subheader('最常出现的号码组合')
                all_combinations = []
                for index, row in filtered_data[number_columns].iterrows():
                    numbers = row.dropna().astype(int).tolist()
                    all_combinations.extend(combinations(numbers, 2))
                combination_counts = pd.Series(all_combinations).value_counts().head(10)
                fig, ax = plt.subplots(figsize=(12, 6))
                combination_counts.plot(kind='bar', color='cyan', ax=ax)
                ax.set_title('最常出现的号码组合', fontproperties=font)
                ax.set_xlabel('号码组合', fontproperties=font)
                ax.set_ylabel('出现次数', fontproperties=font)
                ax.grid(axis='y')
                ax.set_xticklabels(ax.get_xticklabels(), fontproperties=font, rotation=45, ha='right')
                for p in ax.patches:
                    ax.annotate(str(int(p.get_height())), (p.get_x() * 1.005, p.get_height() * 1.005))
                st.pyplot(fig)

                # 最常出现的生肖组合
                st.subheader('最常出现的生肖组合')
                all_zodiac_combinations = []
                for index, row in filtered_data[zodiac_columns].iterrows():
                    zodiacs = row.dropna().tolist()
                    all_zodiac_combinations.extend(combinations(zodiacs, 2))
                zodiac_combination_counts = pd.Series(all_zodiac_combinations).value_counts().head(10)
                fig, ax = plt.subplots(figsize=(12, 6))
                zodiac_combination_counts.plot(kind='bar', color='orange', ax=ax)
                ax.set_title('最常出现的生肖组合', fontproperties=font)
                ax.set_xlabel('生肖组合', fontproperties=font)
                ax.set_ylabel('出现次数', fontproperties=font)
                ax.grid(axis='y')
                ax.set_xticklabels(ax.get_xticklabels(), fontproperties=font, rotation=45, ha='right')
                for p in ax.patches:
                    ax.annotate(str(int(p.get_height())), (p.get_x() * 1.005, p.get_height() * 1.005))
                st.pyplot(fig)

            elif analysis_type == "特码分析":
                # 只分析第8列的号码和第15列的生肖
                st.subheader('特码分析')
                
                # 绘制特码号码出现次数的柱状图
                st.subheader('特码号码出现的次数')
                special_number_counts = filtered_data['号码7'].value_counts()
                fig, ax = plt.subplots(figsize=(12, 6))
                special_number_counts.sort_index().plot(kind='bar', color='skyblue', ax=ax)
                ax.set_title('特码号码出现的次数', fontproperties=font)
                ax.set_xlabel('号码', fontproperties=font)
                ax.set_ylabel('出现次数', fontproperties=font)
                ax.grid(axis='y')
                ax.set_xticklabels(ax.get_xticklabels(), fontproperties=font, rotation=45, ha='right')
                for p in ax.patches:
                    ax.annotate(str(int(p.get_height())), (p.get_x() * 1.005, p.get_height() * 1.005))
                st.pyplot(fig)

                # 绘制特码生肖出现次数的柱状图
                st.subheader('特码生肖出现的次数')
                special_zodiac_counts = filtered_data['生肖7'].value_counts()
                special_zodiac_counts = special_zodiac_counts.reindex(zodiac_order, fill_value=0)
                fig, ax = plt.subplots(figsize=(12, 6))
                special_zodiac_counts.plot(kind='bar', color='lightgreen', ax=ax)
                ax.set_title('特码生肖出现的次数', fontproperties=font)
                ax.set_xlabel('生肖', fontproperties=font)
                ax.set_ylabel('出现次数', fontproperties=font)
                ax.grid(axis='y')
                ax.set_xticklabels(zodiac_order, fontproperties=font)
                for p in ax.patches:
                    ax.annotate(str(int(p.get_height())), (p.get_x() * 1.005, p.get_height() * 1.005))
                st.pyplot(fig)

            elif analysis_type == "组合猜码分析":
                st.subheader('组合猜码分析')

                # 允许用户选择多个猜码类型
                guess_types = st.multiselect("选择组合的猜码类型", [
                    "5不中", "8不中", "10不中", "中一肖", "中二肖", "中三肖", "中四肖", "中五肖"
                ])

                # 记录每个猜码类型的参数
                guesses = []
                for guess_type in guess_types:
                    st.subheader(f"设置 {guess_type} 的参数")
                    if "不中" in guess_type:
                        guess_numbers = st.text_input(f"输入你猜的号码 (用逗号分隔) [{guess_type}]:")
                        guess_numbers = [int(num.strip()) for num in guess_numbers.split(',') if num.strip().isdigit()]
                        bet_amount = st.number_input(f"每期下注金额 (元) [{guess_type}]:", min_value=1, value=10)
                        odds = st.number_input(f"赔率 (1赔几) [{guess_type}]:", min_value=1, value=10)

                        guesses.append({
                            'type': guess_type,
                            'numbers': guess_numbers,
                            'bet_amount': bet_amount,
                            'odds': odds
                        })
                    else:
                        num_groups = st.number_input(f"你想在 {guess_type} 中选择几组组合:", min_value=1, value=1)
                        for i in range(num_groups):
                            guess_zodiacs = st.multiselect(f"选择你猜的生肖 [{guess_type}] - 组合 {i+1}:", zodiac_order)
                            bet_amount = st.number_input(f"每期下注金额 (元) [{guess_type}] - 组合 {i+1}:", min_value=1, value=10)
                            odds = st.number_input(f"赔率 (1赔几) [{guess_type}] - 组合 {i+1}:", min_value=1, value=10)

                            guesses.append({
                                'type': guess_type,
                                'zodiacs': guess_zodiacs,
                                'bet_amount': bet_amount,
                                'odds': odds
                            })

                # 计算最终收益
                total_bet = 0
                total_win = 0

                for guess in guesses:
                    num_wins = 0
                    for index, row in filtered_data.iterrows():
                        if "不中" in guess['type']:
                            appeared_numbers = row[[f'号码{i}' for i in range(1, 8)]].tolist()
                            if guess['type'] == "5不中" and len(set(guess['numbers']).intersection(appeared_numbers)) == 0:
                                num_wins += 1
                            elif guess['type'] == "8不中" and len(set(guess['numbers']).intersection(appeared_numbers)) == 0:
                                num_wins += 1
                            elif guess['type'] == "10不中" and len(set(guess['numbers']).intersection(appeared_numbers)) == 0:
                                num_wins += 1
                        else:
                            appeared_zodiacs = row[[f'生肖{i}' for i in range(1, 8)]].tolist()
                            if guess['type'] == "中一肖" and len(set(guess['zodiacs']).intersection(appeared_zodiacs)) >= 1:
                                num_wins += 1
                            elif guess['type'] == "中二肖" and len(set(guess['zodiacs']).intersection(appeared_zodiacs)) >= 2:
                                num_wins += 1
                            elif guess['type'] == "中三肖" and len(set(guess['zodiacs']).intersection(appeared_zodiacs)) >= 3:
                                num_wins += 1
                            elif guess['type'] == "中四肖" and len(set(guess['zodiacs']).intersection(appeared_zodiacs)) >= 4:
                                num_wins += 1
                            elif guess['type'] == "中五肖" and len(set(guess['zodiacs']).intersection(appeared_zodiacs)) >= 5:
                                num_wins += 1
                    
                    bet = guess['bet_amount'] * len(filtered_data)
                    win = num_wins * guess['bet_amount'] * guess['odds']
                    total_bet += bet
                    total_win += win

                    st.write(f"{guess['type']} - 组合 - 下注总金额: {bet} 元, 总中奖次数: {num_wins} 次, 总中奖金额: {win} 元")

                net_profit = total_win - total_bet
                st.write(f"最终收益: {net_profit} 元")
