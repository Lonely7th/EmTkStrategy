这篇文章主要介绍如何使用Python对一些简单的交易策略进行回测，对这块比较感兴趣的初学者可以看一看。文章主要分为以下几个部分：

**1.获取证券数据**

**2.编写交易逻辑**

**3.模拟交易操作**

**4.统计结果和绘图**

# 1.获取证券数据
创建策略之前我们要明确一个问题，这个交易策略将会被用在哪个市场？这样我们才能有针对性的获取数据。本文以A股市场为例，先获取A股近10年的数据并保存到数据库。
#### 1.1.安装数据库（MongoDB）
为了提升运行效率，需要将证券数据保存到本地数据库，这里我们选择的数据库是MongoDB，安装过程在此不再赘述，参照[http://www.runoob.com/mongodb/mongodb-window-install.html](http://www.runoob.com/mongodb/mongodb-window-install.html)即可，比较简单。
#### 1.2.编写数据库操作类
安装完数据库，我们编写一个工具类来管理数据库的增删改查等操作：
```
class DBManager:
    def __init__(self, table_name):
        self.client = MongoClient("127.0.0.1", 27017)
        self.db = self.client["my_database"]
        self.table = self.db[table_name]

    def clsoe_db(self):
        self.client.close()

    # 获取股票代码列表(sz格式)
    def get_code_list(self):
        return self.table.find({}, {"ticker": 1}, no_cursor_timeout=True)

    # 查询多条数据
    def find_by_key(self, request=None):
        if request is None:
            request = {}
        return self.table.find(request)

    # 查询单条数据
    def find_one_by_key(self, request=None):
        if request is None:
            request = {}
        return self.table.find_one(request)

    # 添加单条数据
    def add_one(self, post, created_time=datetime.datetime.now()):
        # 添加一条数据
        post['created_time'] = created_time
        return self.table.insert_one(post)

    # 添加历史交易记录
    def add_tk_item(self, ticker, __dict):
        return self.table.update_one({'ticker': ticker}, {"$push": {"data_list": __dict}})
```
#### 1.3.获取数据
获取证券数据的途径分为两种，第一种是去网上找现成的数据接口，通过调用接口获取数据，这种方式的优点在于简单便捷，数据的准确性有保障；第二种是自己编写数据爬虫获取数据，这种方式会相对麻烦一点，但如果你对数据的时效性要求较高，或者数据接口中的数据不能满足你的需求，可以选择第二种方式。本文采用的是第一种方式。使用的数据接口是[http://www.baostock.com/](http://www.baostock.com/)。

调用接口：
```
bs.login()  # 初始化baostock
code_list = dm.get_code_list()  # 获取股票代码列表
for item in code_list:
    max_try = 8  # 失败重连的最大次数
    ticker = item["ticker"]
    for tries in range(max_try):
        rs = bs.query_history_k_data(ticker, "date,code,open,high,low,close,volume,amount,adjustflag,turn,"
                                                 "pctChg", frequency="w", adjustflag="3")
        if rs.error_code == '0':
            parse_pager(rs, ticker)  # 解析数据
            break
        elif tries < (max_try - 1):
            sleep(2)
            continue
        else:
            log.logger.error("加载数据失败：" + str(ticker))
log.logger.info("加载数据完成")
bs.logout()
```
解析数据：
```
# 解析数据并保存到数据库
def parse_pager(content, ticker):
    while content.next():
        item_row = content.get_row_data()
        __dict = {
            "date": item_row[0],
            "code": item_row[1],
            "open": item_row[2],
            "high": item_row[3],
            "low": item_row[4],
            "close": item_row[5],
            "volume": item_row[6],
            "amount": item_row[7],
            "adjustflag": item_row[8],
            "turn": item_row[9],
            "pctChg": item_row[10]
        }
        dm.add_tk_item(ticker, __dict)  # 将数据保存到数据库
```
# 2.编写交易逻辑
为了便于描述，本次我们选择了一个较为简单的交易逻辑。以周为交易周期，每周一开盘前分析各股的周macd数据，满足交易条件则以开盘价买入并持有一周，以当周五的收盘价卖出。这个交易逻辑非常简单，回测的表现也有可圈可点之处（回测结果见文末），但离实盘交易还有一定的距离。交易逻辑的核心代码如下：
```
if wmacd_list[-1] > 0 >= wmacd_list[-2]:
    if np.mean(volume_list[-5:-1]) < volume_list[-1]:
        if 0.1 >= diff_list[-1] >= 0:
        data = [x for x in dm_tk.find_one_by_key({"ticker": item["ticker"]})["data_list"] if x["date"] == cur_date][0]
        result_list.append(data)
```
```
def get_w_macd(price_list):
    ema_12_list = list()
    for index in range(len(price_list)):
        if index == 0:
            ema_12_list.append(price_list[0])
        else:
            ema_12_list.append(round(ema_12_list[index - 1] * 11 / 13 + price_list[index] * 2 / 13, 4))
    ema_26_list = list()
    for index in range(len(price_list)):
        if index == 0:
            ema_26_list.append(price_list[0])
        else:
            ema_26_list.append(round(ema_26_list[index - 1] * 25 / 27 + price_list[index] * 2 / 27, 4))
    diff_list = list()
    for index in range(len(ema_12_list)):
        diff = ema_12_list[index] - ema_26_list[index]
        diff_list.append(diff)
    dea_list = list()
    for index in range(len(diff_list)):
        if index == 0:
            dea_list.append(diff_list[0])
        else:
            dea_list.append(round(dea_list[index - 1] * 0.8 + diff_list[index] * 0.2, 4))
    wmacd_list = list()
    for index in range(len(dea_list)):
        bar = (diff_list[index] - dea_list[index]) * 3
        wmacd_list.append(bar)
    return wmacd_list, diff_list, dea_list
```
对于交易逻辑我只截取了其中的一小部分，因为这段代码相对来说比较复杂，而且读者也不需要看懂其中的逻辑，实际开发过程中肯定会使用自己的交易逻辑而不是这个。
# 3.模拟交易操作
明确好交易逻辑后，我们就可以开始模拟交易操作了。首先我们初始化一些数据，这些数据在我们日常交易中也非常常见，比如起始资金、当前可用资金、交易周期、持仓列表、最大仓位等等，由于我们的交易策略比较简单，所以我们只要初始化起始资金就可以了：
```
capital_base = 1000000  # 起始资金设定为100万
history_capital = list()  # 用于记录交易结果
```
接下来我们创建一条时间轴，所有的交易操作都将跟随时间轴进行：
```
# 生成时间轴
def date_range(start, end, step=1, format="%Y-%m-%d"):
    strptime, strftime = datetime.datetime.strptime, datetime.datetime.strftime
    days = (strptime(end, format) - strptime(start, format)).days + 1
    return [strftime(strptime(start, format) + datetime.timedelta(i), format) for i in range(0, days, step)]
```
```
date_list = date_range("2016-01-01", "2016-12-31")  # 生成2016-01-01至2016-12-31的所有时间点
```
生成好时间轴后，使用for循环遍历时间轴，按照之前设定的交易逻辑，我们需要在每周一和周五进行操作，由于该策略不涉及加减仓，故我们对交易过程就行了简化，用直接计算得到的结果替代了买入卖出的操作，对于更为复杂的交易策略，开发者需要分别实现开仓、平仓和加减仓等各种操作：
```
for cur_date in date_list:
    if datetime.datetime.strptime(cur_date, "%Y-%m-%d").weekday() == 4:  # 判断当前日期是否需要操作    
        result_list = list()  # 用于记录当前时间符合交易条件的股票代码
        for item in code_list:  # 遍历各支股票，筛选出符合交易条件的股票

            -执行交易逻辑-

            if 符合交易条件:
                result_list.append(data)

        # 计算结果
        if result_list:
            capital = capital_base / len(result_list)  # 对当前资金进行均分
            temp_capital = 0
            for item in result_list:
                close_price = float(item["close"])
                open_price = float(item["open"])
                max_price = float(item["high"])
                profit = (close_price - open_price) / open_price
                temp_capital += (capital * (1 + profit))
            capital_base = temp_capital 
        history_capital.append(capital_base)  # 记录本次操作后剩余的资金
```
# 4.统计结果和绘图
模拟交易完成后我们来对结果进行统计，由于我们已经将交易的结果记录在history_capital中，此时我们可以轻松的计算出收益率：
```
net_rate = (history_capital[-1] - history_capital[0]) / history_capital[0]  # 计算回测结果
log.logger.info("total_profit：" + str(round(net_rate * 100, 2)) + "%")
```
为了让交易的结果更加直观，我们还可以将其绘制成折线图，使用matplotlib进行绘图：
```
plt.subplot(111)
lable_x = np.arange(len(history_capital))
plt.plot(lable_x, history_capital, color="r", linewidth=1.0, linestyle="-")
plt.xlim(lable_x.min(), lable_x.max() * 1.1)
plt.ylim(min(history_capital) * 0.9, max(history_capital) * 1.1)
plt.grid(True)
plt.show()
```
**回测结果展示：**

![2014.png](https://upload-images.jianshu.io/upload_images/9225319-05a4b38bbeed73a1.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![2015.png](https://upload-images.jianshu.io/upload_images/9225319-0503425130d524f9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![2016.png](https://upload-images.jianshu.io/upload_images/9225319-3b33b0238228731b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![2017.png](https://upload-images.jianshu.io/upload_images/9225319-402697b3eb4282a4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

到此为止，我们就完成了使用Python对某个交易策略进行回测的全部流程，读者可以自由变换交易逻辑来获取不同的结果，通过对回测结果进行分析，可以对我们日常的交易带来一点帮助。
与我交流：1003882179@qq.com
