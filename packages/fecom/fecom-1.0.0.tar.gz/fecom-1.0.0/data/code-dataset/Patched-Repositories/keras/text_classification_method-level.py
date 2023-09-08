import matplotlib.pyplot as plt
import os
import re
import shutil
import string
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import losses
import sys
from fecom.patching.patching_config import EXPERIMENT_DIR
from fecom.measurement.execution import before_execution as before_execution_INSERTED_INTO_SCRIPT
from fecom.measurement.execution import after_execution as after_execution_INSERTED_INTO_SCRIPT
from fecom.experiment.experiment_kinds import ExperimentKinds
experiment_number = sys.argv[1]
experiment_project = sys.argv[2]
EXPERIMENT_FILE_PATH = EXPERIMENT_DIR / ExperimentKinds.METHOD_LEVEL.value / experiment_project / f'experiment-{experiment_number}.json'
print(tf.__version__)
url = 'https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz'
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.get_file()')
dataset = tf.keras.utils.get_file('aclImdb_v1', url, untar=True, cache_dir='.', cache_subdir='')
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.get_file()', method_object=None, function_args=['aclImdb_v1', url], function_kwargs={'untar': True, 'cache_dir': '.', 'cache_subdir': ''})
dataset_dir = os.path.join(os.path.dirname(dataset), 'aclImdb')
os.listdir(dataset_dir)
train_dir = os.path.join(dataset_dir, 'train')
os.listdir(train_dir)
sample_file = os.path.join(train_dir, 'pos/1181_9.txt')
with open(sample_file) as f:
    print(f.read())
remove_dir = os.path.join(train_dir, 'unsup')
shutil.rmtree(remove_dir)
batch_size = 32
seed = 42
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory()')
raw_train_ds = tf.keras.utils.text_dataset_from_directory('aclImdb/train', batch_size=batch_size, validation_split=0.2, subset='training', seed=seed)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory()', method_object=None, function_args=['aclImdb/train'], function_kwargs={'batch_size': batch_size, 'validation_split': 0.2, 'subset': 'training', 'seed': seed})
for (text_batch, label_batch) in raw_train_ds.take(1):
    for i in range(3):
        print('Review', text_batch.numpy()[i])
        print('Label', label_batch.numpy()[i])
print('Label 0 corresponds to', raw_train_ds.class_names[0])
print('Label 1 corresponds to', raw_train_ds.class_names[1])
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory()')
raw_val_ds = tf.keras.utils.text_dataset_from_directory('aclImdb/train', batch_size=batch_size, validation_split=0.2, subset='validation', seed=seed)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory()', method_object=None, function_args=['aclImdb/train'], function_kwargs={'batch_size': batch_size, 'validation_split': 0.2, 'subset': 'validation', 'seed': seed})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory()')
raw_test_ds = tf.keras.utils.text_dataset_from_directory('aclImdb/test', batch_size=batch_size)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory()', method_object=None, function_args=['aclImdb/test'], function_kwargs={'batch_size': batch_size})

def custom_standardization(input_data):
    start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.strings.lower()')
    lowercase = tf.strings.lower(input_data)
    after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.strings.lower()', method_object=None, function_args=[input_data], function_kwargs=None)
    start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.strings.regex_replace()')
    stripped_html = tf.strings.regex_replace(lowercase, '<br />', ' ')
    after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.strings.regex_replace()', method_object=None, function_args=[lowercase, '<br />', ' '], function_kwargs=None)
    return tf.strings.regex_replace(stripped_html, '[%s]' % re.escape(string.punctuation), '')
max_features = 10000
sequence_length = 250
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.layers.TextVectorization()')
vectorize_layer = layers.TextVectorization(standardize=custom_standardization, max_tokens=max_features, output_mode='int', output_sequence_length=sequence_length)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.layers.TextVectorization()', method_object=None, function_args=None, function_kwargs={'standardize': custom_standardization, 'max_tokens': max_features, 'output_mode': 'int', 'output_sequence_length': sequence_length})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()')
train_text = raw_train_ds.map(lambda x, y: x)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()', method_object=raw_train_ds, function_args=[lambda x, y: x], function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.layers.TextVectorization.adapt()')
vectorize_layer.adapt(train_text)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.layers.TextVectorization.adapt()', method_object=vectorize_layer, function_args=[train_text], function_kwargs=None)

def vectorize_text(text, label):
    start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.expand_dims()')
    text = tf.expand_dims(text, -1)
    after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.expand_dims()', method_object=None, function_args=[text, -1], function_kwargs=None)
    return (vectorize_layer(text), label)
(text_batch, label_batch) = next(iter(raw_train_ds))
(first_review, first_label) = (text_batch[0], label_batch[0])
print('Review', first_review)
print('Label', raw_train_ds.class_names[first_label])
print('Vectorized review', vectorize_text(first_review, first_label))
print('1287 ---> ', vectorize_layer.get_vocabulary()[1287])
print(' 313 ---> ', vectorize_layer.get_vocabulary()[313])
print('Vocabulary size: {}'.format(len(vectorize_layer.get_vocabulary())))
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()')
train_ds = raw_train_ds.map(vectorize_text)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()', method_object=raw_train_ds, function_args=[vectorize_text], function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()')
val_ds = raw_val_ds.map(vectorize_text)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()', method_object=raw_val_ds, function_args=[vectorize_text], function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()')
test_ds = raw_test_ds.map(vectorize_text)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map()', method_object=raw_test_ds, function_args=[vectorize_text], function_kwargs=None)
AUTOTUNE = tf.data.AUTOTUNE
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map.cache().prefetch()')
train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map.cache().prefetch()', method_object=train_ds, function_args=None, function_kwargs={'buffer_size': AUTOTUNE})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map.cache().prefetch()')
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map.cache().prefetch()', method_object=val_ds, function_args=None, function_kwargs={'buffer_size': AUTOTUNE})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map.cache().prefetch()')
test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.utils.text_dataset_from_directory.map.cache().prefetch()', method_object=test_ds, function_args=None, function_kwargs={'buffer_size': AUTOTUNE})
embedding_dim = 16
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()')
model = tf.keras.Sequential([layers.Embedding(max_features + 1, embedding_dim), layers.Dropout(0.2), layers.GlobalAveragePooling1D(), layers.Dropout(0.2), layers.Dense(1)])
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()', method_object=None, function_args=[[layers.Embedding(max_features + 1, embedding_dim), layers.Dropout(0.2), layers.GlobalAveragePooling1D(), layers.Dropout(0.2), layers.Dense(1)]], function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.summary()')
model.summary()
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.summary()', method_object=model, function_args=None, function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.compile()')
model.compile(loss=losses.BinaryCrossentropy(from_logits=True), optimizer='adam', metrics=tf.metrics.BinaryAccuracy(threshold=0.0))
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.compile()', method_object=model, function_args=None, function_kwargs={'loss': losses.BinaryCrossentropy(from_logits=True), 'optimizer': 'adam', 'metrics': tf.metrics.BinaryAccuracy(threshold=0.0)})
epochs = 10
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.fit()')
history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.fit()', method_object=model, function_args=[train_ds], function_kwargs={'validation_data': val_ds, 'epochs': epochs})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.evaluate()')
(loss, accuracy) = model.evaluate(test_ds)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.evaluate()', method_object=model, function_args=[test_ds], function_kwargs=None)
print('Loss: ', loss)
print('Accuracy: ', accuracy)
history_dict = history.history
history_dict.keys()
acc = history_dict['binary_accuracy']
val_acc = history_dict['val_binary_accuracy']
loss = history_dict['loss']
val_loss = history_dict['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.show()
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()')
export_model = tf.keras.Sequential([vectorize_layer, model, layers.Activation('sigmoid')])
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential()', method_object=None, function_args=[[vectorize_layer, model, layers.Activation('sigmoid')]], function_kwargs=None)
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.compile()')
export_model.compile(loss=losses.BinaryCrossentropy(from_logits=False), optimizer='adam', metrics=['accuracy'])
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.compile()', method_object=export_model, function_args=None, function_kwargs={'loss': losses.BinaryCrossentropy(from_logits=False), 'optimizer': 'adam', 'metrics': ['accuracy']})
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.evaluate()')
(loss, accuracy) = export_model.evaluate(raw_test_ds)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.evaluate()', method_object=export_model, function_args=[raw_test_ds], function_kwargs=None)
print(accuracy)
examples = ['The movie was great!', 'The movie was okay.', 'The movie was terrible...']
start_times_INSERTED_INTO_SCRIPT = before_execution_INSERTED_INTO_SCRIPT(experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.predict()')
export_model.predict(examples)
after_execution_INSERTED_INTO_SCRIPT(start_times=start_times_INSERTED_INTO_SCRIPT, experiment_file_path=EXPERIMENT_FILE_PATH, function_to_run='tensorflow.keras.Sequential.predict()', method_object=export_model, function_args=[examples], function_kwargs=None)
