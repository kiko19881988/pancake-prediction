# docker build --progress=plain --no-cache -t kavehbc/pancake-prediction .
# docker save -o pancake-prediction.tar kavehbc/pancake-prediction
# docker load --input pancake-prediction.tar

FROM python:3.8-buster

LABEL version="1.0.0"
LABEL maintainer="Kaveh Bakhtiyari"
LABEL url="http://bakhtiyari.com"
LABEL vcs-url="https://github.com/kavehbc/pancake-prediction"
LABEL description="Pancakeswap Prediction Bot"

WORKDIR /app
COPY . .

# installing the requirements
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["main.py"]