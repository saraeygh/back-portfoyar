FUND_COL_MAPPING = {
    "regNo": "reg_no",  # str
    "name": "name",  # str
    # "rankOf12Month": "null",
    # "rankOf24Month": "null",
    # "rankOf36Month": "null",
    # "rankOf48Month": "null",
    # "rankOf60Month": "null",
    # "rankLastUpdate": "0001-01-01T00:00:00",
    "fundType": "fund_type",  # int
    "typeOfInvest": "invest_type",  # str
    "fundSize": "fund_size",  # int
    "initiationDate": "initiation_date",  # str
    "dailyEfficiency": "daily",  # float
    "weeklyEfficiency": "weekly",  # float
    "monthlyEfficiency": "monthly",  # float
    "quarterlyEfficiency": "quarterly",  # float
    "sixMonthEfficiency": "six_month",  # float
    "annualEfficiency": "annual",  # float
    "statisticalNav": "statistical_nav",  # int
    "efficiency": "total",  # float
    "cancelNav": "cancel_nav",  # int
    "issueNav": "issue_nav",  # int
    "dividendIntervalPeriod": "dividend_interval_period",  # int
    "guaranteedEarningRate": "guaranteed_earning_rate",  # int
    "date": "last_date",  # str
    "netAsset": "net_asset",  # int
    "estimatedEarningRate": "estimated_earning_rate",
    "investedUnits": "invested_units",  # int
    # "articlesOfAssociationLink": "null",
    # "prosoectusLink": "null",
    "websiteAddress": "website",  # str
    "manager": "fund_manager",  # str
    "managerSeoRegisterNo": "manager_reg_no",
    # "guarantorSeoRegisterNo": "null",
    # "auditor": "موسسه حسابرسی آزموده کاران",  # str
    # "custodian": "موسسه حسابرسی بهراد مشار",  # str
    "guarantor": "guarantor",  # str
    # "beta": "null",
    # "alpha": "null",
    # "isCompleted": "true",
    "fiveBest": "five_best",  # float
    "stock": "stock",  # float
    "bond": "bond",  # float
    "other": "other",  # float
    "cash": "cash",  # float
    "deposit": "deposit",  # float
    "fundUnit": "fund_unit",  # float
    "commodity": "commodity",  # float
    # "fundPublisher": 2,
    "smallSymbolName": "symbol",
    "insCode": "ins_code",
    # "fundWatch": "null",
}

FIPIRAN_HEADERS = {
    "Host": "fund.fipiran.ir",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Referer": "https://fund.fipiran.ir/mf/list",
    "Cookie": "_ga_GMN6YQMVMN=GS1.1.1737524608.1.1.1737525006.0.0.0; _ga=GA1.1.867937809.1737524608; _gid=GA1.2.961009005.1737524609; _ga_KCEQVBSLW1=GS1.2.1737524609.1.1.1737525003.0.0.0; _gat=1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}
