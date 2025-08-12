
## Audio test

https://shared-files-repo.s3.us-east-1.amazonaws.com/doctor_appointment.mp3

```
cd backend
```

add .env according to .env.example

then

```
cd functions
```

```
python -m venv .venv
```

```
source .venv/Scripts/activate
```

```
firebase init
```

override settings and install requirements

if error "To modify pip, please run the following command"
```
path_to_project\challenge-telepatia\backend\functions\venv\Scripts\python.exe -m pip install --upgrade pip
```

then

```
firebase init
```

override settings and install requirements

dependencies will install