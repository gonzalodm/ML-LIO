#!/usr/bin/env python3.8

import modules as mod
import os
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.callbacks import EarlyStopping
from pytorch_lightning.callbacks import LearningRateMonitor
import pytorch_lightning as pl
import argparse

# Argumentos
parser = argparse.ArgumentParser()
parser.add_argument("-i","--inputs", help="Input file path", action="store")
args = parser.parse_args()

# Checkeamos la correcta ejecucion del programa
if args.inputs == None:
    print("Ejecuta el codigo: ./train.py -i path_to_input")
    exit(-1)

# Leemos el archivo de input
inputs = mod.read_input(args.inputs)

# Nombre del archivo de datos
inputs["dataset_file"] = inputs["path_dir"] + "dataset_Pfit.pickle"

# Resultados
inputs["path_results"] = inputs["path_dir"] + "results/"

Data = mod.DataModule(inputs)
Data.setup(stage="fit")

# Guardamos la cantidad de data total: train + val + test
inputs["ndata"] = Data.ndata

# Instanciamos el Modelo
if inputs["restart"]:
    print("Restarting trainning...")
    path = inputs["path_results"] + "/" 
    path = path + inputs["model_file"]
    try:
        model = mod.Modelo.load_from_checkpoint(
                checkpoint_path=path,config=inputs)
    except:
        print("El modelo no se pudo Leer")
        exit(-1)
else:
    model = mod.Modelo(inputs)

# Abrimos un folder para los resultados
if os.path.isdir(inputs["path_results"]):
    os.system("rm -rf " + inputs["path_results"])

# Checkpoint del Modelo
checkpoint = ModelCheckpoint(
    dirpath = inputs["path_results"],
    monitor="val_loss",
    filename = "modelo-{val_loss:.5f}",
    save_top_k = 1,
    mode="min"
)

# Early stopping
early_stopping = EarlyStopping(
    monitor = "val_loss",
    patience= 10,
    verbose=True,
    mode="min"
)

# Lr Monitor
lr_monitor = LearningRateMonitor(logging_interval="epoch")

# Entrenamiento
calls = [checkpoint,early_stopping,lr_monitor]
trainer = pl.Trainer(max_epochs=inputs["nepochs"], gpus=0,callbacks=calls)
trainer.fit(model=model,datamodule=Data)

# Graficamos resultados del train
model.graficar()
