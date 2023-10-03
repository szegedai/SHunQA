FROM python:3.10

RUN pip install --upgrade pip

RUN apt-get update
RUN apt-get install -y curl g++ gcc python3-dev build-essential rust-all

WORKDIR /home/backend

COPY . .

ENV VIRTUAL_ENV=/home/backend/venv

RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install scikit-learn==1.3.0
RUN pip install torch==1.12.0+cpu torchvision==0.13.0+cpu torchaudio==0.12.0 --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install https://huggingface.co/huspacy/hu_core_news_trf/resolve/v3.5.3/hu_core_news_trf-any-py3-none-any.whl
RUN pip install -r requirements.txt

WORKDIR /home

EXPOSE 5000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5000"]