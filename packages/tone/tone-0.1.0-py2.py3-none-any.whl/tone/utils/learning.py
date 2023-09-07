import torch.nn as nn


def ignore_warning(category=None):
    import warnings
    if category is not None:
        warnings.filterwarnings("ignore", category=category)
    else:
        warnings.filterwarnings('ignore')


def set_plot_formats(formats='svg'):
    from matplotlib_inline import backend_inline
    backend_inline.set_matplotlib_formats(formats)


def try_use_device(cuda=True, tensor=True):
    import torch
    if cuda and torch.cuda.is_available():
        device = torch.device("cuda")
        type = torch.cuda.FloatTensor
    else:
        device = torch.device("cpu")
        type = torch.FloatTensor

    if tensor:
        torch.set_default_tensor_type(type)

    torch.set_default_device(device)
    return device


def load_model(model, filename) -> nn.Module:
    import torch
    model.load_state_dict(torch.load(filename))
    model.eval()
    return model


def save_model(model, filename):
    import os
    import torch

    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    torch.save(model.state_dict(), filename)


def save_module(model, filename):
    from .attrdict import attrdict
    import pickle
    import os
    attr = attrdict()
    attr.classname = type(model)
    attr.state_dict = model.state_dict()

    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(filename, 'wb') as file:
        file.write(pickle.dumps(attr))


def load_module(filename) -> nn.Module:
    import pickle
    with open(filename, 'rb') as file:
        attr = pickle.loads(file.read())

    model = attr.classname()
    model.load_state_dict(attr.state_dict)
    model.eval()
    return model


def save_pickle(model, filename):

    import pickle
    import os

    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(filename, 'wb') as file:
        file.write(pickle.dumps(model))


def load_pickle(filename) -> nn.Module:
    import pickle
    with open(filename, 'rb') as file:
        model = pickle.loads(file.read())

    if hasattr(model, 'eval') and callable(model.eval):
        model.eval()

    return model


def metrics(y_true, y_pred):
    from .attrdict import attrdict
    from sklearn import metrics as m
    import math

    scores = attrdict()
    scores.MAPE = m.mean_absolute_percentage_error(y_true, y_pred)
    scores.MSE = m.mean_squared_error(y_true, y_pred)
    scores.RNSE = math.sqrt(scores.MSE)
    scores.MAE = m.mean_absolute_error(y_true, y_pred)
    scores.EVS = m.explained_variance_score(y_true, y_pred)
    scores.R2 = m.r2_score(y_true, y_pred)

    return scores


def naive_fit(model, dataset, criterion, optimizer, epoch, batch_size, device, shuffle, progress=True, step_callback=None):
    import torch
    from tqdm import tqdm

    dataloader = torch.utils.data.DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        drop_last=True,
        generator=torch.Generator(device=device),
        shuffle=shuffle,
    )

    batch = len(dataloader)

    losses = []

    def updater(x, t):
        y = model.forward(x)
        loss = criterion(y, t)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        return loss

    if step_callback is None:
        step_callback = updater

    with tqdm(total=epoch * batch) as bar:
        for e in range(epoch):
            for i, (x, t) in enumerate(dataloader):

                loss = step_callback(x, t)
                losses.append(loss.item())

                if progress:
                    bar.set_description(f"({e + 1:02}/{epoch}) | ({i + 1:02}/{batch})")
                    bar.update()
                    bar.set_postfix(loss=f"{loss.item():0.6}")

    return losses


def naive_test(models, dataset, batch_size, device, progress=True):
    import torch
    from tqdm import tqdm

    dataloader = torch.utils.data.DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        drop_last=True,
        generator=torch.Generator(device=device),
        shuffle=False,
    )

    if progress:
        dataloader = tqdm(dataloader)

    preds = []
    for model in models:
        model.eval()
        preds.append([])

    real = []

    for x, t in dataloader:
        real.append(t)
        for i, model in enumerate(models):
            y = model.forward(x)
            preds[i].append(y)

    real = torch.cat(real)
    for i, pred in enumerate(preds):
        preds[i] = torch.cat(pred)

    return real, preds
