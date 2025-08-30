import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=20, 
                                   zoom_range=0.2, horizontal_flip=True)
val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    "mangrove trees/train", target_size=(224,224), batch_size=32, class_mode="binary")
val_gen = val_datagen.flow_from_directory(
    "mangrove trees/test", target_size=(224,224), batch_size=32, class_mode="binary")

base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224,224,3))
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(1, activation="sigmoid")
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
history = model.fit(train_gen, validation_data=val_gen, epochs=10)
model.save("mangrove_model.h5")
