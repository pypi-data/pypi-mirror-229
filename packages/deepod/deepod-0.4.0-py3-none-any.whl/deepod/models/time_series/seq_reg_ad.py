import numpy as np
import time
from tqdm import tqdm
import torch
from torch.utils.data import DataLoader, Dataset
from deepod.utils.utility import get_sub_seqs


class SeqRegAD:
    def __init__(self, seq_len_lst=None, seq_len=100, stride=10,
                 epochs=5, batch_size=64, lr=1e-3,
                 hidden_dims=100, rep_dim=100,
                 verbose=2, random_state=42):

        if seq_len_lst is None:
            self.seq_len_lst = np.arange(10, 100, 10)
        else:
            self.seq_len_lst = seq_len_lst
        self.stride = stride

        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr

        self.rep_dim = rep_dim

        self.verbose = verbose
        self.random_state = random_state

        self.n_features = -1
        self.network = None
        return

    def fit(self, x):
        self.n_features = x.shape[-1]

        seqs_lst = []
        for seq_len in self.seq_len_lst:
            seqs = get_sub_seqs(x, seq_len=seq_len, stride=self.stride)
            seqs_lst.append(seqs)

        train_dataset = SeqDataset(seqs_lst, self.seq_len_lst, seed=self.random_state)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True, drop_last=True)

        self.network = GRUNet(input_dim=self.n_features, class_num=1,
                              hidden_dim=100, layers=1,
                              emb_dim=self.rep_dim)
        print(self.network)

        criterion = torch.nn.MSELoss(reduction='mean')
        optimizer = torch.optim.Adam(self.network.parameters(), lr=self.lr, weight_decay=1e-6)

        self.network.train()
        # training epoch iteration
        for i in range(self.epochs):
            t1 = time.time()
            train_loss_lst = []
            steps = 0

            # batch iteration
            with tqdm(total=len(train_loader), desc=f'epoch {i+1:3d}/{self.epochs}', ncols=150) as pbar:
                for batch_data, batch_label in train_loader:
                    batch_loss = np.zeros(len(self.seq_len_lst))

                    # each mini-batch set contains a list of mini-batch data with different sequence length
                    for idx, (seq_batch_data, seq_batch_label) in enumerate(zip(batch_data, batch_label)):
                        seq_batch_data = seq_batch_data.float()
                        seq_batch_label = seq_batch_label.float()
                        seq_batch_label = seq_batch_label.reshape((seq_batch_label.size(0), -1))

                        pred = self.network(seq_batch_data)

                        loss = criterion(pred, seq_batch_label)

                        self.network.zero_grad()
                        loss.backward()
                        optimizer.step()
                        batch_loss[idx] = loss.item()

                        steps += 1

                    train_loss_lst.append(batch_loss)

                    loss_str = f'{np.mean(batch_loss):.6f}' + ' <<< ' +\
                               ', '.join([f'{a:.3f}' for a in batch_loss])
                    pbar.set_postfix(loss=f'{loss_str}')
                    pbar.update(1)

            train_loss_lst = np.array(train_loss_lst)
            train_loss_avg = np.average(train_loss_lst, axis=0)
            epoch_loss_str = f'{np.mean(train_loss_avg):.6f}' + ' <<< ' +\
                             ', '.join([f'{a:.3f}' for a in train_loss_avg])

            t = time.time() - t1
            print(f'epoch {i+1:3d}/{self.epochs}: '
                  f'loss={epoch_loss_str} | '
                  f'time={t: .1f}s | '
                  f'steps={steps}')
        return

    def decision_function(self, x):

        seqs_lst = []
        for seq_len in self.seq_len_lst:
            seqs = get_sub_seqs(x, seq_len=seq_len, stride=1)
            seqs_lst.append(seqs)

        # set a new criterion function with reduction=none
        criterion = torch.nn.MSELoss(reduction='none')

        # testing each sequence length
        ensemble_score_lst = []
        for seq_len_idx, seqs in enumerate(seqs_lst):

            # split sub-seqs with one length into mini-batches
            test_loader = DataLoader(seqs, batch_size=self.batch_size, shuffle=False, drop_last=False)

            self.network.eval()
            with torch.no_grad():

                # get loss of each mini-batch and concatenate losses as a vector,
                # and use it as anomaly scores
                score_lst = []
                with tqdm(total=len(test_loader),
                          desc=f'testing len={self.seq_len_lst[seq_len_idx]}, '
                               f'{seq_len_idx+1} / {len(self.seq_len_lst)} :',
                          ncols=150) as pbar:
                    for batch_data in test_loader:
                        batch_data = batch_data.float()
                        batch_label = torch.tensor([self.seq_len_lst[seq_len_idx]] * batch_data.size(0)).float()
                        batch_label = batch_label.reshape([batch_label.shape[0], -1])
                        pred = self.network(batch_data)
                        loss = criterion(pred, batch_label)
                        loss = loss.flatten()
                        score_lst.append(loss.data.cpu())

                        pbar.update(1)

            score_lst = np.concatenate(score_lst)

            # ensemble, fusion
            # normalize scores (use min-max here, other possibilities: ranking, z-score? )
            _max_, _min_ = np.max(score_lst), np.min(score_lst)
            score_lst = (score_lst - _min_) / (_max_ - _min_)
            ensemble_score_lst.append(score_lst)

        # the shape of score_list is (full_length_of_testing_data - seq_len +1),
        # thus, we align the shape of each score_lst by dropping the score of the begging timestamps
        min_size = np.min([score_lst.shape[0] for score_lst in ensemble_score_lst])
        ensemble_score_lst = [score_lst[-min_size:] for score_lst in ensemble_score_lst]
        ensemble_score_lst = np.array(ensemble_score_lst)

        scores = np.average(ensemble_score_lst, axis=0)

        # padding
        padding = np.zeros(np.max(self.seq_len_lst) - 1)
        assert padding.shape[0] + scores.shape[0] == x.shape[0]
        scores = np.hstack((padding, scores))

        return scores


class SeqDataset(Dataset):
    def __init__(self, seqs_lst, seq_len_lst, seed=42):
        rng = np.random.RandomState(seed=seed)
        self.size = np.min([seqs.shape[0] for seqs in seqs_lst])
        self.seqs_data = [seqs[rng.choice(seqs.shape[0], self.size, replace=False)]
                          for seqs in seqs_lst]
        self.seqs_label = [[seq] * self.size for seq in seq_len_lst]
        return

    def __getitem__(self, index):
        data = [a[index] for a in self.seqs_data]
        label = [a[index] for a in self.seqs_label]
        return data, label

    def __len__(self):
        return self.size


# network class
class GRUNet(torch.nn.Module):
    # input_dim：输入数据的特征维度。
    # class_num：分类任务中的类别数量，默认为 10。
    # hidden_dim：GRU 网络的隐藏层维度，默认为 20。
    # emb_dim：输出的嵌入层维度，默认为 20。
    # layers：GRU 网络的层数，默认为 1。
    def __init__(self, input_dim, class_num=10, hidden_dim=20, emb_dim=20, layers=1):
        super(GRUNet, self).__init__()
        self.gru = torch.nn.GRU(input_dim, hidden_size=hidden_dim, batch_first=True, num_layers=layers)
        self.hidden2output = torch.nn.Linear(hidden_dim, emb_dim)
        self.cls_head = torch.nn.Linear(emb_dim, class_num)

    def forward(self, x):
        _, hn = self.gru(x)
        emb = hn[0, :]
        emb = self.hidden2output(emb)
        logit = self.cls_head(emb)
        return logit


class LSTMNet(torch.nn.Module):
    def __init__(self, input_dim, class_num=10, hidden_dim=100, emb_dim=64, layers=3):
        super(LSTMNet, self).__init__()
        self.lstm = torch.nn.LSTM(input_dim, hidden_size=hidden_dim, batch_first=True,
                                  num_layers=layers)
        self.hidden2output = torch.nn.Linear(hidden_dim, emb_dim)
        self.cls_head = torch.nn.Linear(emb_dim, class_num)

    def forward(self, x):
        output, (hn, c) = self.lstm(x)
        emb = hn[0, :]
        emb = self.hidden2output(emb)
        logit = self.cls_head(emb)
        return logit


if __name__ == '__main__':
    import pandas as pd
    import utils

    data_path = '/home/xuhz/dataset/5-TSdata/_processed_data/ASD/omi-10/'
    dataset_name = 'omi-10'

    train_df = pd.read_csv(f'{data_path}/{dataset_name}_train.csv', sep=',', index_col=0)
    test_df = pd.read_csv(f'{data_path}/{dataset_name}_test.csv', sep=',', index_col=0)
    labels = test_df['label'].values
    train_df, test_df = train_df.drop('label', axis=1), test_df.drop('label', axis=1)

    # train_df, test_df = utils.data_standardize(train_df, test_df)
    # train_x = train_df.values
    # test_x = test_df.values

    # 我这里的data_standardize返回的ndarray，如果是dataframe的话.values一下，fit输入的是ndarray
    train_x, test_x = utils.data_standardize(train_df, test_df)

    detector = SeqRegAD(epochs=10, seq_len_lst=[10, 30, 50])
    detector.fit(train_x)

    s = detector.decision_function(test_x)

    eval_metrics = utils.get_metrics(labels, s)
    adj_eval_metrics = utils.get_metrics(labels, utils.adjust_scores(labels, s))

    txt = f'{dataset_name}, '
    txt += ', '.join(['%.4f' % a for a in eval_metrics]) + \
           ', pa, ' + \
           ', '.join(['%.4f' % a for a in adj_eval_metrics])
    print(txt)
