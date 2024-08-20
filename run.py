import requests
from bs4 import BeautifulSoup
import pandas as pd



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
    print(html_content[:1000])  # 打印前1000个字符
else:
    print(f"无法获取网页内容，状态码: {response.status_code}")

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
        print(f"数据提取错误: 期数 {period} 有 {len(period_numbers)} 个号码和 {len(period_zodiacs)} 个生肖")

# 创建DataFrame
columns = ['期数'] + [f'号码{i}' for i in range(1, 8)] + [f'生肖{i}' for i in range(1, 8)]
df = pd.DataFrame(results, columns=columns)

# 保存为CSV文件，修改保存路径
df.to_csv('六合彩开奖记录.csv', index=False, encoding='utf-8-sig')

print("数据提取完成并保存为六合彩开奖记录.csv")
