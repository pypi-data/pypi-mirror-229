import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import sys
from fecom.patching.patching_config import EXPERIMENT_DIR
from fecom.measurement.execution import before_execution as before_execution_INSERTED_INTO_SCRIPT
from fecom.measurement.execution import after_execution as after_execution_INSERTED_INTO_SCRIPT
from fecom.experiment.experiment_kinds import ExperimentKinds
experiment_number = sys.argv[1]
experiment_project = sys.argv[2]
EXPERIMENT_FILE_PATH = EXPERIMENT_DIR / ExperimentKinds.METHOD_LEVEL.value / experiment_project / f'experiment-{experiment_number}.json'
print(tf.__version__)
fashion_mnist = tf.keras.datasets.fashion_mnist
((train_images, train_labels), (test_images, test_labels)) = fashion_mnist.load_data()
class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
train_images.shape
len(train_labels)
train_labels
test_images.shape
len(test_labels)
plt.figure()
plt.imshow(train_images[0])
plt.colorbar()
plt.grid(False)
plt.show()
train_images = train_images / 255.0
test_images = test_images / 255.0
plt.figure(figsize=(10, 10))
for i in range(25):
    plt.subplot(5, 5, i + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(train_images[i], cmap=plt.cm.binary)
    plt.xlabel(class_names[train_labels[i]])
plt.show()
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()')
model = tf.keras.Sequential([tf.keras.layers.Flatten(input_shape=(28, 28)), tf.keras.layers.Dense(128, activation='relu'), tf.keras.layers.Dense(10)])
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()', method_object=None, function_args=[[tf.keras.layers.Flatten(input_shape=(28, 28)), tf.keras.layers.Dense(128, activation='relu'), tf.keras.layers.Dense(10)]], function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.compile()')
model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=['accuracy'])
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.compile()', method_object=model, function_args=None, function_kwargs={'optimizer': 'adam', 'loss': tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 'metrics': ['accuracy']})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.fit()')
model.fit(train_images, train_labels, epochs=10)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.fit()', method_object=model, function_args=[train_images, train_labels], function_kwargs={'epochs': 10})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.evaluate()')
(test_loss, test_acc) = model.evaluate(test_images, test_labels, verbose=2)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.evaluate()', method_object=model, function_args=[test_images, test_labels], function_kwargs={'verbose': 2})
print('\nTest accuracy:', test_acc)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()')
probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()', method_object=None, function_args=[[model, tf.keras.layers.Softmax()]], function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.predict()')
predictions = probability_model.predict(test_images)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.predict()', method_object=probability_model, function_args=[test_images], function_kwargs=None)
predictions[0]
np.argmax(predictions[0])
test_labels[0]

def plot_image(i, predictions_array, true_label, img):
    (true_label, img) = (true_label[i], img[i])
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(img, cmap=plt.cm.binary)
    predicted_label = np.argmax(predictions_array)
    if predicted_label == true_label:
        color = 'blue'
    else:
        color = 'red'
    plt.xlabel('{} {:2.0f}% ({})'.format(class_names[predicted_label], 100 * np.max(predictions_array), class_names[true_label]), color=color)

def plot_value_array(i, predictions_array, true_label):
    true_label = true_label[i]
    plt.grid(False)
    plt.xticks(range(10))
    plt.yticks([])
    thisplot = plt.bar(range(10), predictions_array, color='#777777')
    plt.ylim([0, 1])
    predicted_label = np.argmax(predictions_array)
    thisplot[predicted_label].set_color('red')
    thisplot[true_label].set_color('blue')
i = 0
plt.figure(figsize=(6, 3))
plt.subplot(1, 2, 1)
plot_image(i, predictions[i], test_labels, test_images)
plt.subplot(1, 2, 2)
plot_value_array(i, predictions[i], test_labels)
plt.show()
i = 12
plt.figure(figsize=(6, 3))
plt.subplot(1, 2, 1)
plot_image(i, predictions[i], test_labels, test_images)
plt.subplot(1, 2, 2)
plot_value_array(i, predictions[i], test_labels)
plt.show()
num_rows = 5
num_cols = 3
num_images = num_rows * num_cols
plt.figure(figsize=(2 * 2 * num_cols, 2 * num_rows))
for i in range(num_images):
    plt.subplot(num_rows, 2 * num_cols, 2 * i + 1)
    plot_image(i, predictions[i], test_labels, test_images)
    plt.subplot(num_rows, 2 * num_cols, 2 * i + 2)
    plot_value_array(i, predictions[i], test_labels)
plt.tight_layout()
plt.show()
img = test_images[1]
print(img.shape)
img = np.expand_dims(img, 0)
print(img.shape)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.predict()')
predictions_single = probability_model.predict(img)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.predict()', method_object=probability_model, function_args=[img], function_kwargs=None)
print(predictions_single)
plot_value_array(1, predictions_single[0], test_labels)
_ = plt.xticks(range(10), class_names, rotation=45)
plt.show()
np.argmax(predictions_single[0])
