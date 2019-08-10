import tensorflow as tf
tf.enable_eager_execution()

import numpy as np
import os
import time

path_to_file = tf.keras.utils.get_file('shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')

txt = open(path_to_file).read()

vocab = sorted(set(txt))

char2idx = {u:i for i,u in enumerate(vocab)}

idx2char = np.array(vocab)

text_as_int = np.array([char2idx[c] for c in txt])

seq_length = 100

chunks = tf.data.Dataset.from_tensor_slices(text_as_int).batch(seq_length+1,drop_remainder = True)

for item in chunks.take(5):
    print(repr(''.join(idx2char[item.numpy()])))

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text,target_text

dataset = chunks.map(split_input_target)

BATCH_SIZE = 64

BUFFER_SIZE = 10000

dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE,drop_remainder = True)

class Model(tf.keras.Model):
    def __init__(self,vocab_size,embedding_dim,units):
        super(Model,self).__init__()
        self.units = units

        self.embedding = tf.keras.layers.Embedding(vocab_size,embedding_dim)

        if tf.test.is_gpu_available():
            self.gru = tf.keras.layers.CuDNNGRU(self.units,return_sequeces=True,recurrent_initializer='glorot_uniform',stateful=True)
        else:
            self.gru = tf.keras.layers.GRU(self.units,return_sequences=True,recurrent_activation='sigmoid',recurrent_initializer='glorot_uniform',stateful=True)

        self.fc = tf.keras.layers.Dense(vocab_size)

    def call(self,x):
        embedding = self.embedding(x)
        output = self.gru(embedding)
        prediction = self.fc(output)
        return prediction

vocab_size = len(vocab)
embedding_dim = 256
units = 1024
model = Model(vocab_size,embedding_dim,units)

optimizer = tf.train.AdadeltaOptimizer()

def loss_function(real,preds):
    return tf.losses.sparse_softmax_cross_entropy(labels=real,logits=preds)

model.build(tf.TensorShape([BATCH_SIZE,seq_length]))

model.summary()

checkpoint_dir = './training_checkpoints'

checkpoint_prefix = os.path.join(checkpoint_dir,'ckpt')

EPOCHES = 1

for epoch in range(EPOCHES):
    start = time.time()

    hidden = model.reset_states()

    for (batch,(inp,target)) in enumerate(dataset):
        with tf.GradientTape() as tape:
            predictions = model(inp)
            loss = loss_function(target,predictions)

        grads = tape.gradient(loss,model.variables)
        optimizer.apply_gradients(zip(grads,model.variables))

        if batch % 100 == 0:
            print('Epoch {} Batch {} Loss {:.4f}'.format(epoch+1,batch,loss))

    if (epoch+1) % 5 ==0:
        model.save_weights(checkpoint_prefix)

## for generate --build a new model
model = Model(vocab_size, embedding_dim, units)

model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))

model.build(tf.TensorShape([1, None]))

num_generate = 1000

start_string = 'Q'

input_eval = [char2idx[s] for s in start_string]
input_eval = tf.expand_dims(input_eval,0)

text_generated = []

temperature = 1.0

model.reset_states()
for i in range(num_generate):
    predictions = model(input_eval)
    predictions = tf.squeeze(predictions,0)

    predictions = predictions / temperature
    predictions_id = tf.multinomial(predictions,num_samples = 1)[-1,0].numpy()

    input_eval = tf.expand_dims([predictions_id],0)

    text_generated.append(idx2char[predictions_id])

print(start_string + ''.join(text_generated))


