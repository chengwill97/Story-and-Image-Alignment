# Installation Instructions for Flask App

### 1. Setup Anaconda/Miniconda

[Follow Instructions here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html?highlight=conda)

### 2. Create Python environment

1. Go to flask app folder

```
cd $(SANDI_PROJECT_ROOT)/flask
```

2. Create Anconda environment

```
conda env create -f environment.yml python=2.7

conda activate sandi

pip install -r requirements.txt --ignore-installed

pip install --upgrade https://github.com/Lasagne/Lasagne/archive/master.zip
```

### 3. Set up resources folder

1. Download resources folder

2. Download yolo model into ```resources/yolo```
Full weights: ```wget https://pjreddie.com/media/files/yolo.weights```
Light Weights: ```wget https://pjreddie.com/media/files/tiny-yolo.weights```

### 4. Set up environment variables

1. Check .flaskenv

2. Check .env