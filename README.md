**Python 3.7+**

### Prerequisites
1. 
- account 0x1D9f2C01c8A20DcC59e806caFF5f46033e84ad2B must be active and must have sufficient balance;
- account 0x0AeA70d72D5e2218CF9aF28410ed388AE03b799b must be active, must have sufficient balance and must be owner/admin of KYC contract
2. Install required packages:
```
pip3 install -r requirements.txt
```


### Run tests
```
pytest --node=http://15.237.34.82:8575
```

Run tests with a little better looking report:
```
pytest --node=http://15.237.34.82:8575 --alluredir=allure-results
```

### Reports
1. `report.html` file in working directory;  
OR
2. build [Allure](https://github.com/allure-framework/allure2) report from `allure-results`
