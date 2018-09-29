# fit-solution
A flask based financial web application which is used to virtually trade stocks and provide real-time foreign exchange rates.

## Parts of Web Application
1.  Stock Trading:

As the user gets access to the FitSolution account, a fixed amount of virtual money is assigned to the user (In our case we provide $20,000) using which they can play around with the application; also a chart showing stock data of various companies is rendered, from there user can go on to quote the price of a share using the ticker symbol of any company under NASDAQ.
 
Upon visiting the price quote section, a pointer is made visible which shows how whether there is a strong buy for the stock, or a strong sell. If users wish to buy the stock, they can buy the desired number of shares from the buy section of the web app. In case the user wants to sell the shares, sell section can be accessed similarly. Users can also access the history of their transactions in a table extending back to their first transaction with all the necessary details associated with the transaction.
 
The user can also keep track of his/her profit or loss and the current amount of cash left in the wallet. When talking about real-time prices of stocks, the API’s that made significant contribution to FitSolution, were “Alpha Vantage” and “IEX Trading”, using which we were able to fetch the current price of the share of desired company.

Graphs and data were made available using the platform known as “Trading View.” The available data was embedded into the HTML pages as per the documentation offered by Tradingview to make FitSolution more interactive by providing charts and markers which gives the user a real but virtual experience of how stock trading works in real life. The tables that were rendered when in “History” and “Stocks Held” section of the application were designed using HTML and CSS.
 
When fed up dealing stocks, users can now proceed onto the other sections of FitSolution, they are covered further in the following portion.
 
2. 	Foreign Exchange
 
It is the second feature of FitSolution, in this; a user can query the current foreign exchange rates between any two currencies. A couple of lists are generated using Jinja2, HTML and “Open Exchange API”, containing all the major currencies being used in different countries, from which user selects two currencies, then the server handles the request made by client and gets the job done.
 
3. 	Crypto-currency rates
 
“Tradingview” helped us yet another time in this section; this section provides the pricing of crypto-currencies with respect to real currencies, such as USD. Being accompanied by a graph depicting the rise and fall of the prices, this chart is a perfect indicator of the crypto-currency worth in real market.
 
In case of mishandling of password by the user, he can change the password by visiting the settings tab on the navigation bar. Again the new password is hashed and stored in the database and the old one is ruled out so that it can’t help in logging into the application. Once the user is done with the work, he can log out at any instance and the status of the portal will remain when logging into the application some other time.


## Requirements
- python
- pip

## Screenshots
![alt text](https://github.com/ayushdata/fit-solution/blob/master/screenshots/Homepage.png)
** Homepage: Access to Login and Register pages **

![alt text](https://github.com/ayushdata/fit-solution/blob/master/screenshots/Quoted.png)
** Quoted price along with strong buy/sell indicator **

![alt text](https://github.com/ayushdata/fit-solution/blob/master/screenshots/Sell.png)
** Sell the shares held **

![alt text](https://github.com/ayushdata/fit-solution/blob/master/screenshots/priceAndGains.png)
** Stocks held and Profit/Loss on $20000 initial money **

![alt text](https://github.com/ayushdata/fit-solution/blob/master/screenshots/Cryptos.png)
** Chart to show cryptocurrency value variation ** 

