import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

print(f"TensorFlow Version: {tf.__version__}")

# Paths
base_dir = "/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/Handwriting"
train_dir = os.path.join(base_dir, "training")
test_dir = os.path.join(base_dir, "testing")

# Image parameters
IMG_SIZE = 224
BATCH_SIZE = 32

# Data Generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=10,
    zoom_range=0.1,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

# Load Pretrained ResNet50
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# Freeze base model layers
for layer in base_model.layers:
    layer.trainable = False

# Add custom head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.5)(x)
output = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=output)

# Compile
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("Starting initial training...")
# Train
history = model.fit(
    train_generator,
    validation_data=test_generator,
    epochs=10
)

# Fine-tuning
print("Starting fine-tuning...")
for layer in base_model.layers[-20:]:
    layer.trainable = True

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_generator, 
    validation_data=test_generator, 
    epochs=5
)

# Evaluate
loss, acc = model.evaluate(test_generator)
print("Test Accuracy:", acc)

# Save the model
os.makedirs("/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/ml-models/models/handwriting", exist_ok=True)
model_path = "/home/hari/Downloads/parkinson/Parkinson-disease-diagonisis/ml-models/models/handwriting/resnet50_combined_best.keras"
model.save(model_path)
print(f"Model saved to {model_path}")
