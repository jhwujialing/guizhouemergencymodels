FROM python:3.6

WORKDIR /spider_shuiwen
# 安装支持
ADD . .
#RUN pip install -r /test/requirements.txt
#RUN apt-get install yum
#RUN apt-get install vim


# 安装git、python、nginx、supervisor等，并清理缓存
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        vim \
        nginx \
        supervisor
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx-app.conf /etc/nginx/sites-available/default
COPY supervisor-app.conf /etc/supervisor/conf.d/
CMD ["supervisord", "-n"]
#RUN nginx
#CMD ["python", "/test/test1.py"]
#ENTRYPOINT ["python","/test1/test2.py"]