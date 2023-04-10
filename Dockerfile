FROM python
COPY  chatbot.py .
COPY  requirements.txt .
ENV ACCESS_TOKEN   6294688745:AAFqe6VoCNqiDHZloI_nB6M0y8V2aBjZjaw
ENV server   zeroonenetflix.database.windows.net
ENV database   zeroone
ENV username   drstrange
ENV password   NoPassword7940
ENV driver   {ODBC Driver 18 for SQL Server}
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y gcc unixodbc-dev
RUN pip install pyodbc
CMD python chatbot.py