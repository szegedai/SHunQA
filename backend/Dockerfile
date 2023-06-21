FROM python:3.10

# upgrade pip
RUN pip install --upgrade pip

# get curl for healthchecks
RUN apt-get update
RUN apt-get install -y curl g++ gcc python3-dev build-essential rust-all

# permissions and nonroot user for tightened security
# RUN adduser -D nonroot
# RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
# RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
# RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
# USER nonroot

# copy all the files to the container
# COPY --chown=nonroot:nonroot . .
COPY . .

# venv
ENV VIRTUAL_ENV=/home/app/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# RUN export FLASK_APP=app.py
RUN pip install torch==1.12.0+cpu torchvision==0.13.0+cpu torchaudio==0.12.0 --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

# define the port number the container should expose
EXPOSE 5000

CMD ["python", "flask_service.py"]