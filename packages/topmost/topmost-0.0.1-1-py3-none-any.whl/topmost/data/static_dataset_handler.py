import torch
from torch.utils.data import DataLoader
import numpy as np
import scipy.sparse
import scipy.io
from . import file_utils


class StaticDatasetHandler:
    def __init__(self, dataset_dir, batch_size=200, device='cpu', as_tensor=False):
        # train_bow: NxV
        # test_bow: Nxv
        # word_emeddings: VxD
        # vocab: V, ordered by word id.

        self.train_bow, self.test_bow, self.train_texts, self.test_texts, self.train_labels, self.test_labels, self.vocab, self.pretrained_WE = self.load_data(dataset_dir)
        self.vocab_size = len(self.vocab)

        print("===>train_size: ", self.train_bow.shape[0])
        print("===>test_size: ", self.test_bow.shape[0])
        print("===>vocab_size: ", self.vocab_size)
        print("===>average length: {:.3f}".format(self.train_bow.sum(1).sum() / self.train_bow.shape[0]))
        print("===>#label: ", len(np.unique(self.train_labels)))

        if as_tensor:
            self.train_bow = torch.from_numpy(self.train_bow).to(device)
            self.test_bow = torch.from_numpy(self.test_bow).to(device)
            self.train_dataloader = DataLoader(self.train_bow, batch_size=batch_size, shuffle=True)
            self.test_dataloader = DataLoader(self.test_bow, batch_size=batch_size, shuffle=False)

    def load_data(self, path):

        train_bow = scipy.sparse.load_npz(f'{path}/train_bow.npz').toarray().astype('float32')
        test_bow = scipy.sparse.load_npz(f'{path}/test_bow.npz').toarray().astype('float32')
        word_embeddings = scipy.sparse.load_npz(f'{path}/word_embeddings.npz').toarray().astype('float32')

        train_texts = file_utils.read_text(f'{path}/train_texts.txt')
        test_texts = file_utils.read_text(f'{path}/test_texts.txt')
        train_labels = np.loadtxt(f'{path}/train_labels.txt', dtype=int)
        test_labels = np.loadtxt(f'{path}/test_labels.txt', dtype=int)

        vocab = file_utils.read_text(f'{path}/vocab.txt')

        return train_bow, test_bow, train_texts, test_texts, train_labels, test_labels, vocab, word_embeddings
